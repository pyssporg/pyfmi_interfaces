---
id: INFO-017
type: info
title: Commitments
summary: The artifact boundary, one dialect interface, one FMI serializer, upstream packaging, reproducibility, the reduction contract, regeneration, generated plumbing, and no build step.
date: 2026-11-17
status: current
---

# Commitments

Nine rules bind every change; a change that breaks one needs a vision edit
first.

- **The artifact is the library boundary.** Only FMI XML, C headers, C++ runtime
  sources, Modelica text, and the `.fmu` archive cross to another project.
- **One dialect interface.** The dialect is read only through `pycps_sysml2`;
  this package never imports `pyssp_sysml2`.
- **One FMI serializer.** FMI XML is built, serialized, and validated only
  through `pyssp_standard.standard.fmi2`.
- **Packaging is upstream.** `pyfmi package` delegates to `pyssp_standard.FMU`;
  no archive writer lives here.
- **Reproducibility is a feature.** The same architecture and injected
  `generation_time` produce byte-identical files, archive included.
- **The reduction is the contract.** Every generator reads the variable set and
  primitive spelling through `pyfmi_sysml2.core`, never a private copy, so the
  artifacts cannot disagree about either.
- **Regeneration is the update path.** Generated surfaces are replaced whole,
  never patched; re-running the generators absorbs an interface change. The
  implementer's model file is the exception: created once, never rewritten.
- **Plumbing is generated; the model is not.** The runtime implements the FMI
  2.0 entry points from the variable set; equations, integration, and event
  logic stay in `<stem>_model.cpp` (C++) or `<Name>.mo` (Modelica).
- **The library does not build.** It writes C++ sources and never invokes a
  compiler, emits a build system, or packages an unbuilt binary.
