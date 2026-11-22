"""Deprecated: import :mod:`pyfmi_interfaces` instead.

``pyfmi_sysml2`` is a compatibility shim kept for one deprecation window. It
re-exports the public surface of :mod:`pyfmi_interfaces` and registers every
``pyfmi_interfaces`` submodule under the matching ``pyfmi_sysml2`` name, so
``import pyfmi_sysml2.core`` (and ``.c``, ``.model_description``,
``.modelica``, ``.fmu``, ``.cli``) keeps working unchanged.

New code should import ``pyfmi_interfaces`` directly. This shim will be removed
in a future release.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys

import pyfmi_interfaces as _interface_package

__version__ = _interface_package.__version__
__all__ = list(_interface_package.__all__)


def _reexport_public() -> None:
    namespace = globals()
    for name in _interface_package.__all__:
        if name != "__version__":
            namespace[name] = getattr(_interface_package, name)


def _register_submodules() -> None:
    prefix = _interface_package.__name__
    for info in pkgutil.walk_packages(_interface_package.__path__, prefix + "."):
        module = importlib.import_module(info.name)
        legacy_name = __name__ + info.name[len(prefix) :]
        sys.modules.setdefault(legacy_name, module)
    # Attribute-style access, e.g. ``pyfmi_sysml2.core`` after a bare import.
    for legacy_name, module in list(sys.modules.items()):
        if legacy_name == __name__ or not legacy_name.startswith(__name__ + "."):
            continue
        parent_name, _, child = legacy_name.rpartition(".")
        parent = sys.modules.get(parent_name)
        if parent is not None:
            setattr(parent, child, module)


_reexport_public()
_register_submodules()
