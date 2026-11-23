"""Unit tests for the interface model helpers."""

from __future__ import annotations

import pytest

from pyfmi_interfaces import select_component
from pyfmi_interfaces.core import Component, ExportIdentity, Reduction
from pyfmi_interfaces.core.identity import component_guid, resolve_guid

pytestmark = pytest.mark.unit

BARE_GUID = "01234567-89ab-cdef-0123-456789abcdef"
BRACED_GUID = "{01234567-89ab-cdef-0123-456789abcdef}"


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


@pytest.mark.parametrize("value", [BARE_GUID, BRACED_GUID])
def test_resolve_guid_prefers_an_override_verbatim(value: str) -> None:
    identity = ExportIdentity("Root", False, value)

    assert resolve_guid(identity, "Scale") == value


def test_resolve_guid_derives_when_there_is_no_override() -> None:
    assert resolve_guid(ExportIdentity("Root", False), "Scale") == (
        "{1cd5dff9-41fe-5fdf-abd6-fe39bc507661}"
    )


def test_component_guid_override_wins_verbatim() -> None:
    assert component_guid("Root", "Scale", guid=BARE_GUID) == BARE_GUID


@pytest.mark.parametrize("value", ["", "   "])
def test_guid_override_rejects_blank_values(value: str) -> None:
    with pytest.raises(ValueError, match="Scale"):
        resolve_guid(ExportIdentity("Root", False, value), "Scale")
    with pytest.raises(ValueError, match="Scale"):
        component_guid("Root", "Scale", guid=value)
