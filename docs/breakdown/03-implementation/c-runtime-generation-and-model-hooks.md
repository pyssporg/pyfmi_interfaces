---
id: INFO-015
type: info
title: C++ runtime generation and model hooks
summary: c/runtime.py writes a C++17 FMI 2.0 CoSimulation runtime with 38 entry points and a three-hook model seam, regenerates the C headers, copies the FMI headers, and creates the model file once.
date: 2026-11-17
status: current
---

# C++ runtime generation and model hooks

`generate_c_runtime()` regenerates the C headers through `generate_c_headers()`,
then per exported component writes `<stem>_fmi.cpp` (regenerated),
`<stem>_hooks.h` (regenerated), and `<stem>_model.cpp` (created once, never
rewritten). It copies `fmi2Functions.h`, `fmi2FunctionTypes.h`, and
`fmi2TypesPlatform.h` into `<out>/fmi2/`.

- **Runtime:** C++17 with C linkage; 38 entry points.
- **Stubs:** nine entry points return `fmi2Error`: `fmi2GetFMUstate`,
  `fmi2SetFMUstate`, `fmi2FreeFMUstate`, `fmi2SerializedFMUstateSize`,
  `fmi2SerializeFMUstate`, `fmi2DeSerializeFMUstate`,
  `fmi2GetDirectionalDerivative`, `fmi2SetRealInputDerivatives`,
  `fmi2GetRealOutputDerivatives`.
- **Status:** `fmi2GetIntegerStatus`/`fmi2GetStringStatus` always error;
  `fmi2GetRealStatus` supports only `fmi2LastSuccessfulTime`;
  `fmi2GetBooleanStatus` only `fmi2Terminated`.
- **Hooks:** `<stem>_model_initialize(<stem>_Instance*)`,
  `<stem>_model_do_step(<stem>_Instance*, fmi2Real, fmi2Real)`, and
  `<stem>_model_terminate(<stem>_Instance*)`, C linkage. Default initialize and
  terminate return `fmi2OK`; the default step returns `fmi2Error`.
- **State:** one private handle holds the model `Instance`, callbacks, logging
  flag, initialized/terminated phase, start time, last successful time, and
  last do-step status; get/set validate the whole batch before writing
  (`CP-005`).
- **`--omit`:** repeatable or comma-separated `fmi2*` names; omitted
  definitions are not emitted, a banner names them, and an unknown name is a
  `ValueError`.
- **Determinism and build:** identical inputs produce identical bytes; the
  generator never invokes a compiler or writes a build file (`INFO-016`).
