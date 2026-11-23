---
id: INFO-019
type: info
title: Iterative development example
summary: tests/iterative/run.sh generates the Modelica interface, adds the model logic, renames a port, and shows the build failing at the model line; tests/test_iterative_example.py runs it as a slow system test.
date: 2026-11-17
status: current
---

# Iterative development example

`tests/iterative/` is the generator's loop made executable: three revisions
of one hand-built reduction, one hand-written model, and a script that checks
each outcome. `omc` is driven from the script, never by `pyfmi`.

The script runs four stages in a temporary directory:

1. generate from the v1 reduction, copy `logic.mo` over the scaffold, build — passes;
2. regenerate from the v2 reduction, which renames the input port `raw` to
   `command`, in the same directory — the checksum of `Scaler.mo` is unchanged
   and `buildModel` fails with `Variable raw.value not found in scope Scaler` at
   the model's own line;
3. rename `raw.value` to `command.value` in the model — builds again, proving
   the fix is local to the implementer's file;
4. regenerate from the v3 reduction, which adds the output member `clipped` — the
   build fails with `Too few equations, under-determined system` and names
   `limited.clipped`.

Stage 2 is the point: the generated half is replaced whole, the hand-written
model is not, and the failure is a named symbol at a line, not a silent
renumbering. Stage 4 shows the structural change a name check cannot catch; the
balance check does.

`tests/test_iterative_example.py` runs the script as a `system`/`slow` test, so
the example cannot rot into prose. It skips when `omc` is absent and resolves
the `pyfmi` console script next to the test interpreter.
