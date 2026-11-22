---
id: INFO-012
type: info
title: Local setup
summary: Create a venv with Python 3.11 or newer, install the editable package with the dev extra, and use that interpreter for every command.
date: 2026-11-19
status: current
---

# Local setup

The checkout ships no `venv`; create one per checkout:

```bash
python3 -m venv venv
./venv/bin/pip install -e ".[dev]"
```

The two runtime dependencies are direct-URL wheels, not index lookups:

- `pycps-sysml2` v0.3.0, the SysML dialect whose experiment and attribute
  classification API the code reads;
- `experimental-pyssp-standard` v0.9.4.dev0, the FMI XML and archive API.

They come from `github.com/pyssporg/<repo>/releases/download/v<version>/` assets,
so bump the pin only after the sibling wheel exists; an unreleased tag breaks.

Commands:

```bash
./venv/bin/pyfmi --help
./venv/bin/ruff check src tests
./venv/bin/python -m pytest -m "not slow"
./venv/bin/python -m pytest            # includes the omc oracle
```

`UPDATE_GOLDENS=1 ./venv/bin/python -m pytest` rewrites goldens locally; it has
no effect when `CI` is set. Review the diff before committing a golden.

The editable install provides the `pyfmi` console script; otherwise run `PYTHONPATH=src ./venv/bin/python -m pyfmi_interfaces.cli`.
