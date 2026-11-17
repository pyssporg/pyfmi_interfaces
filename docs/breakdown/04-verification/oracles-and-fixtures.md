---
id: TEST-003
type: test
title: Oracles, fixtures, and goldens
summary: gcc and g++ syntax-check the headers, g++ compiles, links, and executes the runtime harness, fmpy validates and loads the packaged FMU, omc checkModel proves the Modelica package and buildModel the model seam, and six shared fixtures carry case records and byte-compared goldens.
date: 2026-11-17
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

Fixtures in `tests/fixtures/<subject>/<subject>.sysml` are the shared inputs:
`minimal` (scalar parameters and ports), `sensor` (String/Boolean, list
expansion), `controller` (parameters, `inout`, arrays), `bus` (second
composition shape, shared ports), `generator` (direct `:> FmuModel`), and
`packages` (two-root load, included parts; `test_package_roots.py`).

Each `case.md` records conversion, fault, level, input, expected, oracle, comparison, normalization, volatile fields, and update policy. Goldens live under
`tests/golden/<artifact>/<subject>/` for `c-headers`, `c-runtime`, `model-description`, `modelica`, `package`, `cross-artifact`.

Policy: no source-project name (`Aircraft`, `FuelSystem`, `FlightGearBridge`)
may appear in `src/` or a golden; a test enforces it. Names are configuration.
