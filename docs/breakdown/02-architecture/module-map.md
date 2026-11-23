---
id: INFO-002
type: info
title: Module map
summary: One core package plus one subpackage per artifact family; the package is parser-free, reads a Reduction built by pyfmi_sysml, and depends on pyssp_standard, never on pycps_sysml2 or pyssp_sysml2.
date: 2026-11-17
status: current
---

# Module map

`src/pyfmi_interfaces/` is one `core/` package and one subpackage per artifact family; a new artifact type is a directory with one explicit registration line.

- `__init__.py` the facade, `cli.py` the dispatcher collecting family `COMMANDS`;
- `core/model.py` holds the parser-free interface model — `Component`, `Field`,
  `PortGroup`, `Variable`, `Experiment`, `ExportIdentity`, and `Reduction` — plus
  `select_component()`, the one component-selection rule;
- `core/identity.py` the injected clock and uuid5 guid, `core/resources.py` the bundled-header lookup;
- `core/annotations.py` the tool-independent `Annotation` value (`name` plus a
  validated verbatim XML payload) and its error;
- `core/cli.py` the `Command` registry, shared options, and error policy;
- `core/spelling.py` every C, C++, `*_DataType`, and Modelica table, so no two artifacts spell a primitive differently;
- `c/headers.py` the C interface headers, `c/runtime.py` the C++17 runtime and model seam;
- `model_description/document.py` the one XML emitter: the document, the
  `include_default_experiment` switch, the ordered `VendorAnnotations` view, and
  its codec, `modelica/package.py` the connector set and implementer model;
- `fmu/__init__.py` only the `pyfmi package` command, with packaging in `pyssp_standard`'s `FMU` facade;
- `fmi2_headers/*.h` the bundled FMI 2.0.5 headers;
- `src/pyfmi_sysml2/` a deprecated import shim that only re-exports the public
  surface and registers the submodules; new code imports `pyfmi_interfaces`.

**Dependency rule.** `core/` imports no family; a family imports `core/` and its
own emitters, never another family; only `__init__.py` and `cli.py` import
families:

`core/ <- {c, model_description, modelica, fmu} <- {__init__.py, cli.py}`

Each family `__init__.py` exposes generators and a `COMMANDS` tuple; `cli.py`
concatenates them, with a static test requiring registration to match the family
directories. The package depends one way only, `pyfmi_interfaces` ->
`pyssp_standard`; no SysML parser and no `pyssp_sysml2` import appears here, and
every generator reads the variable set through `core/`.

**Interface model.** `pyfmi_sysml` owns the single parse and builds the
parser-free `Reduction` (components, export identity, package name, and
experiment). Every generator accepts that `Reduction` and works without the
dialect, so a caller parses once and generates elsewhere.

**Adding a family.** Add `<family>/__init__.py` and one emitter per artifact; read
variables through `core.model` and spell primitives through `core.spelling`;
expose generators plus a `COMMANDS` tuple built with `core/cli.py` helpers;
register the family in `cli.py`, re-export from `__init__.py`, and add fixtures with byte-compared goldens and a `case.md`.
