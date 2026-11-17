---
id: INFO-008
type: info
title: FMU packaging
summary: pyfmi_sysml2 has no packaging module; pyssp_standard's FMU.stage and FMU.package own layout, validation, staging, archive verification, and determinism, and the CLI calls FMU.package directly.
date: 2026-11-17
status: current
---

# FMU packaging

`pyfmi_sysml2` keeps no packaging module and no wrapper functions. Packaging
lives in `pyssp_standard`'s `FMU` facade, and the `pyfmi package` command in
`fmu/__init__.py` calls `FMU.package` directly:

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

Policy lives at the point of emission, not in a library wrapper: the CLI's
`--platform` argument accepts only `linux64` (argparse `choices`, default
`linux64`), and it passes `fmi_version="2.0"` so the facade rejects other
versions. A direct Python caller imports `FMU` from `pyssp_standard` and chooses
its own platform token and version.

`FMU.stage` owns layout and validation: it gates the description on FMI 2.0,
checks `modelIdentifier` against the binary stem, expands directory entries,
refuses duplicate names, places every group, and sets the binary's executable
bit. `FMU.package` owns staging (temporary unless `stage_dir` is given) and
verifies that `modelDescription.xml` sits at the root and the binary under
`binaries/<platform>/`.

Determinism stays with `package_archive`: FMI epoch timestamps, sorted entries,
`0o644` metadata modes, and `0o755` under `binaries/`.
