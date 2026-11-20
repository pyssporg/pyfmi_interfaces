"""Contract: a ``Reduction`` is a complete, parser-free generator input.

This is the seam that lets parsing and generation be used separately: the
dialect is read once by ``to_reduction``, and every generator then produces the
same bytes from the reduction as from the architecture path, without importing
``pycps_sysml2`` again.
"""

from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from conftest import GENERATION_TIME, fixture_path
from pyfmi_sysml2 import (
    generate_c_headers,
    generate_c_runtime,
    generate_model_description,
    generate_modelica,
    to_reduction,
)

pytestmark = pytest.mark.contract

SOURCE = fixture_path("controller", "controller.sysml")


def _tree(root: Path) -> dict[str, bytes]:
    """Every generated file under ``root``, keyed by its relative path."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_generators_produce_the_same_bytes_from_a_reduction(tmp_path: Path) -> None:
    """Drift caught: a generator still reads the architecture, not the reduction."""
    reduction = to_reduction(SOURCE)
    runs = (
        (
            lambda root: generate_c_headers(SOURCE, root / "out"),
            lambda root: generate_c_headers(reduction, root / "out"),
        ),
        (
            lambda root: generate_c_runtime(SOURCE, root / "out"),
            lambda root: generate_c_runtime(reduction, root / "out"),
        ),
        (
            lambda root: generate_model_description(
                SOURCE, root / "out", generation_time=GENERATION_TIME
            ),
            lambda root: generate_model_description(
                reduction,
                root / "out",
                generation_time=GENERATION_TIME,
            ),
        ),
        (
            lambda root: generate_modelica(SOURCE, root / "out"),
            lambda root: generate_modelica(reduction, root / "out"),
        ),
    )

    for from_path, from_reduction in runs:
        expected = tmp_path / "path"
        actual = tmp_path / "reduction"
        from_path(expected)
        from_reduction(actual)
        assert _tree(actual) == _tree(expected)


def test_generators_do_not_import_the_dialect_for_a_reduction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Drift caught: a parser import added to a generator's reduction path."""
    reduction = to_reduction(SOURCE)
    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name.split(".")[0] == "pycps_sysml2":
            raise AssertionError(f"generator imported the dialect: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)

    generate_c_headers(reduction, tmp_path / "c")
    generate_c_runtime(reduction, tmp_path / "c")
    generate_model_description(
        reduction, tmp_path / "md", generation_time=GENERATION_TIME
    )
    generate_modelica(reduction, tmp_path / "mo")


def test_a_reduction_refuses_to_be_re_resolved() -> None:
    """Drift caught: overriding arguments of an already resolved export unit."""
    reduction = to_reduction(SOURCE)

    with pytest.raises(ValueError, match="already fixes composition"):
        to_reduction(reduction, composition="ControllerComposition")
    with pytest.raises(ValueError, match="already fixes composition"):
        to_reduction(reduction, base_index=1)
