"""The shared Reduction surface every artifact family builds on.

Families import the variable model, the primitive spelling tables, the export
identity, and the bundled headers here; core imports no family, so the
dependency arrow points one way.
"""

from __future__ import annotations

from pyfmi_interfaces.core.annotations import Annotation, AnnotationError
from pyfmi_interfaces.core.identity import (
    DEFAULT_GENERATION_TIME,
    GENERATION_TIME_FORMAT,
    GUID_NAMESPACE,
    component_guid,
    format_generation_time,
    guid,
    resolve_guid,
    utc_now,
)
from pyfmi_interfaces.core.model import (
    Component,
    Experiment,
    ExportIdentity,
    Field,
    PortGroup,
    Reduction,
    Variable,
    select_component,
)
from pyfmi_interfaces.core.resources import fmi2_headers
from pyfmi_interfaces.core.spelling import (
    CPP_TYPES,
    C_TYPES,
    DATA_TYPE_TAGS,
    DISCRETE_TYPES,
    INPUT_START,
    MODELICA_TYPES,
    c_type,
    modelica_type,
    sanitize_identifier,
)

__all__ = [
    "CPP_TYPES",
    "C_TYPES",
    "DATA_TYPE_TAGS",
    "Annotation",
    "AnnotationError",
    "DEFAULT_GENERATION_TIME",
    "DISCRETE_TYPES",
    "INPUT_START",
    "MODELICA_TYPES",
    "Component",
    "Experiment",
    "ExportIdentity",
    "Field",
    "GENERATION_TIME_FORMAT",
    "GUID_NAMESPACE",
    "PortGroup",
    "Reduction",
    "Variable",
    "c_type",
    "component_guid",
    "fmi2_headers",
    "format_generation_time",
    "guid",
    "modelica_type",
    "resolve_guid",
    "sanitize_identifier",
    "select_component",
    "utc_now",
]
