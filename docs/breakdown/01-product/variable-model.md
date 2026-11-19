---
id: CP-002
type: capability
title: Variable model
summary: Parameters come from the parameter dialect, lists expand into scalars, port fields are dotted names, and value references restart at zero per component.
date: 2026-11-17
status: current
---

# Variable model

The variable set is fixed before any artifact is written, from parameters and
ports.

- **Parameters** come from the parameter dialect only (`in port parameters
  ...`). A flat parameter attribute is rejected, never silently dropped.
- A parameter keeps its interface default as `start`, with `variability=fixed`
  and `causality=parameter`; an applied parameter set does not override it.
- A fixed-length list expands into one scalar per element, named
  `<name>[<index>]`, offset by `--base-index`; a non-fixed multiplicity is
  refused.
- **Ports** contribute one variable per payload field, named `<port>.<field>`;
  a list field expands to `<port>.<field>[<index>]`.
- `out` becomes `causality="output"`; `in`, `inout`, and an undirected port
  become `causality="input"`, because FMI 2.0 has no bidirectional scalar.
- `Integer`, `Boolean`, and `String` fields are `variability="discrete"`; only
  `Real` may stay continuous.
- Every input carries a neutral `start` (`0`, `false`, `""`) because FMI 2.0
  requires one and the dialect authors none; outputs carry none.
- Parameter ports and typed containers are not signal fields; an attribute
  whose type is FMU metadata, SSP metadata, a parameter set, or an experiment
  is skipped by `classify_attribute`, never emitted as a field.
- **Ordering:** value references restart at 0 per component, parameters first,
  then ports and fields in declaration order; components are exported sorted by
  name and each carries the same numbered set to every artifact.
- One scalar per variable: FMI 2.0 has no array variable.
