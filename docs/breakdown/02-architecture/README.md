---
title: Architecture
summary: The module map, the single interface reduction, and the determinism rules behind every artifact.
---

# Architecture

How the package is divided, which module owns the variable set, and why two runs
produce the same bytes.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **INFO-002** [Module map](module-map.md) — One core package plus one subpackage per artifact family; every generator reads a caller-built Reduction, and the package depends only on pyssp_standard.
- **INFO-003** [Interface reduction](interface-reduction.md) — This package owns the Reduction types; the caller constructs the Reduction once, decides which variables exist, and every generator reads that contract as the one variable set.
- **INFO-004** [Determinism model](determinism.md) — A uuid5 guid from a frozen namespace string, a fixed default epoch, and an epoch-stamped sorted archive make every artifact reproducible.
<!-- pb:index:end -->
