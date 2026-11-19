"""Reduction of a SysML architecture onto the FMI interface it must expose.

Every generator in this package reads the architecture through this module, so
that the modelDescription, the C headers, and the Modelica connectors cannot
disagree about *which* variables exist. The reduction follows the
``pyssp_sysml2`` v0.3.0 FMI policy:

- parameters come from the parameter dialect only (``in port parameters ...``),
  never from flat part attributes, and keep their interface defaults;
- a parameter list is expanded into one scalar per element, named
  ``<name>[<index>]``; the index base is configurable through ``base_index``
  (0 by default, 1 targets OMC-built Modelica FMUs, which declare arrays
  one-based);
- a port whose only member is a non-array ``value`` is named after the port
  alone (``y``), matching the SSP connector; every other port field is named
  ``<port>.<field>`` and expanded the same way;
- value references restart at 0 for every component, parameters first, then
  ports in declaration order and fields in declaration order.

FMI 2.0 has no array variable and no bidirectional scalar, so an ``inout`` or
undirected port becomes an input and the Modelica connector keeps the
direction out of the signal declaration.
"""

from __future__ import annotations

from dataclasses import dataclass
from os import PathLike

from pycps_sysml2 import (
    Architecture,
    Attribute,
    PartDefinition,
    PortDefinition,
    load,
)
from pycps_sysml2.core import map_fmi_type
from pycps_sysml2.metadata.helpers import short_name
from pycps_sysml2.metadata.roles import FMU_MODEL_MARKER, is_fmu_model
from pycps_sysml2.parameters import (
    SSP_POLICY,
    AttributeKind,
    classify_attribute,
    component_definitions,
    is_parameter_interface,
    parameter_declarations,
    parameter_items,
    validate_parameter_dialect,
)

from pyfmi_sysml2.core.model import Component, Field, PortGroup, Variable
from pyfmi_sysml2.core.spelling import DISCRETE_TYPES, INPUT_START

#: Attribute kinds that are typed containers, never FMI signal fields.
_CONTAINER_KINDS = frozenset(
    {
        AttributeKind.FMU_METADATA,
        AttributeKind.SSP_METADATA,
        AttributeKind.PARAMETER_SET,
        AttributeKind.EXPERIMENT,
    }
)


def architecture(source: Architecture | str | PathLike[str]) -> Architecture:
    """An already loaded architecture, or the one at ``source``."""
    if isinstance(source, Architecture):
        return source
    return load(source)


def direction_causality(direction: str | None) -> str:
    """FMI causality for a SysML port direction.

    FMI 2.0 CoSimulation has no bidirectional scalar variable, so ``inout`` and
    an undirected port are exposed as inputs.
    """
    return "output" if direction == "out" else "input"


def _fixed_count(multiplicity: str | None, value: object) -> int | None:
    """Declared element count for a field, or ``None`` for a scalar."""
    if multiplicity:
        text = multiplicity
        if ".." in text:
            lower, upper = text.split("..", 1)
            if lower != upper:
                raise ValueError(
                    f"Variable multiplicity '[{text}]' is not a fixed length; "
                    "FMI 2.0 needs one scalar per element"
                )
            text = lower
        try:
            return int(text)
        except ValueError:
            raise ValueError(
                f"Unsupported multiplicity '[{multiplicity}]'"
            ) from None
    if isinstance(value, tuple):
        return len(value)
    return None


def _field_dtype(attribute: Attribute) -> str:
    return map_fmi_type(attribute.primitive_type_str())


def _is_signal_port(architecture: Architecture, part_def: PartDefinition) -> bool:
    """True for a port that carries FMI signal fields, not parameters."""
    if part_def is None:
        return False
    return not is_parameter_interface(part_def)


def _is_scalar_port(definition: PortDefinition) -> bool:
    """True for a port that names one FMI variable rather than a group.

    Same predicate as ``pyssp_sysml2``: the loader normalizes a connector
    without a dot to a port with one member named ``value``, and the SSP
    exporter names that connector after the port. An array-valued ``value`` is
    deliberately not scalar: FMI expands it into ``<port>.value[<index>]``
    scalars, which one bare connector cannot carry (the SSP exporter refuses
    that shape instead of flattening it).
    """
    if tuple(definition.attributes) != ("value",):
        return False
    attribute = definition.attributes["value"]
    return _fixed_count(attribute.multiplicity, attribute.value) is None


def component_interface(
    architecture: Architecture,
    part_def: PartDefinition,
    *,
    base_index: int = 0,
) -> Component:
    """Build the FMI interface of one leaf part definition.

    ``base_index`` shifts the ``[i]`` suffixes of every array member; the
    default 0 keeps the FMI convention, 1 targets OMC-built Modelica FMUs.
    """
    parameters: list[Field] = []
    variables: list[Variable] = []
    counter = 0

    for attribute in parameter_declarations(architecture, part_def):
        type_name = _field_dtype(attribute)
        items = parameter_items(attribute, base_index=base_index)
        count = len(items)
        array = count if count > 1 or attribute.multiplicity else None
        parameters.append(Field(attribute.name, type_name, array, base_index))
        for position, item in enumerate(items):
            counter += 1
            # The FMI name is offset by base_index; the C member is not.
            member = (
                item.name
                if array is None
                else f"{attribute.name}[{position}]"
            )
            variables.append(
                Variable(
                    name=item.name,
                    type_name=type_name,
                    causality="parameter",
                    variability="fixed",
                    value_reference=counter - 1,
                    index=counter,
                    description=attribute.doc,
                    start=item.value,
                    member=member,
                )
            )

    ports: list[PortGroup] = []
    for name, usage in part_def.ports.items():
        definition = architecture.resolve_port(usage)
        if definition is None:
            raise ValueError(
                f"Unresolved port definition for {part_def.name}.{name}"
            )
        if not _is_signal_port(architecture, definition):
            continue
        scalar = _is_scalar_port(definition)
        member_directions: list[str | None] = []
        fields: list[Field] = []
        for attribute in definition.attributes.values():
            if (
                classify_attribute(architecture, attribute, policy=SSP_POLICY)
                in _CONTAINER_KINDS
            ):
                continue
            member_direction = usage.effective_member_direction(attribute)
            member_directions.append(member_direction)
            causality = direction_causality(member_direction)
            type_name = _field_dtype(attribute)
            array = _fixed_count(attribute.multiplicity, attribute.value)
            fields.append(Field(attribute.name, type_name, array, base_index))
            for suffix, member in fields[-1].members():
                counter += 1
                variables.append(
                    Variable(
                        name=(
                            name
                            if scalar
                            else f"{name}.{attribute.name}{suffix}"
                        ),
                        type_name=type_name,
                        causality=causality,
                        variability=(
                            "discrete" if type_name in DISCRETE_TYPES else None
                        ),
                        value_reference=counter - 1,
                        index=counter,
                        description=(
                            attribute.doc or usage.doc or definition.doc
                        ),
                        start=(
                            INPUT_START[type_name]
                            if causality == "input"
                            else None
                        ),
                        member=f"{name}.{member}",
                    )
                )
        if member_directions and all(
            direction == member_directions[0] for direction in member_directions
        ):
            port_direction = member_directions[0]
        else:
            port_direction = usage.direction if not member_directions else None
        ports.append(
            PortGroup(
                name=name,
                definition=definition.name,
                direction=port_direction,
                causality=direction_causality(port_direction),
                fields=tuple(fields),
                doc=usage.doc or definition.doc,
            )
        )

    return Component(
        name=part_def.name,
        doc=part_def.doc,
        parameters=tuple(parameters),
        ports=tuple(ports),
        variables=tuple(variables),
    )


@dataclass(frozen=True)
class ExportIdentity:
    """How the export unit names the components it exports.

    A container root exports leaf components as ``<system>.<component>``. A
    part definition that is itself the FMU model (``:> FmuModel``) exports
    itself under its bare name, so the FMI identity of a direct FMU is the
    definition name rather than ``<name>.<name>``.
    """

    system: str
    direct: bool

    def model_name(self, component: str) -> str:
        """FMI ``modelName`` of one exported component."""
        return component if self.direct else f"{self.system}.{component}"

    def guid_key(self, component: str) -> str:
        """Frozen uuid5 name of one exported component's guid."""
        scope = "pyssp_sysml2" if self.direct else f"pyssp_sysml2/{self.system}"
        return f"{scope}/{component}"


def export_identity(
    architecture: Architecture, system: PartDefinition
) -> ExportIdentity:
    """The naming rule for the export unit ``resolve_system`` selected."""
    return ExportIdentity(system.name, is_fmu_model(architecture, system))


def resolve_system(
    architecture: Architecture, composition: str | None = None
) -> PartDefinition:
    """The part definition whose components are exported.

    ``composition`` names it explicitly. Without a name, a part definition
    marked ``:> FmuModel`` is the export unit itself, and several such
    candidates must name one. When none is marked, the single part definition
    that has parts and is not used as a part elsewhere is taken; an
    architecture with several such roots must name one.
    """
    if composition is not None:
        return architecture.get_part_def(composition)

    fmu_models = [
        definition
        for definition in architecture.part_definitions.values()
        if is_fmu_model(architecture, definition)
        and short_name(definition.name) != FMU_MODEL_MARKER
    ]
    if fmu_models:
        if len(fmu_models) == 1:
            return fmu_models[0]
        names = ", ".join(sorted(definition.name for definition in fmu_models))
        raise ValueError(
            "Cannot pick a composition root; "
            f"{len(fmu_models)} {FMU_MODEL_MARKER} candidates ({names}). "
            "Pass composition=."
        )

    used: set[str] = set()
    for definition in architecture.part_definitions.values():
        for usage in definition.parts.values():
            resolved = architecture.resolve_part(usage)
            if resolved is not None:
                used.add(architecture.stored_key(resolved))
    roots = [
        definition
        for definition in architecture.part_definitions.values()
        if definition.parts
        and architecture.stored_key(definition) not in used
    ]
    if len(roots) != 1:
        names = ", ".join(sorted(definition.name for definition in roots))
        raise ValueError(
            "Cannot pick a composition root; "
            f"{len(roots)} candidates ({names or 'none'}). Pass composition=."
        )
    return roots[0]


def components(
    architecture: Architecture,
    *,
    composition: str | None = None,
    base_index: int = 0,
) -> list[Component]:
    """Every exported component, sorted by name.

    A composition that is itself the FMU model exports that definition as its
    single component; a container root exports its leaf descendants. The
    parameter dialect is validated first, so a flat parameter attribute is
    reported instead of silently dropped. ``base_index`` is forwarded to each
    component's interface.
    """
    system = resolve_system(architecture, composition)
    validate_parameter_dialect(architecture, system, policy=SSP_POLICY)
    if export_identity(architecture, system).direct:
        definitions = [system]
    else:
        definitions = [
            definition
            for definition in sorted(
                component_definitions(architecture, system),
                key=lambda candidate: candidate.name,
            )
            if not definition.parts
        ]
    return [
        component_interface(architecture, definition, base_index=base_index)
        for definition in definitions
    ]


def component(
    architecture: Architecture,
    name: str,
    *,
    composition: str | None = None,
    base_index: int = 0,
) -> Component:
    """One named exported component."""
    for candidate in components(
        architecture, composition=composition, base_index=base_index
    ):
        if candidate.name == name:
            return candidate
    raise KeyError(f"No exported component named {name!r}")
