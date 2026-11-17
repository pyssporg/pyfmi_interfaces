# Case: `modelica/bus`

One inout port and one definition used both `in` and `out`: the bus is the case
that decides what a connector may claim about direction.

- **Conversion:** `bus.sysml` (SysML v2) → `GeneratedInterfaces/package.mo`,
  `GeneratedInterfaces/package.order`, `GeneratedInterfaces/Interfaces.mo`,
  `GeneratedInterfaces/GeneratedInterfaces.mo`,
  `GeneratedInterfaces/Bus_Interface.mo`, `GeneratedInterfaces/Bus.mo`
- **Requirement / fault:** a connector is a type, so a port definition used from
  more than one side cannot carry a single member direction. Emitting `input `
  for `Orientation` (used `in`, `out`, and `inout`) or for `Position` (used `in`
  and `out`) compiles but lies about the signal direction on one side, and a
  Modelica model that connects the wrong half then looks correct.
- **Level:** component
- **Input:** `tests/fixtures/bus/bus.sysml` (package `Bus`, composition
  `BusComposition`); no external source, no licence obligation
- **Expected:** the committed files listed under *Artifacts*
- **Independent oracle:** `omc`, the OpenModelica compiler — `loadFile` on
  `package.mo` plus `checkModel` on both subpackages and on the generated
  `Bus_Interface` partial model (three successful checks). This case was
  verified with `OpenModelica 1.26.1` (`/usr/bin/omc`). The generator is this
  repository; the parser and checker are not.
- **Comparison:** exact bytes against the committed file, plus the `omc` gates in
  `tests/test_modelica.py::test_openmodelica_accepts_the_generated_packages` and
  `tests/test_modelica.py::test_openmodelica_builds_hand_written_logic_against_the_partial`
  (a hand-written model extending the partial must build; the untouched scaffold
  must fail with `Too few equations`)
- **Normalization:** none; the writer is a pure function of the parsed
  architecture and its arguments, with no clock, hash seed, or environment input
- **Volatile fields:** none
- **Update policy:** `UPDATE_GOLDENS=1`, read the diff, commit fixtures and
  goldens together; refused when `CI` is set
- **Notes:** `Actuation` (all `in`) keeps `input `, `StatusPacket` (all `out`)
  keeps `output `, and the two mixed definitions emit bare members. `Integer`
  direction is visible in `StatusPacket.health`. The `omc` gate is marked `slow`
  (about 1 s, one `omc` invocation each); the text golden above is
  the default CI gate.

## Artifacts

Generated from `tests/fixtures/bus/bus.sysml`; every artifact path is relative
to this directory.

| Path | Kind |
| --- | --- |
| `GeneratedInterfaces/package.mo` | root package with the `Modelica` uses annotation |
| `GeneratedInterfaces/package.order` | `Interfaces`, `GeneratedInterfaces`, then per component `Bus_Interface` and `Bus` |
| `GeneratedInterfaces/Interfaces.mo` | eight primitive input/output connector aliases |
| `GeneratedInterfaces/GeneratedInterfaces.mo` | one connector per port definition |
| `GeneratedInterfaces/Bus_Interface.mo` | generated `partial model` — parameters and connector instances |
| `GeneratedInterfaces/Bus.mo` | implementer-owned `model`, created once, never rewritten |

`case.md` is provenance, not a golden.

## What this case proves

If this case is deleted, a regression that prefixes every connector with the
first usage's direction escapes: the controller, minimal, and sensor fixtures
each use a definition one way (or, in `minimal`, without an `inout` port), so
they would still pass. Here the mixed and `inout` definitions are the contract.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case added with the generator | U3.4: Modelica interface package |
| 2026-11-17 | Modelica seam: generated partial model and implementer-owned model | Iterative model development: interface generated, logic hand-written |
