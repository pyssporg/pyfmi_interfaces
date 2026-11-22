# AGENTS

## Vision first (required)

Before you read code, edit files, or plan a change, read the project vision:

**`docs/breakdown/00-intent/intent.md`**

It states why this repository exists. The binding rules are
`docs/breakdown/00-intent/commitments.md` and the refusals are
`docs/breakdown/00-intent/non-goals.md`. Together they are the first documents
to read, not references of last resort.

- Read it in full before making any change to code, tests, docs, or artifacts.
- Judge every proposed change against it. If a change conflicts with the vision,
  its commitments, goals, or non-goals, stop and surface the conflict; do not
  implement it silently.
- If the work shows the long-term direction is wrong, change the vision
  deliberately first, then the code. Never let the repository drift away from
  its stated intent.

## Rules

1. **Don't assume. Surface tradeoffs.** If a contract is ambiguous, stop and say
   so rather than picking a behaviour silently.
2. **Minimum code that solves the problem.** Nothing speculative.
3. **Touch only what you must.** Clean up only your own mess.
4. **Define success criteria and verify.**

## Repository Focus

`pyfmi_interfaces` generates FMI 2.0 CoSimulation artifacts from a parser-free
interface `Reduction`: `modelDescription.xml`, C interface headers, a C++17
runtime with a five-hook model seam, Modelica connectors with a partial-model
implementer seam, and a packaged `.fmu`. The artifact is the library boundary;
the `pyfmi` CLI, four generator functions, and `fmi2_headers` are the public
surface.

- This package is parser-free. The SysML dialect and the `Reduction`
  construction live in the `pyfmi_sysml` composition layer, which reads through
  `pycps_sysml2`; this package implements the FMI half of the contract.
- FMI XML is owned by `pyssp_standard.standard.fmi2`; this package maps the
  reduction onto it.
- The `pyfmi_sysml2` import name is a deprecated compatibility shim: it only
  re-exports this package and retires after the stated window. New code imports
  `pyfmi_interfaces`.
- The code is one `core/` package plus one subpackage per artifact family
  (`c/`, `model_description/`, `modelica/`, `fmu/`), plus the bundled
  `fmi2_headers/`. A family imports `core/` only and never another family; only
  the facade and `cli.py` import families.
- Packaging is upstream: `pyfmi package` delegates to `pyssp_standard`'s `FMU`
  facade, and `fmu/` only binds the command line to it.
- Current state, contracts, and design rationale live in `docs/breakdown/`; the
  code is the source of truth when the two disagree.

## Hard constraints

- **Never import a parser or `pyssp_sysml2`.** The two artifact libraries are
  siblings. `pycps_sysml2` is owned by `pyfmi_sysml`; every generator here
  consumes a parser-free `Reduction`, and SSP emission is not this repository's
  job.
- **Never hand-roll ElementTree for FMI XML.** Build, serialize, and validate
  through `pyssp_standard.standard.fmi2` (`Fmi2ModelDescriptionDocument`,
  `Fmi2ModelDescriptionXmlCodec`, `Fmi2ModelDescriptionValidator`).
- **Every artifact is reproducible from an injected `generation_time`.** The
  clock is a parameter, not an ambient read; a naive datetime is refused. The
  same architecture and clock produce byte-identical files, including the
  archive.
- **The built artifact is the unit under test.** Assertions run against the
  generated file or the packed `.fmu`, not against an intermediate string that
  the writer might not use.
- **One variable set.** Every generator reads the reduction and the spelling
  tables in `pyfmi_interfaces.core`; none re-derives variables, causalities, or
  value references, and none keeps a private type table.
- **Never build generated code.** The package writes C++ sources; it does not
  invoke a compiler, emit a build system, or package an unbuilt binary. Build
  commands live only in documentation examples and the test harness.
- **`linux64` only.** Do not widen the platform allow-list without a decision.

## Code guidelines

- Keep changes direct and explicit. Minimize duplication, but do not hide the
  document assembly behind abstractions.
- Prefer one subpackage per artifact family and one module per artifact; a
  generator returns the paths it wrote.
- Treat this as experimental software: interfaces need not be stable, and
  clarity outranks compatibility shims.
- Avoid thin wrappers unless they buy something substantial. A wrapper that only
  renames a library call is noise.
- Preserve user changes in a dirty worktree; never revert unrelated edits.

## Conventions

- `README.md` is the landing page for users; `AGENTS.md` is for contributors.
- Current state lives in `docs/breakdown/` leaves, in the present tense. Dated
  decisions live in `docs/archive/archive.zip`, read with `pb archive`; never
  add per-layer `decisions/` folders.
- Regenerate `docs/archive/README.md`, `design-choice-log.md`, and
  `traceability-map.md` with `pb registers`; never edit them by hand.
- Every fixture carries a `case.md` with the artifact, oracle, comparison, and
  update policy. Goldens are compared byte-for-byte; `UPDATE_GOLDENS=1`
  rewrites them locally and is ignored under `CI`.
- Keep docs aligned with the actual CLI, file layout, and dependency pins.

## Environment

- Python >= 3.11. No virtualenv is tracked; create one per checkout.
- Install: `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`. The
  runtime dependency is a direct-URL wheel pinned to a sibling GitHub release;
  SysML ingestion and its parser dependencies live in `pyfmi_sysml`.
- Tests: `.venv/bin/python -m pytest -q`; the CI subset is
  `.venv/bin/python -m pytest -m "not slow"`.
- Lint: `.venv/bin/ruff check src tests`.
- Oracles: `gcc`/`g++` syntax-check and link the C/C++ artifacts, `fmpy`
  validates the modelDescription and loads the packaged FMU, and `omc` checks
  the Modelica package; each skips with a reason when absent.
- Breakdown checks:
  `python3 <pb> check --strict --root docs/breakdown` and
  `python3 <pb> node-size --strict --root docs/breakdown`, where `<pb>` is the
  product-breakdown skill's `scripts/pb`.
