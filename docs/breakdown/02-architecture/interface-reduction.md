---
id: INFO-003
type: info
title: Interface reduction
summary: core/reduction.py turns an architecture into Component, PortGroup, Field, and Variable objects, assigns value references once, and is the only place that decides which variables exist.
date: 2026-11-17
status: current
---

# Interface reduction

`core/reduction.py` is the single source of the variable set: every generator
reads it and none re-derives variables, causalities, or value references.

`components()` resolves the export unit, validates the parameter dialect, and
returns the exported components: a container root's leaf descendants sorted by
name, or a single part definition marked `:> FmuModel`. Each `Component` carries
parameter fields, port groups, and the flat `variables` tuple every generator
iterates.

Rules encoded here, not repeated in the generators: parameters first, then ports
and fields in declaration order, one VR per scalar restarting at 0 per
component; `direction_causality()` maps `out` to output and everything else to
input; `_fixed_count()` refuses a multiplicity FMI cannot express as scalars; a
flat connector control is an explicit refusal. C, C++, `*_DataType`, and
Modelica tables live in `core/spelling.py`, so no two artifacts spell a
primitive differently.

`resolve_system()` picks the `:> FmuModel` definition as the export unit, or
else the part definition that has parts and is not used as a part elsewhere;
several candidates require `composition=` and are refused by name.

The namespace is package-scoped: own-package definitions store under their bare
name and others under `<package>::<name>`, while `Definition.name` stays bare.
Root selection compares stored keys, so a definition from a second load root is
not itself a composition root; the qualifier never reaches an artifact.

`export_identity()` owns the naming rule: a container root names a component
`<system>.<component>`, a direct FMU uses the bare definition name, and both
guids derive from that one rule.
