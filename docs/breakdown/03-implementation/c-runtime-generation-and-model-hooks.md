---
id: INFO-015
type: info
title: C++ runtime generation and model hooks
summary: c/runtime.py writes a C++17 FMI 2.0 CoSimulation runtime with 38 entry points and a five-hook model seam plus implementer-owned user_data, regenerates the C headers, copies the FMI headers, and creates the model file once.
date: 2026-11-17
status: current
---

# C++ runtime generation and model hooks

`generate_c_runtime()` regenerates the C headers, then per exported component
writes `<stem>_fmi.cpp` and `<stem>_hooks.h` (regenerated) plus
`<stem>_model.cpp` (created once, never rewritten), and copies the three FMI
headers into `<out>/fmi2/`. `--component NAME` keeps one component (unknown
name: `KeyError`). The runtime is C++17, C linkage, 38 entry points.

- **Stubs:** nine return `fmi2Error`: the six FMU-state/serialization
  functions, `fmi2GetDirectionalDerivative`, and both real derivative calls.
- **Status:** integer/string status always error, real status only
  `fmi2LastSuccessfulTime`, boolean only `fmi2Terminated`.
- **Hooks:** five, C linkage, each taking `<stem>_Instance*`:
  `<stem>_model_initialize`, `<stem>_model_do_step` (`fmi2Real`, `fmi2Real`),
  `<stem>_model_terminate`, `<stem>_model_reset`, and `<stem>_model_free`. The
  default step returns `fmi2Error`; the other four return `fmi2OK`.
- **Call sites:** `fmi2ExitInitializationMode` initialize, `fmi2DoStep`
  do_step, `fmi2Terminate` terminate; `fmi2Reset` reset before the fields are
  cleared, status propagated, `user_data` kept; `fmi2FreeInstance` free before
  the delete, status ignored; `<stem>_model.cpp` holds all five bodies, reset
  and free as no-ops.
- **user_data:** last `<stem>_Instance` field, `void* user_data = nullptr;`,
  implementer-owned, never read or written by the runtime; `fmi2Reset` keeps
  it and `model_free` releases it.
- **Handle:** one private handle holds the model `Instance`, callbacks, logging
  flag, phase, and times; get/set validate the batch before writing (`CP-005`).
- **`--omit`:** repeatable or comma-separated `fmi2*` names; omitted
  definitions leave a banner, and an unknown name is a `ValueError`.
- **Determinism and build:** identical inputs produce identical bytes; the
  generator never invokes a compiler or writes a build file (`INFO-016`).
