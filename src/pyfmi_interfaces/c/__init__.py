"""C interface headers and the C++17 FMI runtime from a Reduction."""

from __future__ import annotations

from pyfmi_interfaces.c.headers import generate_c_headers
from pyfmi_interfaces.c.runtime import generate_c_runtime

__all__ = ["generate_c_headers", "generate_c_runtime"]
