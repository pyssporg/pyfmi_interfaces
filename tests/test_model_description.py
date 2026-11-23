"""Component tests for the ``modelDescription.xml`` emission path."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from pyfmi_interfaces import generate_model_description
from pyfmi_interfaces.core import (
    Component,
    Experiment,
    ExportIdentity,
    Reduction,
    Variable,
)
from pyfmi_interfaces.model_description.document import render_model_description

pytestmark = pytest.mark.component

GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _variable(
    name: str, causality: str, value_reference: int, index: int
) -> Variable:
    return Variable(
        name=name,
        type_name="Real",
        causality=causality,
        variability="continuous",
        value_reference=value_reference,
        index=index,
        description=None,
        member=name,
    )


def _reduction() -> Reduction:
    component = Component(
        name="Scale",
        doc=None,
        parameters=(),
        ports=(),
        variables=(
            _variable("u", "input", 0, 1),
            _variable("y", "output", 1, 2),
        ),
    )
    return Reduction(
        components=(component,),
        identity=ExportIdentity("Root", False),
        package="Demo",
        experiment=Experiment(start_time=0.0, stop_time=1.0, step_size=0.1),
        root="Root",
    )


def test_default_experiment_is_present_by_default() -> None:
    xml = render_model_description(
        _reduction(), "Scale", generation_time=GENERATION_TIME
    )

    assert "<DefaultExperiment" in xml


def test_default_experiment_is_absent_when_excluded(tmp_path: Path) -> None:
    paths = generate_model_description(
        _reduction(),
        tmp_path,
        generation_time=GENERATION_TIME,
        include_default_experiment=False,
    )
    xml = paths[0].read_text(encoding="utf-8")

    assert "DefaultExperiment" not in xml
