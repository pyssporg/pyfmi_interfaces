"""The shared reduction surface every artifact family builds on.

Families import the variable model, the reduction, the primitive spelling
tables, the export identity, and the bundled headers here; core imports no
family, so the dependency arrow points one way.
"""

from __future__ import annotations

from pyfmi_sysml2.core.identity import (
    DEFAULT_GENERATION_TIME,
    GENERATION_TIME_FORMAT,
    GUID_NAMESPACE,
    component_guid,
    format_generation_time,
    guid,
    utc_now,
)
from pyfmi_sysml2.core.model import (
    Component,
    Experiment,
    ExportIdentity,
    Field,
    PortGroup,
    Reduction,
    Variable,
)
from pyfmi_sysml2.core.reduction import (
    architecture,
    component,
    components,
    direction_causality,
    export_identity,
    fmu_units,
    resolve_system,
    to_reduction,
)
from pyfmi_sysml2.core.resources import fmi2_headers
from pyfmi_sysml2.core.spelling import (
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
    "architecture",
    "c_type",
    "component",
    "component_guid",
    "components",
    "direction_causality",
    "export_identity",
    "fmi2_headers",
    "fmu_units",
    "format_generation_time",
    "guid",
    "modelica_type",
    "resolve_system",
    "sanitize_identifier",
    "to_reduction",
    "utc_now",
]
