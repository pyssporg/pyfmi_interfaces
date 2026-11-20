# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add `user_data` to the generated instance struct plus two model hooks,
  `<stem>_model_reset` (from `fmi2Reset`, before the instance fields are
  cleared) and `<stem>_model_free` (from `fmi2FreeInstance`), so implementer
  state survives a reset and is released on free; the hooks header and the
  model template carry all five bodies.
- Generate a C++17 FMI 2.0 CoSimulation runtime per exported component with
  `pyfmi c-runtime`: `<stem>_fmi.cpp`, a regenerated `<stem>_hooks.h`, a
  once-only `<stem>_model.cpp` implementer seam, and copies of the bundled FMI
  2.0 headers under `fmi2/`.
- Add `--omit` to `c-runtime`, which drops the named FMI entry points and leaves
  a marker for an implementer-supplied definition.
- Generate a `<Name>_Interface` partial model per exported component, carrying
  the parameters with their authored values and one connector instance per port.
- Generate `<Name>.mo`, the implementer-owned model that extends the partial
  model; created once and never rewritten. `package.order` lists both.
- Add `tests/iterative/`, an executable walkthrough that renames a port,
  regenerates in place, and shows the build failing at the model line; run as a
  slow test.
- Add `--component NAME` to `c-headers` and `c-runtime` (API:
  `generate_c_headers(..., component=None)` and
  `generate_c_runtime(..., component=None)`) to emit one exported component plus
  the common header; an unknown name raises `KeyError`.

### Changed

- Read the FMI `DefaultExperiment` from the composition's typed experiment
  container (`Experiment` / `DefaultExperiment`) instead of the retired
  `pyssp_default_start_time` / `pyssp_default_stop_time` tags; `stepSize` is
  emitted when the container declares one. Bumps to 0.3.0 with the dialect
  release it follows.
- Port fields are filtered by the dialect's `classify_attribute`: an attribute
  typed as FMU metadata, SSP metadata, a parameter set, or an experiment is
  authoring data, not a signal field.
- Split the package into artifact families (`c/`, `model_description/`,
  `modelica/`, `fmu/`) over the shared `core/` model, reduction, spelling, and
  identity code.
- `pyfmi package` now delegates to `pyssp_standard`'s `FMU` facade.
- The Modelica oracle now also checks each generated partial model and builds a
  hand-written model against it, because `checkModel` does not balance-check.

### Removed

- Drop the flat-connector refusal: flattening is export-time data, never model
  data, so this library has nothing to refuse.
- Remove the `pyssp_*` control-tag plumbing: the `core.CONTROL` and
  `FLAT_CONNECTOR_ATTR` imports, the control-name filters on ports and port
  fields, and the inline applied-set model literal (now the `applied` fixture).
- Drop the in-package FMU archive writer; packaging is owned by
  `pyssp_standard`.

### Fixed

- `--base-index` no longer offsets storage: generated C arrays stay zero-based
  with exactly `array` elements, and only the FMI element names and VR enum
  labels shift, so `base_index=1` indexes `gains[0]..[n-1]` instead of one past
  the end.

## [0.4.0] - 2026-11-20

### Added

- Restore the typed `Variable.start`: parameters keep their authored value and
  inputs their neutral `INPUT_START` value, while `Variable.start_text` remains
  the formatted FMI text. A `Reduction` therefore loses no start information.
- Add `Component.attributes` and `PortGroup.attributes`, carrying the authored
  part-definition and port-definition attributes as `(name, value)` pairs in
  declaration order, so a consumer never re-resolves the architecture.
- Add `Reduction.root`, the selected composition or system name, or `None` when
  no root was resolved.

### Changed

- A `Reduction` is now the complete parser-free generator input: package, root,
  typed starts, variables, and authored attributes cross the seam together.

### Fixed

- Typed start values and authored attributes are no longer discarded when a
  reduction crosses the library boundary.

## [0.2.0] - 2026-11-09

### Added

- Emit a `#define <UPPER_STEM>_GUID "{...}"` macro in every generated C
  component header, matching `modelDescription.xml`.
- Export a marked `FmuModel` definition directly, named by itself.

### Changed

- Thread `base_index` through field members, C headers, and the model
  description.
- Default `generation_time` to the fixed FMI epoch for reproducible output.
- Resolve export candidates by stored key; declare library imports in fixtures.
- Harden the ecosystem CI workflows and seed the `CHANGELOG.md`.

