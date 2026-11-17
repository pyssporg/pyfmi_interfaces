---
id: CP-004
type: capability
title: Set a model up for first use and keep it in step when its interface changes
summary: An implementer generates interfaces to start coding, then re-generates after a port or parameter change; success is artifacts and code agreeing without hand reconciliation.
date: 2026-11-17
status: current
---

# Set a model up for first use and keep it in step when its interface changes

The implementer asks: give me the interfaces my model must satisfy, and give
them to me again when the architecture's interface moves.

- **Actor:** the engineer writing and maintaining the implementation behind a
  SysML architecture.
- **Goal:** start from generated interfaces instead of a hand-copied variable
  list, and absorb an interface change without reconciling artifacts by hand.
- **Observable outcome:** after each change the generated artifacts and the
  implementation agree on variables, value references, and connector
  signatures, and the implementation compiles against them.
- **Where it fits:** the first generation is the starting contract (`CP-001`,
  `CP-002`); later consistency comes from regeneration and determinism
  (`INFO-004`), never from editing generated files.
- **Where it strains:** regeneration replaces generated files wholesale and
  merges no edits, so the implementer's code lives in the model file, which the
  generator creates once and never rewrites.
