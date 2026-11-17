"""The reduced FMI interface model every artifact generator reads.

A :class:`Component` carries the fields, the port groups and the scalar
variables of one exported part definition; the generators map these objects
onto their own output format and never re-derive the variable set.
"""

from __future__ import annotations

from dataclasses import dataclass

from pycps_sysml2.core import format_value


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
    """One FMI ScalarVariable, with its C member expression."""

    name: str
    type_name: str
    causality: str
    variability: str | None
    value_reference: int
    index: int
    description: str | None
    start: object | None
    member: str

    @property
    def start_text(self) -> str | None:
        """XML text for ``start``, or ``None`` when no default was authored."""
        if self.start is None:
            return None
        return format_value(self.type_name, self.start)

    @property
    def writable(self) -> bool:
        """Whether the C mapping may write through this value reference."""
        return self.causality != "output"


@dataclass(frozen=True)
class PortGroup:
    """A port usage: its payload fields and their FMI variables."""

    name: str
    definition: str
    direction: str | None
    causality: str
    fields: tuple[Field, ...]
    doc: str | None

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
    """A leaf part definition and its complete FMI interface."""

    name: str
    doc: str | None
    parameters: tuple[Field, ...]
    ports: tuple[PortGroup, ...]
    variables: tuple[Variable, ...]

    @property
    def outputs(self) -> tuple[Variable, ...]:
        return tuple(v for v in self.variables if v.causality == "output")

    @property
    def vr_count(self) -> int:
        return len(self.variables)
