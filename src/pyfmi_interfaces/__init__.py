"""Generate FMI 2.0 CoSimulation artifacts from a reduced interface model.

The caller supplies the reduction; this package is a pure artifact generator.
The public surface is one function per artifact plus the ``pyfmi`` command line:

- :func:`generate_model_description` — ``modelDescription.xml``
- :func:`generate_c_headers` — C interface headers
- :func:`generate_c_runtime` — C++17 FMI 2.0 CoSimulation runtime
- :func:`generate_modelica` — Modelica connectors and package files
- :func:`select_component` — the exported-component selection rule
- :func:`fmi2_headers` — the bundled FMI 2.0 standard C headers
- :class:`Annotation` — a tool id plus a validated verbatim XML payload
- :class:`ModelDescription` / :class:`ModelDescriptionXmlCodec` — the
  annotation-aware FMI 2.0 document view and its one canonical emitter

Every generator accepts a :class:`Reduction` and runs from that input alone. The
``.fmu`` archive is written by ``pyssp_standard``'s ``FMU`` facade;
import ``FMU`` from ``pyssp_standard`` and call ``FMU.package``.
"""

from pyfmi_interfaces.c import generate_c_headers, generate_c_runtime
from pyfmi_interfaces.core import (
    Annotation,
    AnnotationError,
    Component,
    Experiment,
    ExportIdentity,
    Reduction,
    Variable,
    fmi2_headers,
    select_component,
)
from pyfmi_interfaces.model_description import (
    ModelDescription,
    ModelDescriptionXmlCodec,
    generate_model_description,
)
from pyfmi_interfaces.modelica import generate_modelica

__version__ = "0.5.1"

__all__ = [
    "Annotation",
    "AnnotationError",
    "Component",
    "Experiment",
    "ExportIdentity",
    "ModelDescription",
    "ModelDescriptionXmlCodec",
    "Reduction",
    "Variable",
    "__version__",
    "fmi2_headers",
    "generate_c_headers",
    "generate_c_runtime",
    "generate_model_description",
    "generate_modelica",
    "select_component",
]
