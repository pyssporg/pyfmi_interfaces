---
id: CP-002
type: capability
title: Variable model
summary: Parameters are typed values, lists expand into scalars, port fields are dotted names, and value references restart at zero per component.
date: 2026-11-17
status: current
---

# Variable model

The variable set is fixed before any artifact is written, by the caller's
`Reduction`.

- **Parameters** appear as `Field` entries in `Component.parameters` plus a
  `Variable(field, causality="parameter", variability="fixed")` carrying the
  default as typed `Variable.start`. `Variable.start_text` is that value
  rendered for FMI; a parameter set is not applied here.
- A fixed-length list expands into one scalar per element, named
  `<name>[<index>]`, offset by the field's `base_index`; the array count is
  fixed, because FMI has no variable multiplicity.
- **Ports** contribute one variable per payload field, named `<port>.<field>`;
  a list field expands to `<port>.<field>[<index>]`. A port whose only member is
  a non-array `value` is the exception: like the SSP connector, its variable is
  named after the port alone (`y`, never `y.value`). An array-valued `value`
  stays `<port>.value[<index>]`, because one scalar variable per element cannot
  carry a bare connector name.
- `out` becomes `causality="output"`; `in`, `inout`, and an undirected port
  become `causality="input"`, because FMI 2.0 has no bidirectional scalar.
- `Integer`, `Boolean`, and `String` fields are `variability="discrete"`; only
  `Real` may stay continuous.
- Every input carries a neutral typed `start` (`0`, `false`, `""`) because FMI
  2.0 requires one; its `start_text` is rendered from that value, and outputs
  carry neither.
- Parameter ports and typed containers are not signal fields; metadata,
  parameter sets, and experiments stay out of `variables`, never emitted as
  fields.
- **Ordering:** value references restart at 0 per component, parameters first,
  then ports and fields in declaration order; components are exported sorted by
  name and each carries the same numbered set to every artifact.
- One scalar per variable: FMI 2.0 has no array variable.
- Each `Component` and signal `PortGroup` also carries authored attributes as
  `(name, value)` pairs, so a consumer never re-reads them from elsewhere.
