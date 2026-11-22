"""The deprecated ``pyfmi_sysml2`` name is an import-compatible shim."""

from __future__ import annotations

import importlib
import sys

import pytest

pytestmark = pytest.mark.static


def test_legacy_name_reexports_the_public_surface():
    import pyfmi_interfaces
    import pyfmi_sysml2

    assert pyfmi_sysml2.__version__ == pyfmi_interfaces.__version__
    for name in pyfmi_interfaces.__all__:
        if name == "__version__":
            continue
        assert getattr(pyfmi_sysml2, name) is getattr(pyfmi_interfaces, name)


@pytest.mark.parametrize(
    "subpackage",
    ["c", "core", "model_description", "modelica", "fmu", "cli"],
)
def test_subpackages_import_under_the_legacy_name(subpackage):
    legacy = importlib.import_module(f"pyfmi_sysml2.{subpackage}")
    modern = importlib.import_module(f"pyfmi_interfaces.{subpackage}")

    assert legacy is modern
    assert sys.modules[f"pyfmi_sysml2.{subpackage}"] is modern


def test_shim_docstring_marks_the_deprecation():
    import pyfmi_sysml2

    assert "Deprecated" in (pyfmi_sysml2.__doc__ or "")
