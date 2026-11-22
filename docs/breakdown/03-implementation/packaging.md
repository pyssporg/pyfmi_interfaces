---
id: INFO-008
type: info
title: FMU packaging
summary: pyfmi_interfaces has no archive writer and no local staging layer; pyssp_standard's FMU.stage and FMU.package own layout, validation, staging, archive verification, and determinism, and the CLI calls FMU.package directly.
date: 2026-11-17
status: current
---

# FMU packaging

`pyfmi_interfaces` has no archive writer and no local staging layer. Packaging
lives in `pyssp_standard`'s `FMU` facade; `fmu/__init__.py` only binds the
command line to it:

```python
FMU.package(
    args.output,
    model_description=args.model_description,
    binaries={args.platform: args.binary},
    sources=args.header,
    resources=args.resource,
    documentation=args.documentation,
    fmi_version="2.0",
)
```

Policy lives at the point of emission: `--model-description` and `--binary`
are required, and `--platform` accepts only `linux64` (argparse `choices`,
default `linux64`). Passing `fmi_version="2.0"` makes the facade reject other
versions. A direct Python caller imports `FMU` from `pyssp_standard` and chooses
its own platform token and version.

`FMU.stage` owns layout and validation: the FMI 2.0 gate, `modelIdentifier`
against each binary stem, directory expansion, duplicate-name refusal, group
placement, and the executable bit. `FMU.package` owns staging (temporary unless
`stage_dir` is given) and verifies `modelDescription.xml` at the root and the
binary under `binaries/<platform>/`.

Determinism stays with `package_archive`: FMI epoch timestamps, sorted entries,
`0o644` metadata modes, and `0o755` under `binaries/`.
