"""Modelica interface packages generated from a SysML architecture.

The connector set is the sysml-side mirror of the FMI interface: one ``connector``
per distinct port definition used by the exported components, with the same
fields in the same order the FMI reduction uses. The names are configuration,
not constants: the root package, the enclosing ``within`` clause, and the
subpackage layout are arguments, and nothing domain-specific is emitted.

Per exported component the package carries two more files: ``<Name>_Interface``,
a ``partial model`` holding the parameters and one connector instance per port,
and ``<Name>``, a model the generator creates once and never rewrites. The
partial model is the generated plumbing; the model is the implementer's logic,
the Modelica counterpart of the C++ model file. A ``partial model`` is exempt
from balance checking, so the generated half always checks clean while the
implementer's half fails to build until it has equations.

A connector is a type, so a definition used by components in different
directions cannot declare a direction that is true everywhere. The member prefix
is the port direction when every usage agrees on it, and empty when the usages
disagree or any of them is ``inout`` or undirected; a bidirectional connector
has to stay undirected for the Modelica tool to accept it on both sides.

The subpackages are declared inside their parent, so their ``within`` clause is
the root package, nested under ``within`` when one is given; only the root
``package.mo`` carries the bare ``within`` clause.
"""

from __future__ import annotations

from pathlib import Path

from pycps_sysml2 import Architecture

from pyfmi_sysml2.core import (
    Component,
    Field,
    architecture,
    components,
    modelica_type,
)

#: Root package default. The generated files never embed a concrete model name.
DEFAULT_PACKAGE = "GeneratedInterfaces"

#: The primitive connector aliases every generated package carries.
PRIMITIVES = ("Real", "Integer", "Boolean", "String")

#: Subpackage names, also the ``package.order`` entries.
INTERFACES = "Interfaces"
GENERATED = "GeneratedInterfaces"

#: Suffix of the generated ``partial model`` for one exported component.
INTERFACE_SUFFIX = "_Interface"

INDENT = "  "

#: Modelica reserved words; a port named after one is spelled with a trailing
#: underscore, the same rule the C header uses for C keywords.
RESERVED = frozenset(
    """
    algorithm and annotation block break class connect connector constant
    constrainedby der discrete each else elseif end enumerated equation
    expandable extends external false final flow for function if import impure
    in initial inner input loop model not operator or outer output package
    parameter partial protected public pure record redeclare replaceable return
    stream then true try type when while within
    """.split()
)


def _instance_name(name: str) -> str:
    """A Modelica identifier for a connector instance, keyword-escaped."""
    return f"{name}_" if name in RESERVED else name


def _interface_model_name(component: Component) -> str:
    """Class name of the generated ``partial model`` for one component."""
    return f"{component.name}{INTERFACE_SUFFIX}"


def _port_definitions(
    exported: list[Component],
) -> dict[str, tuple[tuple[str, str], ...]]:
    """Field sets and member prefix per distinct port definition.

    Keyed by the definition name, sorted. Two usages of one definition must
    agree on the fields; a definition that is used in one direction only keeps
    that direction, anything else stays undirected.
    """
    fields_by_definition: dict[str, tuple[Field, ...]] = {}
    qualifiers: dict[str, set[str]] = {}
    for component in exported:
        for port in component.ports:
            known = fields_by_definition.get(port.definition)
            assert known is None or known == port.fields, (
                f"port definition {port.definition} disagrees between usages: "
                f"{known} != {port.fields}"
            )
            fields_by_definition[port.definition] = port.fields
            qualifiers.setdefault(port.definition, set()).add(
                port.modelica_qualifier
            )

    result: dict[str, tuple[tuple[str, str], ...]] = {}
    for definition in sorted(fields_by_definition):
        prefixes = qualifiers[definition]
        qualifier = next(iter(prefixes)) if len(prefixes) == 1 else ""
        result[definition] = tuple(
            (qualifier, _field_text(field))
            for field in fields_by_definition[definition]
        )
    return result


def _field_text(field: Field) -> str:
    """One connector member without its indent and terminator."""
    type_name = modelica_type(field.type_name)
    if field.array is None:
        return f"{type_name} {field.name}"
    return f"{type_name} {field.name}[{field.array}]"


def _modelica_literal(type_name: str, text: str) -> str:
    """Modelica spelling of one FMI start value."""
    if type_name == "String":
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if type_name == "Boolean":
        return "true" if text.strip().lower() in ("true", "1") else "false"
    return text


def _parameter_declarations(component: Component) -> list[str]:
    """``parameter`` lines carrying the value each parameter was authored with.

    A parameter whose elements have no authored value stays unbound rather than
    guessing one, so the tool refuses to simulate until someone supplies it.
    """
    starts = {
        variable.name: variable.start_text
        for variable in component.variables
        if variable.causality == "parameter"
    }
    lines: list[str] = []
    for field in component.parameters:
        values = [starts.get(member) for _, member in field.members()]
        declaration = f"{INDENT}parameter {_field_text(field)}"
        if all(value is not None for value in values):
            if field.array is None:
                literal = _modelica_literal(field.type_name, values[0])
                declaration += f" = {literal}"
            else:
                rendered = ", ".join(
                    _modelica_literal(field.type_name, value) for value in values
                )
                declaration += f" = {{{rendered}}}"
        lines.append(f"{declaration};")
    return lines


def _interface_text(parent: str, component: Component) -> str:
    """The generated ``partial model`` holding one component's plumbing."""
    name = _interface_model_name(component)
    lines = [f"within {parent};", "", f"partial model {name}"]
    lines.extend(_parameter_declarations(component))
    for port in component.ports:
        lines.append(
            f"{INDENT}{GENERATED}.{port.definition} "
            f"{_instance_name(port.name)};"
        )
    lines.append(f"end {name};")
    return "\n".join(lines) + "\n"


def _model_text(parent: str, component: Component) -> str:
    """Initial text of ``<Name>.mo``, written only when absent."""
    return "\n".join(
        [
            f"within {parent};",
            "",
            f"model {component.name}",
            f"{INDENT}extends {_interface_model_name(component)};",
            "equation",
            f"{INDENT}// TODO: implement the equations of {component.name}.",
            f"end {component.name};",
            "",
        ]
    )


def _package_text(package: str, within: str | None) -> str:
    header = f"within {within};" if within is not None else "within ;"
    return "\n".join(
        [
            header,
            f"package {package}",
            f'{INDENT}annotation(uses(Modelica(version="4.0.0")));',
            f"end {package};",
            "",
        ]
    )


def _order_text(exported: list[Component]) -> str:
    lines = [INTERFACES, GENERATED]
    for component in exported:
        lines.append(_interface_model_name(component))
        lines.append(component.name)
    return "\n".join(lines) + "\n"


def _parent_scope(package: str, within: str | None) -> str:
    """Fully qualified name of the root package, as a subpackage sees it."""
    return package if within is None else f"{within}.{package}"


def _interfaces_text(parent: str) -> str:
    lines = [f"within {parent};", f"package {INTERFACES}"]
    for type_name in PRIMITIVES:
        lines.append(
            f"{INDENT}connector {type_name}Input = input {type_name};"
        )
        lines.append(
            f"{INDENT}connector {type_name}Output = output {type_name};"
        )
    lines.append(f"end {INTERFACES};")
    return "\n".join(lines) + "\n"


def _generated_text(
    parent: str, definitions: dict[str, tuple[tuple[str, str], ...]]
) -> str:
    lines = [f"within {parent};", f"package {GENERATED}"]
    for name in sorted(definitions):
        lines.append(f"{INDENT}connector {name}")
        for qualifier, member in definitions[name]:
            lines.append(f"{INDENT * 2}{qualifier}{member};")
        lines.append(f"{INDENT}end {name};")
        lines.append("")
    lines.append(f"end {GENERATED};")
    return "\n".join(lines) + "\n"


def generate_modelica(
    source: Architecture | str | Path,
    output_dir: str | Path,
    *,
    package: str = DEFAULT_PACKAGE,
    within: str | None = None,
    composition: str | None = None,
) -> list[Path]:
    """Write the Modelica interface package and return every file it wrote.

    ``output_dir/<package>/`` holds ``package.mo``, ``package.order``,
    ``Interfaces.mo`` (the four primitive input/output aliases),
    ``GeneratedInterfaces.mo`` (one connector per port definition), and per
    exported component ``<Name>_Interface.mo`` (parameters and connector
    instances) plus ``<Name>.mo`` (created once, never rewritten). The
    subpackages are declared inside the root package, so ``within`` nests them.
    """
    parsed = architecture(source)
    exported = components(parsed, composition=composition)
    definitions = _port_definitions(exported)

    root = Path(output_dir) / package
    parent = _parent_scope(package, within)
    files = {
        root / "package.mo": _package_text(package, within),
        root / "package.order": _order_text(exported),
        root / f"{INTERFACES}.mo": _interfaces_text(parent),
        root / f"{GENERATED}.mo": _generated_text(parent, definitions),
    }
    for component in exported:
        name = _interface_model_name(component)
        files[root / f"{name}.mo"] = _interface_text(parent, component)

    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    written = list(files)
    for component in exported:
        model = root / f"{component.name}.mo"
        if not model.exists():
            model.write_text(_model_text(parent, component), encoding="utf-8")
            written.append(model)
    return sorted(written)
