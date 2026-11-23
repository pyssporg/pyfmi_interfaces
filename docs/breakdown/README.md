---
title: Product Breakdown — pyfmi_interfaces
summary: Current-state record of why the FMI generator exists, its artifact contract, architecture, implementation, verification, operation, and evolution.
---

# Product Breakdown — pyfmi_interfaces

Current-state record of `pyfmi_interfaces`: the artifact it promises, the workflow
it serves, and how generation is organized, verified, and released.

## The Seven Layers

- `00-intent/` — why the project exists and what it refuses to become.
- `01-product/` — the artifact contract, the variable model, the
  setup-and-refresh use case, the generated-plumbing/model split, and refusals.
- `02-architecture/` — module map, interface reduction, determinism.
- `03-implementation/` — per-module notes, C++ runtime, API facts.
- `04-verification/` — test levels, consistency gate, oracles, fixtures.
- `05-operation/` — setup, the implementer's build, and release.
- `06-evolution/` — candidate improvements and upstream gaps.
- the decision archive (`docs/archive/archive.zip`) — dated decision stream,
  history only, read via `pb archive`.

## Boundary Rule

A document's home is the layer whose question it answers; information flows
downward only. Current state lives in layer leaves, history in the decision
archive, and tracking in the generated registers. This file indexes current
state only.

- Read top-down: intent, product, architecture, implementation, verification,
  operation.
- Cite other nodes by ID, never by path.
- Evolution holds candidates only; it never restates current state.

## Excludes

- Runnable fixtures and goldens: `tests/fixtures/`, `tests/golden/`.
- Generated builds: `build/` and `/tmp`.
- Sibling libraries: `pyssp_standard`.
