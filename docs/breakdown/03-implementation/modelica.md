---
id: INFO-007
type: info
title: Modelica generation
summary: generate_modelica writes a configurable root package with undirected connectors plus, per component, a generated partial model whose port instances carry direction, and an implementer-owned model created once.
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

A connector is a type, so it is always undirected; the `<Name>_Interface.mo` port
instances carry `input`/`output`, or nothing for `inout` or undirected — the
instance is what an FMU export reads. Keyword-named ports gain a trailing
underscore; fields keep type and array size, arrays expanding to scalars.

Configuration, never constants: `package` defaults to `GeneratedInterfaces`;
`within` nests the root in an existing scope (only the root `package.mo` carries
the bare `within`); names come from the `Reduction`, nothing domain-specific.

The package is not an FMU: it carries no FMI export annotation and no
executable. A Modelica wrapper around a compiled FMU is a non-goal (`INFO-018`).
