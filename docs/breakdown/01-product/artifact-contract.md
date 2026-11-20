---
id: CP-001
type: capability
title: FMI 2.0 CoSimulation artifact contract
summary: Six outputs from one reduction: a validated modelDescription, C interface headers, C++17 runtime sources with a model seam, a Modelica package with an implementer model, and a deterministically packaged .fmu.
date: 2026-11-17
status: current
---

# FMI 2.0 CoSimulation artifact contract

All outputs read the one `Reduction` from `core/`:

- `modelDescription.xml`, validated through `pyssp_standard.standard.fmi2`;
- C interface headers `<prefix>_InterfaceCommon.h` and one `<prefix>_<Component>.h` per exported component;
- C++17 runtime with C linkage: `<stem>_fmi.cpp`, `<stem>_hooks.h`, and the bundled headers under `<out>/fmi2/`, all regenerated whole;
- the model seam `<stem>_model.cpp`, created once and never rewritten, with five hooks and an implementer-owned `user_data` that survives `fmi2Reset` (`CP-005`);
- a Modelica package: connector set, `<Name>_Interface` partial models, and `<Name>` implementer models created once and never rewritten;
- the packaged `.fmu`, written by `pyssp_standard.FMU` through `pyfmi package`; this package writes no archive.

Archive layout: `modelDescription.xml` at the zip root, never nested; `binaries/linux64/<modelIdentifier>.so`, built by the consumer and executable; `sources/` for the `--header` files; `resources/` and `documentation/` only when supplied.

`modelDescription.xml` carries `fmiVersion="2.0"`, a `modelName`, and a `guid`; exactly one `CoSimulation` element with `modelIdentifier`; a unique `name` and `valueReference` and exactly one typed child per `ScalarVariable`; index-ordered `ModelStructure/Outputs` and `InitialUnknowns` without duplicates; it passes `Fmi2ModelDescriptionValidator`, semantic and XSD.

Consistency: modelDescription, C headers, and C++ runtime carry the same numbered set from the one reduction; the Modelica package mirrors the same names and order, and the packager copies the files; the binary stem equals the `modelIdentifier`; repacking equal inputs yields identical bytes; `generationDateAndTime` comes from the injected clock, not the wall clock.

The schema allows more than this contract emits: optional FMI features the dialect does not author, authoring attributes included, are absent rather than invented.
