---
id: CP-005
type: capability
title: Generated FMI plumbing, implementer-supplied model
summary: The runtime implements every FMI 2.0 CoSimulation entry point from the variable set; equations and event logic stay in a model file the generator creates once.
date: 2026-11-17
status: current
---

# Generated FMI plumbing, implementer-supplied model

A consumer relies on the runtime covering the FMI 2.0 entry points and on owning
the model seam alone.

- **All entry points exist by default.** Every FMI 2.0 CoSimulation function the
  bundled headers declare is defined, in C++17 with C linkage (`INFO-015`).
- **Variables are generic.** Get/Set dispatch over the header's VR map, so
  bounds, data type, and writability come from the one variable set (`CP-002`).
- **Parameters follow the lifecycle.** Parameters are settable before
  initialization ends, inputs at any time, outputs never.
- **Unsupported features refuse.** FMU state, directional derivatives, and
  input/output derivatives return `fmi2Error`, and the modelDescription claims
  none of them.
- **The model seam is a file, not an edit.** `<stem>_model.cpp` defines five
  hooks declared in `<stem>_hooks.h`: `<stem>_model_initialize`,
  `<stem>_model_do_step`, `<stem>_model_terminate`, `<stem>_model_reset`
  (called from `fmi2Reset` before the fields clear, status propagated), and
  `<stem>_model_free` (called from `fmi2FreeInstance`, before the delete,
  status ignored). The generator creates it once with `TODO` bodies; the
  default step returns `fmi2Error` until implemented, and regeneration never
  rewrites the file (`CP-004`).
- **State is the implementer's.** `<stem>_Instance` ends with
  `void* user_data = nullptr;`, which the runtime never reads or writes, keeps
  across `fmi2Reset`, and leaves to `model_free` to release.
