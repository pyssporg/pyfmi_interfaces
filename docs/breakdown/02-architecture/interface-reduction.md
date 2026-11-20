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
port attribute classified as a typed container (metadata, parameter set,
experiment) is skipped rather than emitted. Member sets are the effective view
(`effective_members`), so inherited parameters, parts, and port fields are
reduced exactly like declared ones. `_is_scalar_port()` mirrors the
SSP scalar-port rule, so a port whose only member is a non-array `value`
exports the port name alone (`y`); its `Variable.member` stays `y.value`,
which is why the C value-reference enum is unchanged. C, C++,
`*_DataType`, and Modelica tables live in `core/spelling.py`, so no two
artifacts spell a primitive differently.

`resolve_system()` picks the `:> FmuModel` definition as the export unit, or
else the part definition that has parts and is not used as a part elsewhere;
several candidates require `composition=` and are refused by name. A marked
candidate that another candidate specializes is a shared role base (a library's
`FmuInterop :> FmuModel`), not an export unit, so only the leaves count;
`composition=` may still name the base explicitly. An included root can supply
the export unit: a library may define the FMU another package packages, and the
leaf rule selects it the same way.

`fmu_units()` exposes that same leaf set without requiring `composition=`: it
drops shared bases and the marker, keeps every sibling leaf, and sorts by bare
name then stored key, so a caller can export each unit in turn. `resolve_system()`
still refuses several siblings.

The namespace is package-scoped: own-package definitions store under their bare
name and others under `<package>::<name>`, while `Definition.name` stays bare.
Root selection compares stored keys, so a definition from a second load root is
not itself a composition root; the qualifier never reaches an artifact.

`export_identity()` owns the naming rule: a container root names a component
`<system>.<component>`, a direct FMU uses the bare definition name, and both
guids derive from that one rule.
