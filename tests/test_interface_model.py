"""Unit tests for the interface model helpers."""

from __future__ import annotations

import pytest

from pyfmi_interfaces import select_component
from pyfmi_interfaces.core import Component, ExportIdentity, Reduction

pytestmark = pytest.mark.unit


def _component(name: str) -> Component:
    return Component(name=name, doc=None, parameters=(), ports=(), variables=())


def _multi_component_reduction() -> Reduction:
    return Reduction(
        components=(
            _component("Alpha"),
            _component("Bravo"),
            _component("Charlie"),
        ),
        identity=ExportIdentity("Root", False),
        package="Demo",
    )


def test_select_component_chooses_the_named_candidate() -> None:
    reduction = _multi_component_reduction()

    selected = select_component(reduction, "Bravo")

    assert selected is reduction.components[1]
    assert selected.name == "Bravo"


def test_select_component_rejects_an_unknown_name() -> None:
    with pytest.raises(ValueError, match="No exported component named 'Delta'"):
        select_component(_multi_component_reduction(), "Delta")


def test_export_identity_guid_namespace_is_frozen() -> None:
    assert (
        ExportIdentity("Root", False).guid_key("Scale")
        == "pyssp_sysml2/Root/Scale"
    )
    assert ExportIdentity("Scale", True).guid_key("Scale") == "pyssp_sysml2/Scale"
