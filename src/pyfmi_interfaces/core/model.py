"""The reduced FMI interface model every artifact generator reads.

A :class:`Component` carries the fields, the port groups and the scalar
variables of one exported part definition; the generators map these objects
onto their own output format and never re-derive the variable set.

A :class:`Reduction` is the complete, caller-built input of every generator:
the exported components, the export identity, the package name, and the export
unit's experiment.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    """One declared member: a scalar, or a fixed-length array.

    ``base_index`` shifts the emitted ``[i]`` suffixes; the default 0 keeps the
    FMI 0-based convention, 1 targets OMC-built Modelica FMUs.
    """

    name: str
    type_name: str
    array: int | None = None
    base_index: int = 0

    def members(self) -> list[tuple[str, str]]:
        """``(fmi_suffix, member_expression)`` for every element.

        The suffix is the FMI-facing index, offset by ``base_index``; the C
        member is always zero-based, because the array the header declares has
        exactly ``array`` elements whatever the FMI names say.
        """
        if self.array is None:
            return [("", self.name)]
        start = self.base_index
        return [
            (f"[{i}]", f"{self.name}[{i - start}]")
            for i in range(start, start + self.array)
        ]


@dataclass(frozen=True)
class Variable:
    """One FMI ScalarVariable, with its C member expression.

    ``start`` is the authored typed value (the neutral ``INPUT_START`` value
    for an input); ``start_text`` is that value already formatted for FMI, so no
    generator formats a value.
    """

    name: str
    type_name: str
    causality: str
    variability: str | None
    value_reference: int
    index: int
    description: str | None
    member: str
    start: object | None = None
    start_text: str | None = None

    @property
    def writable(self) -> bool:
        """Whether the C mapping may write through this value reference."""
        return self.causality != "output"

    @property
    def c_name(self) -> str:
        """Name stem of the generated value-reference enumerator.

        A port variable follows its C member path: a flattened scalar port
        keeps ``<port>.value`` even though its FMI name is the bare port, and
        an array port keeps its ``base_index`` suffix because its FMI name
        already carries it. A parameter uses its FMI name, because the C array
        stays zero-based while ``base_index`` may lift the FMI suffix.
        """
        if self.causality == "parameter" or "." in self.name:
            return self.name
        return self.member


@dataclass(frozen=True)
class PortGroup:
    """A port usage: its payload fields, attributes, and their FMI variables."""

    name: str
    definition: str
    direction: str | None
    causality: str
    fields: tuple[Field, ...]
    doc: str | None
    attributes: tuple[tuple[str, object], ...] = ()

    @property
    def modelica_qualifier(self) -> str:
        """Modelica declaration prefix for the connector field."""
        if self.direction == "in":
            return "input "
        if self.direction == "out":
            return "output "
        return ""


@dataclass(frozen=True)
class Component:
    """A leaf part definition and its complete FMI interface.

    ``attributes`` keeps the authored part-definition attributes as
    ``(name, value)`` pairs in declaration order.
    """

    name: str
    doc: str | None
    parameters: tuple[Field, ...]
    ports: tuple[PortGroup, ...]
    variables: tuple[Variable, ...]
    attributes: tuple[tuple[str, object], ...] = ()

    @property
    def outputs(self) -> tuple[Variable, ...]:
        return tuple(v for v in self.variables if v.causality == "output")

    @property
    def vr_count(self) -> int:
        return len(self.variables)


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
        # Frozen for byte-identical GUIDs from earlier releases; never rename
        # the namespace.
        scope = "pyssp_sysml2" if self.direct else f"pyssp_sysml2/{self.system}"
        return f"{scope}/{component}"


@dataclass(frozen=True)
class Experiment:
    """The export unit's ``DefaultExperiment``, in FMI 2.0 terms.

    All four are optional doubles, exactly as FMI 2.0.5 defines them; an absent
    field is omitted from the document.
    """

    start_time: float | None = None
    stop_time: float | None = None
    tolerance: float | None = None
    step_size: float | None = None


@dataclass(frozen=True)
class Reduction:
    """One export unit reduced to the input every artifact generator needs.

    ``components`` carries the complete variable set, ``identity`` the naming
    rule, ``package`` the default header/type prefix, ``root`` the optional root
    name, ``attributes`` the root part definition's authored attributes, and
    ``experiment`` the export unit's optional default experiment. A caller that
    already holds a ``Reduction`` can run any generator from that object alone.
    """

    components: tuple[Component, ...]
    identity: ExportIdentity
    package: str
    experiment: Experiment | None = None
    root: str | None = None
    attributes: tuple[tuple[str, object], ...] = ()


def select_component(reduction: Reduction, name: str) -> Component:
    """Return the exported component named ``name``.

    This is the one component-selection rule: a component is addressed by its
    exported name, and an unknown name is a ``ValueError`` rather than a silent
    miss. Generators call it instead of walking ``Reduction.components``
    themselves.
    """
    for candidate in reduction.components:
        if candidate.name == name:
            return candidate
    raise ValueError(f"No exported component named {name!r}")
