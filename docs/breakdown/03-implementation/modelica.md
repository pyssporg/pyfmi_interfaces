---
id: INFO-007
type: info
title: Modelica generation
summary: generate_modelica writes a configurable root package with connectors plus, per component, a generated partial model and an implementer-owned model created once.
date: 2026-11-17
status: current
---

# Modelica generation

`generate_modelica()` writes one package under `<output>/<package>/`; the
default package is `GeneratedInterfaces`. The output contract:

- `package.mo` — root package with the `within` clause and
  `annotation(uses(Modelica(version="4.0.0")))`;
- `package.order` — `Interfaces`, `GeneratedInterfaces`, then each component's
  interface model and model;
- `Interfaces.mo` — `<Type>Input = input <Type>` and `<Type>Output = output
  <Type>` for Real, Integer, Boolean, and String;
- `GeneratedInterfaces.mo` — one `connector` per distinct port definition;
- `<Name>_Interface.mo` — a `partial model`: one `parameter` per reduction
  parameter carrying its authored value (unbound when none), and one connector
  instance per port. Regenerated whole on every run;
- `<Name>.mo` — a `model` that `extends <Name>_Interface` and carries an empty
  `equation` section with a TODO. Created once and never rewritten; the
  Modelica counterpart of the C++ model file.

A connector is a type, so its member prefix is `input`/`output` only when every
usage agrees; otherwise it stays undirected. A port named after a Modelica
keyword gains a trailing underscore. Fields keep their FMI type and fixed array
size; the FMI side expands arrays into scalars.

Configuration, never constants: `package` defaults to `GeneratedInterfaces`;
`within` nests the root inside an existing scope, so only the root `package.mo`
carries the bare `within`. Names come from the architecture; no domain-specific
name is baked in.

The package is not an FMU: it carries no FMI export annotation and no
executable. A Modelica wrapper around a compiled FMU is a non-goal (`INFO-018`).
