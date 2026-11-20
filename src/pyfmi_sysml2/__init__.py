"""Generate FMI 2.0 CoSimulation artifacts from a SysML v2 architecture.

The SysML dialect is owned by :mod:`pycps_sysml2`; this package implements the
FMI half of it. The public surface is one function per artifact plus the
``pyfmi`` command line:

- :func:`generate_model_description` — ``modelDescription.xml``
- :func:`generate_c_headers` — C interface headers
- :func:`generate_c_runtime` — C++17 FMI 2.0 CoSimulation runtime
- :func:`generate_modelica` — Modelica connectors and package files
- :func:`fmi2_headers` — the bundled FMI 2.0 standard C headers
- :func:`fmu_units` — the ``:> FmuModel`` leaf definitions to export
- :func:`to_reduction` — the parser-free input every generator accepts

Parsing and generation are separable. :func:`to_reduction` turns an
architecture (or a path) into a :class:`Reduction`; every generator accepts
that reduction directly and then runs without importing ``pycps_sysml2``. The
``.fmu`` archive is written by ``pyssp_standard``'s ``FMU`` facade; import
``FMU`` from ``pyssp_standard`` and call ``FMU.package``.
"""

from pyfmi_sysml2.c import generate_c_headers, generate_c_runtime
from pyfmi_sysml2.core import (
    Component,
    Experiment,
    ExportIdentity,
    Reduction,
    Variable,
    components,
    fmi2_headers,
    fmu_units,
    to_reduction,
)
from pyfmi_sysml2.model_description import generate_model_description
from pyfmi_sysml2.modelica import generate_modelica

__version__ = "0.4.0"

__all__ = [
    "Component",
    "Experiment",
    "ExportIdentity",
    "Reduction",
    "Variable",
    "__version__",
    "components",
    "fmi2_headers",
    "fmu_units",
    "generate_c_headers",
    "generate_c_runtime",
    "generate_model_description",
    "generate_modelica",
    "to_reduction",
]
