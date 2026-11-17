---
id: IMP-001
type: imp
title: Interface hash for the exported artifact set
summary: Emit a deterministic hash of the reduced variable set so a consumer can tell an interface changed while the guid stays frozen
date: 2026-11-17
status: suggested
---

# Interface hash for the exported artifact set

- **Question:** does the artifact carry anything that changes when the variable
  set changes and stays put when it does not?
- **Evidence:** no. The guid is `uuid5` over a frozen
  `pyssp_sysml2/<composition>/<component>` string, so adding, removing,
  retyping, or reordering a variable leaves it byte-identical while every later
  value reference moves. The name-derived C enum alias absorbs that shift inside
  the one tree we rewrite, but a consumer that cached value references against
  the guid — a Simulink FMI import block, a saved result file, a live `fmpy`
  session — sees "same FMU" and misbinds silently.
- **Change:** emit one deterministic `interface hash` over the reduced variable
  set — per component, the ordered (name, type, causality, variability, value
  reference, count) tuples plus a generator schema version — as a separate,
  consumable artifact next to the current outputs. The guid, `modelName`, and
  value-reference assignment stay exactly as they are. Whether it lands as
  vendor annotation content in `modelDescription.xml` or as a sibling file
  depends on `INFO-014`: annotation content is not modelled upstream yet, so the
  sibling file is the assumed shape and the annotation is the follow-up.
- **Risk:** spans `core/`, `model_description/`, and `fmu/`, so the one-variable-set
  contract and the cross-artifact gate both feel it, and the archive layout gains
  a file. It documents change detection, not compatibility: written as an ABI
  promise, consumers would read it as a guarantee the library does not make.
  Reproducibility holds only if the hash input is canonically ordered, not
  ordered by traversal accident.
- **Acceptance:** two architectures differing by one variable inserted mid-component
  produce different hashes while the guid stays byte-identical; the same
  architecture and `generation_time` produce byte-identical hash content; the
  hash is read from the built artifact, not from an intermediate string.
