---
id: INFO-018
type: info
title: Non-goals
summary: Model Exchange, FMI 3.0, non-linux64 platforms, authoring attributes, model physics, a build step, a Modelica FMU wrapper, placeholder completeness, and artifact patching.
date: 2026-11-17
status: current
---

# Non-goals

The package refuses work that belongs to the implementer, the dialect, or
another release.

- FMI Model Exchange and FMI 3.0.
- Binary platforms other than `linux64`.
- FMI authoring attributes: guid policy, modelName override, capabilities,
  units, declared variability or initial.
- Model physics: equations, state integration, event handling, and a runtime
  that is correct for a specific model. The generated runtime is plumbing, and
  its default step fails until the implementer writes the model (`CP-005`).
- Compiling generated sources, emitting a build system, or producing the FMU
  binary.
- A Modelica wrapper around a compiled FMU.
- Presenting generated placeholders as a complete FMU implementation.
- Patching, merging, or diff-aware rewriting of a generated surface; generated
  files are replaced whole, and the implementer's model file is created once
  and never rewritten.
