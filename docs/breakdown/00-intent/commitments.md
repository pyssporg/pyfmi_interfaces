---
id: INFO-017
type: info
title: Commitments
summary: The artifact boundary, one dialect interface, one FMI serializer, reproducibility, the reduction contract, regeneration, generated plumbing, and no build step.
date: 2026-11-17
status: current
---

# Commitments

Eight rules bind every change; a change that breaks one needs a vision edit
first.

- **The artifact is the library boundary.** Only FMI XML, C headers, C++ runtime
  sources, Modelica text, and the `.fmu` archive cross to another project.
- **One dialect interface.** The SysML dialect is read only through
  `pycps_sysml2`; this package must never import `pyssp_sysml2`.
- **One FMI serializer.** FMI XML is built, serialized, and validated only
  through `pyssp_standard.standard.fmi2`.
- **Reproducibility is a feature.** The same architecture and the same injected
  `generation_time` produce byte-identical files, including the archive.
- **The reduction is the contract.** Every generator reads the variable set
  and the primitive spelling through `pyfmi_sysml2.core`, never through a
  private copy, so the artifacts cannot disagree about either.
- **Regeneration is the update path.** Generated files are replaced whole,
  never patched; an interface change is absorbed by re-running the generators,
  never by reconciling artifacts by hand.
- **Plumbing is generated; the model is not.** The runtime implements the FMI
  2.0 entry points from the variable set; equations, integration, and event
  logic stay in the implementer's model file.
- **The library does not build.** It writes C++ sources and never invokes a
  compiler, emits a build system, or packages an unbuilt binary.
