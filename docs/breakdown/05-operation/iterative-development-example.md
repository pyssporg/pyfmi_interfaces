---
id: INFO-019
type: info
title: Iterative development example
summary: tests/iterative/run.sh generates the interface, adds the model logic, renames a port, and shows the build failing at the model line; a slow test runs it.
date: 2026-11-17
status: current
---

# Iterative development example

`tests/iterative/` is the generator's loop made executable: three revisions
of one architecture, one hand-written model, and a script that checks each
outcome. It is the only place in the repository where a build command is part of
the artifact: `omc` is driven from the script, never by `pyfmi`.

The script runs four stages in a temporary directory:

1. generate from `v1.sysml`, copy `logic.mo` over the scaffold, build — passes;
2. regenerate from `v2.sysml`, which renames the input port `raw` to
   `command`, in the same directory — the checksum of `Scaler.mo` is unchanged
   and `buildModel` fails with `Variable raw.value not found in scope Scaler` at
   the model's own line;
3. rename `raw.value` to `command.value` in the model — builds again, proving
   the fix is local to the implementer's file;
4. regenerate from `v3.sysml`, which adds the output member `clipped` — the
   build fails with `Too few equations, under-determined system` and names
   `limited.clipped`.

Stage 2 is the point: the generated half is replaced whole, the hand-written
model is not, and the failure is a named symbol at a line, not a silent
renumbering. Stage 4 shows the structural change a name check cannot catch; the
balance check does.

`tests/test_examples.py` runs the script as a `system`/`slow` test, so the
example cannot rot into prose. It skips when `omc` is absent and resolves the
`pyfmi` console script next to the test interpreter.
