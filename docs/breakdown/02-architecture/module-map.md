---
id: INFO-002
type: info
title: Module map
summary: One core package plus one subpackage per artifact family; dependency flows sysmlpy to pycps_sysml2 to pyfmi_sysml2 to pyssp_standard.fmi2, never through pyssp_sysml2.
date: 2026-11-17
status: current
---

# Module map

`src/pyfmi_sysml2/` is one `core/` package and one subpackage per artifact
family; a new artifact type is a directory with one explicit registration line.

```
src/pyfmi_sysml2/
├── __init__.py        # public surface: generators, stage_fmu, types
├── cli.py             # collects the family COMMANDS tuples, dispatches
├── fmi2_headers/*.h   # bundled FMI 2.0 standard headers, package data
├── core/              # model, reduction, spelling, identity, resources, cli
├── c/                 # headers, runtime
├── model_description/ # document
├── modelica/          # package
└── fmu/               # archive
```

**Ownership.** `core/reduction.py` decides which variables exist and assigns
value references once; `core/model.py` holds the `Component`, `Field`,
`PortGroup`, and `Variable` dataclasses; `core/identity.py` the injected clock
and uuid5 guid; `core/resources.py` the bundled-header lookup; `core/cli.py`
the `Command` registry, shared options, and error policy. `core/spelling.py`
holds every C, C++, `*_DataType`, and Modelica table in one module on purpose:
artifacts that share a variable set must share the primitive spelling. Each
family owns its artifact: `c/` headers and runtime, `model_description/` the
XML document, `modelica/` the package, `fmu/` the archive.

**Dependency rule.** `core/` imports no family; a family imports `core/` and its
own emitters, never another family; only `__init__.py` and `cli.py` import
families, so the arrow runs one way:

`core/ <- {c, model_description, modelica, fmu} <- {__init__.py, cli.py}`

Each family `__init__.py` exposes its generators and a `COMMANDS` tuple of
`core.cli.Command` entries; `cli.py` concatenates them. No entry points, no
importlib scanning, no plugin discovery; a static test fails when the registered
commands and the family directories disagree. The package depends one way only,
`pycps_sysml2` (dialect) -> `pyfmi_sysml2` -> `pyssp_standard` (FMI XML,
archive); `pyssp_sysml2` is a sibling, never imported. Every generator reads the
variable set through `core/` and none re-derives it.

**Adding an artifact family.**

1. Add `<family>/__init__.py` and one emitter module per artifact.
2. Read variables through `core.reduction` / `core.model`, spell primitives
   through `core.spelling`; add a new primitive there once, never copy a table.
3. Expose the generators and a `COMMANDS` tuple; `configure` uses the shared
   option helpers in `core/cli.py`.
4. Add the one explicit import and `*FAMILY_COMMANDS` line in `cli.py`; re-export
   public names from `__init__.py`.
5. Add fixtures with byte-compared goldens and a `case.md`.
