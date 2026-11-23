# pyfmi_interfaces

Generate FMI 2.0 CoSimulation artifacts from a parser-free interface model:
`modelDescription.xml`, C interface headers, a C++17 runtime with a model seam,
Modelica partial models and connectors, and a packaged `.fmu`.

**Library boundary.** This package is SysML-free. Every generator consumes a
`Reduction`; the SysML reader and the `to_reduction` bridge live in the
`pyfmi_sysml` composition layer, which imports `pycps_sysml2`. FMI XML is built,
serialized, and validated *only* through `pyssp_standard.standard.fmi2`. This
package must never depend on `pyssp_sysml2`: the artifact libraries are siblings,
not layers. What crosses to another project is the artifact — FMI XML, C headers,
C++ runtime sources, Modelica text, or the `.fmu` archive.
**This package does not build C/C++ code.** It writes sources; compiling,
linking, and producing the `.so` are the implementer's steps.

The distribution is `pyfmi-interfaces`; `import pyfmi_sysml2` remains a
deprecated compatibility shim that only re-exports the public surface for one
deprecation window. New code imports `pyfmi_interfaces`.

- Users: this file and `pyfmi --help`.
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

## CLI

`pyfmi` has one subcommand, `package`, which writes a deterministic `.fmu`
archive from an already generated `modelDescription.xml` and binary. Every
written path is printed on stdout. Handled input errors print `pyfmi: <message>`
on stderr and exit 1; argument errors keep argparse's exit 2.

```text
usage: pyfmi [-h] COMMAND ...
```

The four source-taking commands (`model-description`, `c-headers`, `c-runtime`,
`modelica`) live in `pyfmi_sysml` as `pyfmi-sysml`.

## Python API

The package exports four generator functions, `fmi2_headers`, the reduction
types (`Component`, `Variable`, `Reduction`), and `select_component(reduction,
name)`, which returns the named exported component or raises `ValueError`. Every
generator accepts a `Reduction` only:

```python
from pathlib import Path

import pyfmi_interfaces
from pyfmi_sysml import to_reduction

reduction = to_reduction(Path("architecture/plant.sysml"))

pyfmi_interfaces.generate_c_headers(reduction, Path("build"))
pyfmi_interfaces.generate_modelica(reduction, Path("build"))
```

`generation_time=None` uses the fixed epoch `2000-01-01T00:00:00Z`; pass a
timezone-aware datetime for any other stamp. A naive datetime is refused.
`fmi2_headers()` returns the bundled FMI 2.0 standard headers as real file
paths. The `.fmu` archive is written by `pyssp_standard`'s `FMU` facade.

A `Reduction` has already fixed the composition and the array index base; pass
those to `pyfmi_sysml.to_reduction(...)` before calling a generator.
