---
id: INFO-001
type: info
title: Intent
summary: pyfmi_sysml2 generates the FMI artifacts that set a model up on first use and refresh it on interface change, and refuses to become an FMI authoring tool.
date: 2026-11-05
status: current
---

# Intent

## Purpose

`pyfmi_sysml2` turns one SysML v2 architecture into the FMI 2.0 CoSimulation
artifacts a simulation workflow consumes: `modelDescription.xml`, C interface
headers, Modelica connectors, and a packaged `.fmu`. It generates files; it does
not compile models, run simulations, or judge results.

That artifact set exists for two recurring moments in development. At first use
it hands the implementer the interfaces to code against, so a new model starts
from the architecture instead of a hand-copied variable list. When the interface
changes, regenerating is the update path: artifacts are replaced whole, never
patched, so the implementer maintains only their own code and the architecture.

The first use also emits a C++17 runtime that implements the FMI 2.0 entry
points from the variable set, so the implementer starts from working plumbing
instead of thirty empty functions. Model behaviour crosses one seam: a model
file the generator creates once and never rewrites.

The SysML dialect is not owned here. `pycps_sysml2` is the dialect home: it
parses the model and exposes parameters, ports, controls, and metadata.
`pyfmi_sysml2` implements the FMI half of that contract and nothing else.

## Scope

Belongs here:

- the reduction of an architecture onto one FMI variable set;
- modelDescription, C header, C++ runtime, Modelica, and FMU archive generation;
- deterministic bytes from an injected generation time;
- the `pyfmi` command line.

Belongs elsewhere:

- SysML parsing, IR, variation, selection, parameter markers: `pycps_sysml2`;
- FMI XML object model, codec, validator, archive writer: `pyssp_standard`;
- compiling the generated C++ sources, build systems, and the FMU binary: the
  implementer's build;
- SSP, SSD, SSV, SSM emission and SysML synthesis: `pyssp_sysml2`.

## Boundaries

The commitments that bind the design are in `INFO-017`; the work it refuses is
in `INFO-018`.
