---
id: INFO-010
type: info
title: pyssp_standard API facts
summary: The codec returns str, interface type and capabilities are both required, Boolean starts are text, ModelStructure indexes are 1-based, and package_archive normalizes modes and epoch.
date: 2026-11-05
status: current
---

# pyssp_standard API facts

These behaviours are relied on; a change in `pyssp_standard` shows up here
first.

- `Fmi2ModelDescriptionXmlCodec.serialize(document)` returns a `str`, not
  bytes. Write it with `encoding="utf-8"`; parse with `codec.parse(text)`.
- `Fmi2ModelDescriptionDocument` needs both `interface_type` and `capabilities`.
  The codec emits the `CoSimulation` element only when both are present, so
  setting one is a silent omission.
- Scalar `start` values are strings in FMI text form. A Boolean must be
  `"true"`/`"false"`; Python's `str(True)` (`"True"`) is invalid. The reduction
  formats through `pycps_sysml2.core.format_value`.
- `Fmi2ModelStructure` unknown `index` is the 1-based ScalarVariable position,
  not the 0-based `valueReference`. `Variable` carries both for this reason.
- `Fmi2ModelDescriptionValidator.validate(document, xml)` performs semantic and
  XSD checks. Call it before writing; it is not part of `serialize`.
- `pyssp_standard.common.archive.archive.package_archive(directory, output)`
  sorts entries, stamps the FMI epoch (2000-01-01), sets metadata modes `0o644`
  and `binaries/` modes `0o755`, and returns the archive path.
- `FMU.stage(directory, *, model_description, binaries=None, sources=None,
  resources=None, documentation=None, fmi_version=None, overwrite=False)`
  validates the description (version gate, interface, `modelIdentifier` against
  each binary stem), prepares the directory (non-empty without `overwrite`
  raises `FileExistsError`), expands directory entries recursively, refuses
  duplicate entry names, places every group, and sets the binary executable bit.
- `FMU.package(path, *, model_description, binaries=None, sources=None,
  resources=None, documentation=None, fmi_version=None, stage_dir=None)` stages
  into a temporary directory or `stage_dir`, calls `package_archive` with its
  defaults, and verifies `modelDescription.xml` at the root and every
  `binaries/<platform>/<name>`.
- `pyssp_standard.common.archive.fmu_layout.platform_component(platform)` is a
  path-safety check only; it carries no platform allow-list. `pyfmi_sysml2`
  keeps no wrapper either: its CLI pins the `linux64` token with argparse
  `choices` and passes `fmi_version="2.0"` at the call site.
- `Fmi2ModelDescriptionSemanticValidator.validate_binary(document, name)`
  checks `fmiVersion == "2.0"`, the presence of an interface, and that the
  `modelIdentifier` equals the binary stem.

`FMU.stage` and `FMU.package` are newer than the published wheel, so this
repository needs an editable sibling checkout of `experimental_pyssp_standard`
until the pin (`experimental-pyssp-standard` v0.9.3.dev0) carries them.
