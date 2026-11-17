---
id: INFO-007
type: info
title: Modelica generation
summary: generate_modelica writes a configurable root package with connectors plus, per component, a generated partial model and an implementer-owned model.
date: 2026-11-17
status: current
---

# Modelica generation

`generate_modelica()` writes one package under `<output>/<package>/`. Four files
are architecture-wide:

- `package.mo` — the root package with the `within` clause and
  `annotation(uses(Modelica(version="4.0.0")))`;
- `package.order` — `Interfaces`, `GeneratedInterfaces`, then each component's
  interface model and model;
- `Interfaces.mo` — `<Type>Input = input <Type>` and `<Type>Output = output
  <Type>` for Real, Integer, Boolean, and String;
- `GeneratedInterfaces.mo` — one `connector` per distinct port definition.

Each exported component adds two files:

- `<Name>_Interface.mo` — a `partial model` holding the plumbing: one
  `parameter` per reduction parameter, carrying the value it was authored with,
  and one connector instance per port. A parameter with no authored value stays
  unbound instead of being guessed at; a port named after a Modelica keyword is
  spelled with a trailing underscore. Generated whole on every run.
- `<Name>.mo` — a `model` that `extends <Name>_Interface` and carries an empty
  `equation` section with a TODO. Created once and never rewritten, the
  Modelica counterpart of the C++ model file. All implementer logic lives
  inside this class, helpers nested, so `package.order` stays fully generated.

A connector is a type, so its direction must hold for every usage. The member
prefix is `input`/`output` only when all usages agree; if any usage is `inout`,
undirected, or disagrees with another, the connector stays undirected. This is
the Modelica counterpart of the FMI rule that `inout` becomes an input.

The split is honest about incompleteness: a `partial model` is exempt from
balance checking, so the generated half always checks clean, while the
implementer's model fails to build until it has equations. `checkModel` accepts
an under-determined model, so the oracle is `buildModel`: a fixture model that
extends the partial must build, and the untouched scaffold must fail with
`Too few equations`.

Configuration, never constants: `package` defaults to `GeneratedInterfaces`;
`within` nests the root inside an existing scope; the subpackages are declared
inside the parent, so only the root `package.mo` carries the bare `within`.

Names are emitted from the architecture; no domain-specific package, connector,
or model name is baked into the generator. Fields keep their FMI type and fixed
array size; a list field is `Type name[n]` in the connector, while the FMI side
expands it into scalars. The package is not an FMU: it carries no FMI export
annotation and no executable.
