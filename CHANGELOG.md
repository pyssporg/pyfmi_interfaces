# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Generate a `<Name>_Interface` partial model per exported component, carrying
  the parameters with their authored values and one connector instance per port.
- Generate `<Name>.mo`, the implementer-owned model that extends the partial
  model; created once and never rewritten. `package.order` lists both.
- Add `tests/iterative/`, an executable walkthrough that renames a port,
  regenerates in place, and shows the build failing at the model line; run as a
  slow test.

### Changed

- The Modelica oracle now also checks each generated partial model and builds a
  hand-written model against it, because `checkModel` does not balance-check.

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

