---
id: INFO-001
type: info
title: Intent
summary: pyfmi_interfaces generates the FMI artifacts that set a model up on first use and refresh it on interface change, and refuses to become an FMI authoring tool.
date: 2026-11-17
status: current
---

# Intent

`pyfmi_interfaces` turns one parser-free interface `Reduction` into the FMI 2.0
CoSimulation artifacts a workflow consumes: `modelDescription.xml`, C interface
headers, a C++17 runtime, Modelica connectors with a partial-model seam, and a
packaged `.fmu`. It generates files; it does not parse SysML, compile models,
run simulations, or judge results.

The set serves two moments. At first use the implementer codes against the
generated interfaces, so a new model starts from the architecture, not a
hand-copied variable list. On interface change, regeneration replaces artifacts
whole; the implementer maintains only their own code and the architecture.

The runtime implements the FMI 2.0 entry points from the variable set, so the
implementer starts from plumbing. Model behaviour crosses one seam, created
once and never rewritten: `<stem>_model.cpp` (C++), `<Name>.mo` (Modelica).

The SysML dialect and the `Reduction` construction are not owned here.
`pyfmi_sysml` loads through `pycps_sysml2` and reduces once to the parser-free
`Reduction`; this package owns the interface model and emitters, implements the
FMI half of that contract, and nothing else.

**Scope.** Here: the parser-free interface model (`Component`, `PortGroup`,
`Field`, `Variable`, `Experiment`, `ExportIdentity`, `Reduction`);
modelDescription, C header, C++ runtime, and Modelica generation; deterministic
bytes from an injected generation time; the `pyfmi package` command. Elsewhere:
SysML parsing, selection, and reduction (`pyfmi_sysml` over `pycps_sysml2`);
FMI XML object model, codec, validator, archive writer, and `.fmu` packaging via
`pyssp_standard.FMU` (`pyssp_standard`); the four source-taking commands
(`pyfmi-sysml`); compiling generated sources (the implementer's build); SSP and
SysML emission (`pyssp_sysml2`).

**Boundaries.** Commitments `INFO-017`; refusals `INFO-018`.
