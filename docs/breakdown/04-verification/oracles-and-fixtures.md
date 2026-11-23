---
id: TEST-003
type: test
title: Oracles, fixtures, and goldens
summary: gcc and g++ syntax-check the headers, g++ compiles, links, and executes the runtime harness, fmpy validates and loads the packaged FMU, omc checkModel proves the Modelica package and buildModel the model seam, and hand-built reductions are the shared inputs with byte-compared goldens.
date: 2026-11-19
status: current
---

# Oracles, fixtures, and goldens

Oracles are external, independent of the writers, and skip with a stated reason:

- `gcc` — `-std=c11 -fsyntax-only` on the common header; `g++` —
  `-std=c++17 -fsyntax-only` on the instance helper;
- `g++` — compiles and links the generated runtime with its model file and
  the test harness, then executes it: GUID rejection, VR round-trips, type and
  writability refusals, step status, last successful time;
- `fmpy` — validates every modelDescription with its own FMI 2.0 checks, then
  loads a packaged `.fmu`, sets inputs, steps it, and reads outputs;
- `omc` — `checkModel` on both subpackages and each `partial model`, then
  `buildModel` twice: a model extending the partial builds, the untouched
  scaffold fails `Too few equations`. Marked slow.

`checkModel` accepts a model with no equations, so the seam is proven with
`buildModel`.

Tests construct their `Reduction` inputs by hand: a component with scalar
parameters and ports, String/Boolean and list expansion, `inout` and arrays, a
second shared-port shape, a direct FMU model, and multi-component selections.

Each `case.md` records conversion, fault, level, input, expected, oracle, comparison, normalization, volatile fields, and update policy. Goldens live under
`tests/golden/<artifact>/<subject>/`.

Policy: no example-specific project name (`Aircraft`, `FuelSystem`,
`FlightGearBridge`) may appear in `src/` or a golden. Names are configuration.
