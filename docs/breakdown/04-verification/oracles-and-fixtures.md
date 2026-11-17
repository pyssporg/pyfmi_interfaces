---
id: TEST-003
type: test
title: Oracles, fixtures, and goldens
summary: gcc and g++ syntax-check the headers, g++ compiles, links, and executes the generated runtime harness, fmpy validates and loads the packaged FMU, omc checkModel proves the generated Modelica package and buildModel proves the model seam, and six shared fixtures carry case records and byte-compared goldens.
date: 2026-11-05
status: current
---

# Oracles, fixtures, and goldens

External oracles, with the versions recorded on this machine:

- `gcc 13.4.0` — `-std=c11 -fsyntax-only` on the common header;
- `g++ 13.4.0` — `-std=c++17 -fsyntax-only` on the instance helper;
- `g++ 13.4.0` — compile and link the generated runtime with its model file
  plus the test harness, then execute the harness: GUID rejection, VR
  round-trips, type and writability refusals, step status, and last successful
  time;
- `fmpy 0.3.20` — reads and validates every fixture's modelDescription with its
  own FMI 2.0 checks, then loads a packaged `.fmu`, sets inputs, steps it, and
  reads outputs through its CoSimulation implementation;
- `omc OpenModelica 1.26.1` — `loadFile` plus `checkModel` on both generated
  subpackages and each generated `partial model`, then `buildModel` on one
  fixture twice: a hand-written model extending the partial must build, and the
  untouched scaffold must fail with `Too few equations`. Marked slow and skipped
  when `omc` is absent.

The compiler tests skip with a reason when the compiler is missing; they do not
silently pass. The omc check asserts zero `Error` text and three successful
`checkModel` calls per fixture. `checkModel` is not a balance check: it accepts
a model with no equations, which is why the seam is proven with `buildModel`.

Fixtures live in `tests/fixtures/<subject>/<subject>.sysml` and are the shared
architectures the goldens are built from:

- `minimal` — one component, scalar parameters and ports;
- `sensor` — String and Boolean fields, list expansion;
- `controller` — parameters, `inout` and mixed directions, array parameters;
- `bus` — a second composition shape and shared port definitions;
- `generator` — a direct `:> FmuModel` definition with no container root;
- `packages` — a two-root load where an included part definition with parts is
  used by the primary composition, and one bare name exists in both packages
  (asserted by `tests/test_package_roots.py`, no golden).

Every fixture directory carries a `case.md` with Conversion, Requirement /
fault, Level, Input, Expected, Independent oracle, Comparison, Normalization,
Volatile fields, Update policy, and Notes. Goldens live under
`tests/golden/<artifact>/<subject>/`.

Policy: no architecture-specific name from the source project may appear in
`src/` or in a golden (`Aircraft`, `FuelSystem`, `FlightGearBridge`); a test
enforces the ban. Names are configuration, not constants.
