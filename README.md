# pyfmi_interfaces

Generate FMI 2.0 CoSimulation artifacts from a hand-built interface
`Reduction`: `modelDescription.xml`, C interface headers, a C++17 runtime with a
model seam, Modelica partial models and connectors, and a packaged `.fmu`.

**Library boundary.** Every generator consumes a `Reduction` the caller
constructs. FMI XML is built, serialized, and validated *only* through
`pyssp_standard.standard.fmi2`. What crosses to another project is the artifact —
FMI XML, C headers, C++ runtime sources, Modelica text, or the `.fmu` archive.
**This package does not build C/C++ code.** It writes sources; compiling,
linking, and producing the `.so` are the implementer's steps.

The distribution is `pyfmi-interfaces`; the old import name `pyfmi_sysml2` still
re-exports this package for one deprecation window. New code imports
`pyfmi_interfaces`.

- Users: this file, `examples/`, and `pyfmi --help`.
- Contributors: `AGENTS.md`, then `docs/breakdown/00-intent/intent.md`.
- Current contracts and design: `docs/breakdown/README.md`.

## Install

The runtime dependency is a direct-URL wheel pinned to a sibling GitHub release
(`experimental-pyssp-standard` v0.9.4.dev0), so the tag must exist before an
install resolves. `pyfmi_interfaces` is version 0.5.1 and requires Python 3.11
or newer.

```bash
python3 -m venv venv
./venv/bin/pip install -e ".[dev]"
```

From a built wheel, `pip install pyfmi_interfaces-<version>-py3-none-any.whl`
resolves the same URL.

## Quickstart

Construct the input yourself; no reader participates. The runnable version of
this block is `examples/build_reduction_artifacts.py`.

```python
from datetime import datetime, timezone
from pathlib import Path

from pyfmi_interfaces import (
    Component,
    Experiment,
    ExportIdentity,
    Reduction,
    Variable,
    generate_c_headers,
    generate_c_runtime,
    generate_model_description,
    generate_modelica,
)
from pyfmi_interfaces.core import Field, PortGroup

reduction = Reduction(
    components=(
        Component(
            name="Scale",
            doc=None,
            parameters=(Field("gain", "Real"),),
            ports=(
                PortGroup(
                    name="u",
                    definition="Signal",
                    direction="in",
                    causality="input",
                    fields=(Field("value", "Real"),),
                    doc=None,
                ),
                PortGroup(
                    name="y",
                    definition="Signal",
                    direction="out",
                    causality="output",
                    fields=(Field("value", "Real"),),
                    doc=None,
                ),
            ),
            variables=(
                Variable(
                    name="gain",
                    type_name="Real",
                    causality="parameter",
                    variability="fixed",
                    value_reference=0,
                    index=1,
                    description=None,
                    member="gain",
                    start=2.0,
                    start_text="2.0",
                ),
                Variable(
                    name="u",
                    type_name="Real",
                    causality="input",
                    variability=None,
                    value_reference=1,
                    index=2,
                    description=None,
                    member="u.value",
                    start=0.0,
                    start_text="0",
                ),
                Variable(
                    name="y",
                    type_name="Real",
                    causality="output",
                    variability=None,
                    value_reference=2,
                    index=3,
                    description=None,
                    member="y.value",
                ),
            ),
        ),
    ),
    identity=ExportIdentity("Root", False),
    package="Demo",
    experiment=Experiment(start_time=0.0, stop_time=1.0, step_size=0.1),
    root="Root",
)

out = Path("build")
generate_model_description(
    reduction,
    out / "model-description",
    generation_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
)
generate_c_headers(reduction, out / "c")
generate_c_runtime(reduction, out / "runtime")
generate_modelica(reduction, out / "modelica")
```

Every generator takes the `Reduction` first and an output directory second.
`generation_time=None` uses the fixed epoch `2000-01-01T00:00:00Z`; pass a
timezone-aware datetime for any other stamp, and a naive datetime is refused.
`fmi2_headers()` returns the bundled FMI 2.0 standard headers as real file
paths. `select_component(reduction, name)` returns the named exported component
or raises `ValueError`.

A `Reduction` already fixes the exported components, the naming rule, and each
field's array index base; construct those once and pass the same object to every
generator. The `.fmu` archive is written by `pyssp_standard`'s `FMU` facade,
exposed here as the `pyfmi package` command.

## CLI

`pyfmi` has one subcommand, `package`, which writes a deterministic `.fmu`
archive from an already generated `modelDescription.xml` and binary. Every
written path is printed on stdout. Handled input errors print `pyfmi: <message>`
on stderr and exit 1; argument errors keep argparse's exit 2.

```text
usage: pyfmi [-h] COMMAND ...

pyfmi package -o OUT --model-description PATH --binary PATH \
    [--platform linux64] [--header PATH] [--resource PATH] [--documentation PATH]
```

The four generators are Python functions; `pyfmi` only packages. See
`examples/` for a complete build-then-package walkthrough.
