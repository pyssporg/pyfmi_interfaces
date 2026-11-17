---
id: INFO-002
type: info
title: Module map
summary: One core package plus one subpackage per artifact family; dependency flows pycps_sysml2 to pyfmi_sysml2 to pyssp_standard, never through pyssp_sysml2.
date: 2026-11-17
status: current
---

# Module map

`src/pyfmi_sysml2/` is one `core/` package and one subpackage per artifact family; a new artifact type is a directory with one explicit registration line.

- `__init__.py` the facade, `cli.py` the dispatcher collecting family `COMMANDS`;
- `core/reduction.py` decides which variables exist and assigns value references once;
- `core/model.py` holds `Component`, `Field`, `PortGroup`, and `Variable`;
- `core/identity.py` the injected clock and uuid5 guid, `core/resources.py` the bundled-header lookup;
- `core/cli.py` the `Command` registry, shared options, and error policy;
- `core/spelling.py` every C, C++, `*_DataType`, and Modelica table, so no two artifacts spell a primitive differently;
- `c/headers.py` the C interface headers, `c/runtime.py` the C++17 runtime and model seam;
- `model_description/document.py` the XML document, `modelica/package.py` the connector set and implementer model;
- `fmu/__init__.py` only the `pyfmi package` command, with packaging in `pyssp_standard`'s `FMU` facade;
- `fmi2_headers/*.h` the bundled FMI 2.0.5 headers.

**Dependency rule.** `core/` imports no family; a family imports `core/` and its
own emitters, never another family; only `__init__.py` and `cli.py` import
families:

`core/ <- {c, model_description, modelica, fmu} <- {__init__.py, cli.py}`

Each family `__init__.py` exposes generators and a `COMMANDS` tuple; `cli.py`
concatenates them, with a static test requiring registration to match the family
directories. The package depends one way only, `pycps_sysml2` -> `pyfmi_sysml2`
-> `pyssp_standard`; `pyssp_sysml2` is never imported, and every generator reads
the variable set through `core/`.

**Adding a family.** Add `<family>/__init__.py` and one emitter per artifact; read
variables through `core.reduction` and spell primitives through `core.spelling`;
expose generators plus a `COMMANDS` tuple built with `core/cli.py` helpers;
register the family in `cli.py`, re-export from `__init__.py`, and add fixtures with byte-compared goldens and a `case.md`.
