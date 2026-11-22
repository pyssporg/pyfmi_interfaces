"""Contract: every emitter runs from a hand-built ``Reduction`` alone.

These are the reduction-driven tests that stayed in ``pyfmi_interfaces``. They
construct the parser-free model directly, so a generator cannot depend on a
SysML source, a composition name, or a parser import to produce its artifact.
"""

from __future__ import annotations

import builtins
from datetime import datetime, timezone
from pathlib import Path

import pytest

import pyfmi_interfaces
from pyfmi_interfaces import (
    generate_c_headers,
    generate_c_runtime,
    generate_model_description,
    generate_modelica,
)
from pyfmi_interfaces.core.model import (
    Component,
    Experiment,
    ExportIdentity,
    Field,
    PortGroup,
    Reduction,
    Variable,
)

pytestmark = pytest.mark.contract

GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _reduction() -> Reduction:
    component = Component(
        name="Scale",
        doc=None,
        parameters=(Field("gain", "Real"),),
        ports=(
            PortGroup(
                name="u",
                definition="Signal",
                direction="in",
                causality="input",
                fields=(Field("value", "Real"),),
                doc=None,
            ),
            PortGroup(
                name="y",
                definition="Signal",
                direction="out",
                causality="output",
                fields=(Field("value", "Real"),),
                doc=None,
            ),
        ),
        variables=(
            Variable(
                name="gain",
                type_name="Real",
                causality="parameter",
                variability="fixed",
                value_reference=0,
                index=1,
                description=None,
                member="gain",
                start=2.0,
                start_text="2.0",
            ),
            Variable(
                name="u",
                type_name="Real",
                causality="input",
                variability=None,
                value_reference=1,
                index=2,
                description=None,
                member="u.value",
                start=0.0,
                start_text="0",
            ),
            Variable(
                name="y",
                type_name="Real",
                causality="output",
                variability=None,
                value_reference=2,
                index=3,
                description=None,
                member="y.value",
            ),
        ),
    )
    return Reduction(
        components=(component,),
        identity=ExportIdentity("Root", False),
        package="Demo",
        experiment=Experiment(start_time=0.0, stop_time=1.0, step_size=0.1),
        root="Root",
    )


def _tree(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_every_emitter_accepts_a_reduction(tmp_path: Path) -> None:
    """Drift caught: a generator requires a source or an architecture again."""
    reduction = _reduction()

    descriptions = generate_model_description(
        reduction, tmp_path / "md", generation_time=GENERATION_TIME
    )
    headers = generate_c_headers(reduction, tmp_path / "c")
    runtime = generate_c_runtime(reduction, tmp_path / "rt")
    modelica = generate_modelica(reduction, tmp_path / "mo")

    assert [path.name for path in descriptions] == ["modelDescription.xml"]
    assert [path.name for path in headers] == [
        "Demo_InterfaceCommon.h",
        "Demo_Scale.h",
    ]
    assert "Demo_Scale_fmi.cpp" in [path.name for path in runtime]
    assert "Demo_Scale_model.cpp" in [path.name for path in runtime]
    assert "Scale_Interface.mo" in [path.name for path in modelica]

    xml = descriptions[0].read_text(encoding="utf-8")
    assert 'modelName="Root.Scale"' in xml
    assert '<ScalarVariable name="gain"' in xml
    assert '<ScalarVariable name="u"' in xml
    assert '<ScalarVariable name="y"' in xml


def test_emitters_are_deterministic_from_one_reduction(tmp_path: Path) -> None:
    reduction = _reduction()
    first = tmp_path / "first"
    second = tmp_path / "second"

    generate_c_headers(reduction, first)
    generate_c_headers(reduction, second)

    assert _tree(first) == _tree(second)


def test_emitters_never_import_the_dialect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Drift caught: a parser import sneaks back into an emitter."""
    reduction = _reduction()
    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name.split(".")[0] == "pycps_sysml2":
            raise AssertionError(f"emitter imported the dialect: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)

    generate_model_description(
        reduction, tmp_path / "md", generation_time=GENERATION_TIME
    )
    generate_c_headers(reduction, tmp_path / "c")
    generate_c_runtime(reduction, tmp_path / "rt")
    generate_modelica(reduction, tmp_path / "mo")


def test_the_sysml_surface_is_gone_from_interfaces() -> None:
    names = {
        "architecture",
        "component",
        "components",
        "direction_causality",
        "export_identity",
        "fmu_units",
        "resolve_system",
        "to_reduction",
    }

    assert names.isdisjoint(pyfmi_interfaces.__all__)
    for name in names:
        assert not hasattr(pyfmi_interfaces, name)
