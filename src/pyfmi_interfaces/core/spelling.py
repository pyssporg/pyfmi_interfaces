"""How an FMI primitive is spelled in every generated artifact.

All four spelling tables — C, C++, ``*_DataType`` tag, and Modelica — live in
this one module on purpose. The commitment that every generator reads one
shared variable set only holds if the generators also share the primitive
spelling: distributing the tables into the artifact families would let the C
header, the runtime, and the Modelica connector disagree about what a ``Real``
is. A new primitive is added once, here.
"""

from __future__ import annotations

import re

#: FMI primitive name to C type used by the generated headers.
C_TYPES = {
    "Real": "double",
    "Integer": "int",
    "Boolean": "bool",
    "String": "const char*",
}

#: FMI primitive name to the C++ member type used inside ``*_Instance``.
CPP_TYPES = {
    "Real": "double",
    "Integer": "int",
    "Boolean": "bool",
    "String": "std::string",
}

#: FMI primitive name to the generated ``*_DataType`` enumerator suffix.
DATA_TYPE_TAGS = {
    "Real": "REAL",
    "Integer": "INTEGER",
    "Boolean": "BOOLEAN",
    "String": "STRING",
}

#: FMI 2.0 allows ``continuous`` variability only for Real variables.
DISCRETE_TYPES = ("Integer", "Boolean", "String")

#: FMI 2.0 requires a start value on inputs; the caller authors none, so the
#: neutral zero value of each primitive stands in.
INPUT_START = {"Real": 0.0, "Integer": 0, "Boolean": False, "String": ""}

#: FMI primitive name to the Modelica type used in connectors.
MODELICA_TYPES = {
    "Real": "Real",
    "Integer": "Integer",
    "Boolean": "Boolean",
    "String": "String",
}


def c_type(type_name: str, *, cpp: bool = False) -> str:
    """C or C++ storage type for an FMI primitive."""
    table = CPP_TYPES if cpp else C_TYPES
    return table.get(type_name, table["Real"])


def modelica_type(type_name: str) -> str:
    """Modelica type for an FMI primitive (unknown types keep their name)."""
    return MODELICA_TYPES.get(type_name, type_name)


def sanitize_identifier(text: str) -> str:
    """Upper-case a dotted or bracketed name into a C identifier fragment."""
    return re.sub(r"[^0-9A-Za-z]", "_", text).upper()
