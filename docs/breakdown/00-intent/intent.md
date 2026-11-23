---
id: INFO-001
type: info
title: Intent
summary: pyfmi_interfaces generates the FMI artifacts that set a model up on first use and refresh it on interface change, and refuses to become an FMI authoring tool.
date: 2026-11-17
status: current
---

# Intent

`pyfmi_interfaces` turns one caller-built interface `Reduction` into the FMI 2.0
CoSimulation artifacts a workflow consumes: `modelDescription.xml`, C interface
headers, a C++17 runtime, Modelica connectors with a partial-model seam, and a
packaged `.fmu`. It generates files; it does not compile models, run
simulations, or judge results.

The set serves two moments. At first use the implementer codes against the
generated interfaces, so a new model starts from a specified interface, not a
hand-copied variable list. On interface change, regeneration replaces artifacts
whole; the implementer maintains only their own code and the input `Reduction`.

The runtime implements the FMI 2.0 entry points from the variable set, so the
implementer starts from plumbing. Model behaviour crosses one seam, created
once and never rewritten: `<stem>_model.cpp` (C++), `<Name>.mo` (Modelica).

The `Reduction` construction is not owned here. A caller builds the `Reduction`
once; this package owns the interface model and emitters and implements the FMI
half of that contract, and nothing else.

**Scope.** Here: the interface model (`Component`, `PortGroup`,
`Field`, `Variable`, `Experiment`, `ExportIdentity`, `Reduction`);
modelDescription, C header, C++ runtime, and Modelica generation; deterministic
bytes from an injected generation time; the `pyfmi package` command. Elsewhere:
constructing the `Reduction`; FMI XML object model, codec, validator, archive
writer, and `.fmu` packaging via `pyssp_standard.FMU` (`pyssp_standard`);
compiling generated sources (the implementer's build).

**Boundaries.** Commitments `INFO-017`; refusals `INFO-018`.
