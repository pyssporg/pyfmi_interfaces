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
- **The model seam is a file, not an edit.** Model behaviour is three hooks in a
  file created once and never rewritten; an interface change regenerates
  everything else and leaves it alone (`CP-004`).
