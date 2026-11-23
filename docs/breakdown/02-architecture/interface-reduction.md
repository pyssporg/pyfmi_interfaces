---
id: INFO-003
type: info
title: Interface reduction
summary: This package owns the Reduction types; the caller constructs the Reduction once, decides which variables exist, and every generator reads that contract as the one variable set.
date: 2026-11-17
status: current
---

# Interface reduction

`core/model.py` owns the interface model: `Component`, `PortGroup`,
`Field`, `Variable`, `Experiment`, `ExportIdentity`, and `Reduction`. The caller
constructs the `Reduction` with its components, `ExportIdentity`, package and
optional `root` name, and `Experiment`. A generator given a `Reduction` needs
no other input.

Each `Component` carries parameter fields, port groups, the flat `variables`
tuple every generator iterates, and its authored `attributes`; each `PortGroup`
carries its port definition's attributes. `Variable.start` is the typed value
(neutral for an input) and `Variable.start_text` its FMI text, both supplied at
construction, so the model needs no formatter.

The Reduction encodes the rules the generators rely on: parameters first, then
ports and fields in declaration order, one VR per scalar restarting at 0 per
component; `out` maps to FMI output and everything else to input; every array
has a fixed count, because FMI cannot express a variable multiplicity; a typed
container (metadata, parameter set, experiment) is not a signal field. A port
whose only member is a non-array `value` exports the port name alone (`y`); its
`Variable.member` stays `y.value`, which is why the C value-reference enum is
unchanged. C, C++, `*_DataType`, and Modelica tables live in `core/spelling.py`,
so no two artifacts spell a primitive differently.

`ExportIdentity` owns the naming rule: a container root names a component
`<system>.<component>`, a direct FMU uses the bare definition name, and both
guids derive from that one rule.

`select_component()` in `core/model.py` is the single component-selection rule
every generator uses: it returns the exported component whose name matches and
raises `ValueError` for an unknown name. The guid key namespace literal
`pyssp_sysml2` is frozen for byte-identical GUIDs from earlier releases; it must
not be renamed with the distribution.
