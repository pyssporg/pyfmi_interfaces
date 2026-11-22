---
id: INFO-003
type: info
title: Interface reduction
summary: This package owns the parser-free Reduction types; pyfmi_sysml builds the Reduction once, decides which variables exist, and every generator here reads that contract as the one variable set.
date: 2026-11-17
status: current
---

# Interface reduction

`core/model.py` owns the parser-free interface model: `Component`, `PortGroup`,
`Field`, `Variable`, `Experiment`, `ExportIdentity`, and `Reduction`. The single
source of the variable set is `pyfmi_sysml`'s `to_reduction()`: it resolves the
export unit, validates the parameter dialect, and returns a `Reduction` with
components, `ExportIdentity`, package and selected `root` names, and
`Experiment`. This package imports no parser; a generator given a `Reduction`
never reads the dialect.

`to_reduction()` and its parser-side helpers — `components()`,
`resolve_system()`, `fmu_units()`, `export_identity()`, and
`direction_causality()` — live in `pyfmi_sysml`. `components()` returns the
container root's leaf descendants sorted by name, or the single definition
marked `:> FmuModel`. Each `Component` carries parameter fields, port groups, the
flat `variables` tuple every generator iterates, and its authored `attributes`;
each `PortGroup` carries its resolved port definition's attributes.
`Variable.start` is the authored typed value (neutral for an input) and
`Variable.start_text` its FMI text, both produced by the reduction builder, so
the model needs no dialect formatter.

The Reduction encodes the rules the generators rely on: parameters first, then
ports and fields in declaration order, one VR per scalar restarting at 0 per
component; `out` maps to FMI output and everything else to input; a multiplicity
FMI cannot express as scalars is refused; a port attribute classified as a typed
container (metadata, parameter set, experiment) is skipped rather than emitted.
Member sets come from the effective view (`effective_members`), so inherited
parameters, parts, and port fields reduce exactly like declared ones. A port
whose only member is a non-array `value` exports the port name alone (`y`); its
`Variable.member` stays `y.value`, which is why the C value-reference enum is
unchanged. C, C++, `*_DataType`, and Modelica tables live in `core/spelling.py`,
so no two artifacts spell a primitive differently.

Root selection compares stored keys, so a definition from a second load root is
not itself a composition root; the qualifier never reaches an artifact.
`export_identity()` owns the naming rule: a container root names a component
`<system>.<component>`, a direct FMU uses the bare definition name, and both
guids derive from that one rule.
