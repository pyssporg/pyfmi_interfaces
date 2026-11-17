---
id: INFO-015
type: info
title: C++ runtime generation and model hooks
summary: c/runtime.py writes a C++17 runtime plus hooks, copies the bundled FMI headers, and creates the model file once; --omit removes chosen function bodies.
date: 2026-11-17
status: current
---

# C++ runtime generation and model hooks

`c/runtime.py` writes the C++17 runtime that the C headers in `c/headers.py`
describe.

- **Inputs:** the same reduction as the other generators; parameters and ports
  come from the one variable set (`CP-002`).
- **Outputs:** `<stem>_fmi.cpp`, `<stem>_hooks.h`, `<stem>_model.cpp` (created
  only when absent), and byte copies of the three bundled FMI headers under
  `fmi2/`; the command also rewrites the headers it includes.
- **Runtime:** one private handle per instance holds the C++ `Instance`,
  callbacks, logging flag, lifecycle phase, and last successful time; get/set
  validate the whole batch before writing (`CP-005`).
- **Hooks:** `model_initialize`, `model_do_step`, `model_terminate`, C linkage;
  the created model file returns `fmi2OK` from initialize and terminate and
  `fmi2Error` from do-step until the implementer writes it.
- **`--omit`:** a repeatable or comma-separated list of `fmi2*` names; omitted
  definitions are not emitted and a banner names them, so the link fails until
  another object supplies them.
- **Determinism:** identical inputs produce identical bytes; no clock, no
  absolute paths.
- **No build:** the generator never invokes a compiler or writes a build file
  (`INFO-016`).
