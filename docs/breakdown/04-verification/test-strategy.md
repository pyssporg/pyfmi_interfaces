---
id: TEST-001
type: test
title: Test strategy
summary: Six pytest markers, five levels plus a slow qualifier; each owns a distinct fault class, the component level covers modelDescription, headers, the C++17 runtime, the Modelica package, and the packed .fmu, and goldens are the default gate.
date: 2026-11-17
status: current
---

# Test strategy

The suite is organized by the question a test answers, not by module. The six
markers are declared in `pyproject.toml`:

- **static** — a rule that holds without running the package: layering, family
  isolation, CLI registration matching the family directories, dependency
  shape, fixture records, provenance, and the parser-free rule (no module
  imports `pycps_sysml2`) (`test_layering.py`, `test_fixture_policy.py`).
- **unit** — one object's behaviour, no artifact written. The reduction is
  asserted through `pyfmi_interfaces.core` inside the artifact tests.
- **component** — a generated artifact is the unit under test: the bytes of
  `modelDescription.xml`, a C header, a C++17 runtime source, a Modelica
  package, or a packed `.fmu`; the runtime also compiles, links, and executes
  its harness.
- **contract** — two directions must agree: the value-reference enum between
  XML and header, one component identity across XML, header, and archive, and a
  generator run from a `Reduction` producing the same bytes with the dialect
  import blocked (`test_cross_artifact.py`, `test_reduction_inputs.py`).
- **system** — the CLI end to end: parsing, exit codes, files written by one
  `pyfmi` invocation; the packaged FMU is also built and loaded by fmpy
  (`test_cli.py`, `test_fmpy_load.py`).
- **slow** — not a level but an orthogonal qualifier that keeps the `omc`
  check out of the default subset.

Default gate: `python -m pytest -m "not slow"`. CI runs exactly that on 3.11 and
3.12, plus `ruff check src tests`, and fails if the checkout is dirty afterwards.

Goldens are compared byte-for-byte. `UPDATE_GOLDENS=1` rewrites them locally,
but never when `CI` is set: a golden is a reviewed artifact, not test output.
`tests/README.md` maps each marker to its files and the fault it can see.
