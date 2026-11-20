# pyfmi_sysml2

Generate FMI 2.0 CoSimulation artifacts from a SysML v2 architecture:
`modelDescription.xml`, C interface headers, a C++17 runtime with a model seam,
Modelica partial models and connectors, and a packaged `.fmu`.

**Library boundary.** The SysML dialect is read *only* through
[`pycps_sysml2`](https://github.com/pyssporg/pycps_sysml2); FMI XML is built,
serialized, and validated *only* through `pyssp_standard.standard.fmi2`. This
package must never depend on `pyssp_sysml2`: the two artifact libraries are
siblings, not layers. What crosses to another project is the artifact — FMI XML,
C headers, C++ runtime sources, Modelica text, or the `.fmu` archive.
**This package does not build C/C++ code.** It writes sources; compiling,
linking, and producing the `.so` are the implementer's steps.

- Users: this file and `pyfmi --help`.
- Contributors: `AGENTS.md`, then `docs/breakdown/00-intent/intent.md`.
- Current contracts and design: `docs/breakdown/README.md`.

## Install

The two runtime dependencies are direct-URL wheels pinned to sibling GitHub
releases (`pycps-sysml2` v0.3.0 and `experimental-pyssp-standard`
v0.9.4.dev0), so the tags must exist before any install resolves.
`pyfmi_sysml2` is version 0.2.0 and requires Python 3.11 or newer.

The checkout does not ship a virtual environment; create one. From a checkout:

```bash
python3 -m venv venv
./venv/bin/pip install -e ".[dev]"
```

From a built wheel, `pip install pyfmi_sysml2-<version>-py3-none-any.whl`
resolves the same two URLs. Both dependencies are immutable release assets, not
index lookups.

## Examples

`examples/` holds runnable, standalone walkthroughs, each with its own SysML
input: FMI XML from the CLI, a Modelica package with the implementer seam, and
a C++ runtime compiled, packed, and loaded as an `.fmu`. Generated output stays
under `build/` (gitignored). Start at [`examples/README.md`](examples/README.md).

## CLI

`pyfmi` has five subcommands: four generators (`model-description`,
`c-headers`, `c-runtime`, `modelica`) and the `package` command. The four
generators default to `build/`. `c-headers` and `c-runtime` accept
`--component NAME` to emit one exported component plus the common header.
`pyfmi package` requires an output path. Every written path is printed on
stdout, one per line. Handled model or input errors print `pyfmi: <message>` on
stderr and exit 1; argument errors keep argparse's exit 2.

### `pyfmi --help`

```text
usage: pyfmi [-h] COMMAND ...

Generate FMI 2.0 CoSimulation artifacts from a SysML v2 architecture.

positional arguments:
  COMMAND
    model-description
                     Write modelDescription.xml per component.
    c-headers        Write C interface headers.
    c-runtime        Write the C headers and a C++17 FMI runtime.
    modelica         Write a Modelica interface package.
    package          Write a deterministic .fmu archive.

options:
  -h, --help         show this help message and exit

Generators write to build/ unless -o/--output is given; pyfmi package requires
an output archive path.
```

### `pyfmi model-description --help`

```text
usage: pyfmi model-description [-h] [-o OUT] [--composition NAME]
                               [--base-index N] [--component NAME]
                               [--generation-time ISO8601]
                               SOURCE

Write modelDescription.xml per component to an output directory.

positional arguments:
  SOURCE                A .sysml file or a directory containing them.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory (default: build).
  --composition NAME    Composition part definition to export (default: the
                        single root).
  --base-index N        First emitted array index (default: 0; 1 targets OMC-
                        built Modelica FMUs, which declare arrays one-based).
  --component NAME      Restrict the output to one exported component.
  --generation-time ISO8601
                        Fixed generationDateAndTime, for example
                        2026-01-01T00:00:00Z (default: 2000-01-01T00:00:00Z,
                        the fixed epoch).
```

An omitted generation time is the fixed epoch `2000-01-01T00:00:00Z`, so repeated
runs are byte-identical. The option accepts `2026-01-01T00:00:00Z` or an ISO
8601 form with an explicit offset; a naive time is refused with exit 2.

### `pyfmi c-headers --help`

```text
usage: pyfmi c-headers [-h] [-o OUT] [--composition NAME] [--base-index N]
                       [--component NAME] [--prefix NAME]
                       SOURCE

Write the C interface headers to an output directory.

positional arguments:
  SOURCE                A .sysml file or a directory containing them.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory (default: build).
  --composition NAME    Composition part definition to export (default: the
                        single root).
  --base-index N        First emitted array index (default: 0; 1 targets OMC-
                        built Modelica FMUs, which declare arrays one-based).
  --component NAME      Restrict the output to one exported component.
  --prefix NAME         Header prefix and C type prefix (default: the package
                        name).
```

### `pyfmi c-runtime --help`

```text
usage: pyfmi c-runtime [-h] [-o OUT] [--composition NAME] [--base-index N]
                       [--component NAME] [--prefix NAME]
                       [--omit NAME[,NAME...]]
                       SOURCE

Write the C interface headers, a C++17 FMI 2.0 CoSimulation runtime, and a
user-owned model file to an output directory.

positional arguments:
  SOURCE                A .sysml file or a directory containing them.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory (default: build).
  --composition NAME    Composition part definition to export (default: the
                        single root).
  --base-index N        First emitted array index (default: 0; 1 targets OMC-
                        built Modelica FMUs, which declare arrays one-based).
  --component NAME      Restrict the output to one exported component.
  --prefix NAME         Header prefix and C type prefix (default: the package
                        name).
  --omit NAME[,NAME...]
                        Skip the definition of an FMI function and leave a
                        marker; repeatable and comma-separated.
```

`c-runtime` regenerates the C interface headers first, so `c-headers` need not
run before it. `--component NAME` restricts either C command to one exported
component plus the common header; an unknown name exits 1.
`<Prefix>_<Component>_model.cpp` is created once and never rewritten. Every
other generated file, including the C++ runtime and the hooks header, is
replaced on each run. `--omit` exists for an implementer who supplies their own
definition: the file keeps a marker naming the missing function and the link
fails until that definition is provided.

### `pyfmi modelica --help`

```text
usage: pyfmi modelica [-h] [-o OUT] [--composition NAME] [--package NAME]
                      [--within NAME]
                      SOURCE

Write the Modelica interface package to an output directory.

positional arguments:
  SOURCE                A .sysml file or a directory containing them.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory (default: build).
  --composition NAME    Composition part definition to export (default: the
                        single root).
  --package NAME        Root Modelica package name (default:
                        GeneratedInterfaces).
  --within NAME         Enclosing Modelica scope for the root package.
```

### `pyfmi package --help`

```text
usage: pyfmi package [-h] -o OUT --model-description PATH --binary PATH
                     [--platform NAME] [--header PATH] [--resource PATH]
                     [--documentation PATH]

Write a deterministic .fmu archive to the output path.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output .fmu archive path (required).
  --model-description PATH
                        FMI 2.0 modelDescription.xml for the archive root.
  --binary PATH         Built shared library; its stem must be the
                        modelIdentifier.
  --platform NAME       Platform directory under binaries/ (default: linux64).
  --header PATH         Generated header to include under sources/
                        (repeatable).
  --resource PATH       File or directory to include under resources/
                        (repeatable).
  --documentation PATH  File or directory to include under documentation/
                        (repeatable).
```

Example:

```bash
pyfmi model-description architecture/plant.sysml -o build \
  --generation-time 2026-01-01T00:00:00Z
pyfmi c-runtime architecture/plant.sysml -o build
pyfmi modelica architecture/plant.sysml -o build

# Your build step, not part of pyfmi. The library never compiles.
g++ -std=c++17 -shared -fPIC -Ibuild -Ibuild/fmi2 \
  build/Plant_Tank_fmi.cpp build/Plant_Tank_model.cpp -o build/Tank.so

pyfmi package build/Plant.fmu \
  --model-description build/Tank/modelDescription.xml \
  --binary build/Tank.so \
  --header build/Plant_InterfaceCommon.h
```

## Python API

The package exports four generator functions, `fmi2_headers`, and the
reduction types (`Component`, `Variable`, `Reduction`, and `to_reduction`).

```python
def generate_model_description(
    source: Reduction | Architecture | Path | str,
    output_dir: Path | str,
    *,
    composition: str | None = None,
    component: str | None = None,
    generation_time: datetime | None = None,
    base_index: int = 0,
) -> list[Path]: ...

def generate_c_headers(
    source: Reduction | Architecture | str | PathLike[str],
    output_dir: str | PathLike[str],
    *,
    composition: str | None = None,
    component: str | None = None,
    prefix: str | None = None,
    base_index: int = 0,
) -> list[Path]: ...

def generate_c_runtime(
    source: Reduction | Architecture | str | PathLike[str],
    output_dir: str | PathLike[str],
    *,
    composition: str | None = None,
    prefix: str | None = None,
    base_index: int = 0,
    omit: Sequence[str] | str = (),
) -> list[Path]: ...

def generate_modelica(
    source: Reduction | Architecture | str | Path,
    output_dir: str | Path,
    *,
    package: str = "GeneratedInterfaces",
    within: str | None = None,
    composition: str | None = None,
) -> list[Path]: ...

def to_reduction(
    source: Reduction | Architecture | str | PathLike[str],
    *,
    composition: str | None = None,
    base_index: int = 0,
) -> Reduction: ...

def fmi2_headers() -> tuple[Path, ...]: ...
```

`source` is a `.sysml` file, a directory of them, an already loaded
`pycps_sysml2.Architecture`, or a `Reduction`. `generation_time=None` uses the
fixed epoch `2000-01-01T00:00:00Z`; pass a timezone-aware datetime for any other
stamp. A naive datetime is refused. `fmi2_headers()` returns the bundled FMI 2.0
standard headers as real file paths, so an FMU build can pass them to the
`pyssp_standard` `FMU` facade without copying them into the fixture. The `.fmu`
archive is written by that facade; `pyfmi` emits only `linux64`/FMI 2.0 through
its CLI.

Parsing and generation are separable. `to_reduction()` is the only function that
reads `pycps_sysml2`; a `Reduction` carries the components, identity, package
name, and default experiment every generator needs. Pass a `Reduction` to run
the generators without the dialect being imported:

```python
from pathlib import Path

import pycps_sysml2
import pyfmi_sysml2

architecture = pycps_sysml2.load(Path("architecture/plant.sysml"))
reduction = pyfmi_sysml2.to_reduction(architecture)

pyfmi_sysml2.generate_c_headers(reduction, Path("build"))
pyfmi_sysml2.generate_modelica(reduction, Path("build"))
```

A `Reduction` has already fixed `composition=` and `base_index=`; passing either
again is refused rather than silently ignored.

```python
from datetime import datetime, timezone
from pathlib import Path

import pyfmi_sysml2
from pyssp_standard import FMU

source = Path("architecture/plant.sysml")
out = Path("build")
stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)

pyfmi_sysml2.generate_model_description(source, out, generation_time=stamp)
pyfmi_sysml2.generate_c_runtime(source, out)
pyfmi_sysml2.generate_modelica(source, out)

# The binary stem must equal the interface modelIdentifier (here: Tank).
FMU.package(
    out / "Plant.fmu",
    model_description=out / "Tank/modelDescription.xml",
    binaries={"linux64": out / "Tank.so"},
    sources=[out / "Plant_InterfaceCommon.h"],
    fmi_version="2.0",
)
```

## Generated artifact set

- `<out>/<Component>/modelDescription.xml` — one per exported component (a
  container root exports its leaves; a `:> FmuModel` definition exports itself).
- `<out>/<Prefix>_InterfaceCommon.h` — port payload structs, `DataType` enum,
  and `VrMapping`; plain C11.
- `<out>/<Prefix>_<Component>.h` — VR enum, `VrCount`, and the C++ `Instance`
  plus `initialize_vr_map()`; a direct FMU model whose definition names the
  package uses that name once (`Generator.h`).
- `<out>/<Prefix>_<Component>_fmi.cpp` — C++17 runtime with C linkage; implements
  the 38 FMI 2.0 CoSimulation entry points from the VR map. Nine of them are
  explicit `fmi2Error` stubs: the FMU-state, serialization, directional-derivative,
  and input/output-derivative functions.
- `<out>/<Prefix>_<Component>_hooks.h` — the five model hook declarations
  (`<stem>_model_initialize`, `<stem>_model_do_step`, `<stem>_model_terminate`,
  `<stem>_model_reset` called from `fmi2Reset`, and `<stem>_model_free` called
  from `fmi2FreeInstance`).
- `<out>/<Prefix>_<Component>_model.cpp` — created once, never rewritten; the
  implementer's only edited C++ file. It holds all five hook bodies, reset and
  free as no-ops; its default step returns `fmi2Error` until implemented. The
  instance struct ends with `void* user_data`, implementer-owned: the runtime
  never reads or writes it, `fmi2Reset` preserves it, and `model_free` releases
  it.
- `<out>/fmi2/fmi2Functions.h`, `fmi2FunctionTypes.h`, `fmi2TypesPlatform.h` —
  byte copies of the bundled FMI 2.0 standard headers.
- `<out>/<Package>/package.mo`, `package.order` — the root Modelica package and
  its member order.
- `<out>/<Package>/Interfaces.mo` — primitive input/output connector aliases;
  `GeneratedInterfaces.mo` — one undirected connector per port definition.
- `<out>/<Package>/<Component>_Interface.mo` — generated `partial model` with
  the parameters and one connector instance per port; the instance carries
  `input`/`output`, or nothing for `inout`/undirected, so direction lives on
  the instance rather than the connector type. Replaced whole.
- `<out>/<Package>/<Component>.mo` — created once, never rewritten; the
  implementer's Modelica model, extending the generated partial model.
- `<archive>.fmu` — `modelDescription.xml` at the root,
  `binaries/linux64/<modelIdentifier>.so`, and `sources/`, `resources/`,
  `documentation/` when supplied. `pyfmi package` only binds the command line;
  the archive is written by `pyssp_standard`'s `FMU` facade, and `linux64` is
  the only accepted platform.

`Prefix` defaults to the architecture package name; `Package` defaults to
`GeneratedInterfaces`. `--component NAME` narrows the C headers and runtime to
one exported component plus the common header. Value references start at the
requested `--base-index` (default 0) per component: parameters first, then ports
in declaration order, then fields. The C arrays stay zero-based and hold exactly
`array` elements; `--base-index` shifts only the FMI element names and the VR
enum labels, so `--base-index 1` still indexes `gains[0]..[n-1]`.

## Iterative development

`tests/iterative/` is an executable walkthrough of the loop the generators
exist for: generate the interface, write the model logic, change a port in the
architecture, regenerate in place. The generated half is replaced, the
hand-written model is untouched, and the build fails at the exact line that
still names the old port.

```bash
cd tests/iterative && ./run.sh
```

It needs the `pyfmi` console script and OpenModelica; `PYFMI=` and `OMC=`
override either path.

## Common errors

- **`generation_time must be timezone-aware`** — pass
  `datetime(..., tzinfo=timezone.utc)` or the CLI form
  `2026-01-01T00:00:00Z`. A naive time is refused so the artifact cannot depend
  on the host's locality.
- **Flat parameter attribute rejected** — parameters come from the parameter
  dialect (`in port parameters ...`), never from attributes on a part.
- **`platform 'windows64' is not supported; supported platforms: linux64`** —
  this package emits `linux64` only; do not widen the allow-list ad hoc.
- **`modelIdentifier 'Tank' does not match binary stem 'libTank'`** — name the
  shared library exactly `<modelIdentifier>.so` (or pass the matching
  `--platform` binary).
- **`Cannot pick a composition root`** — several `:> FmuModel` definitions, or
  several part definitions that have parts and are unused; pass
  `--composition NAME`.
- **Multiplicity is not a fixed length** — FMI 2.0 needs one scalar per element;
  use a fixed list size.

## Development

```bash
./venv/bin/ruff check src tests
./venv/bin/python -m pytest -m "not slow"     # CI subset
./venv/bin/python -m pytest                   # includes the omc oracle
UPDATE_GOLDENS=1 ./venv/bin/python -m pytest  # rewrite goldens locally
```

Goldens are compared byte-for-byte and `UPDATE_GOLDENS` is ignored when `CI` is
set. The header tests use `gcc -std=c11 -fsyntax-only` and
`g++ -std=c++17 -fsyntax-only`; the Modelica test uses `omc loadFile` +
`checkModel` and skips when `omc` is absent. See
`docs/breakdown/04-verification/README.md`.

## Migrating from `pyssp_sysml2`

`pyssp_sysml2 generate fmi` was removed in `pyssp_sysml2` v0.4.0. Use `pyfmi`
instead:

| removed | replacement |
|---|---|
| `pyssp_sysml2 generate fmi --architecture ...` | `pyfmi model-description ...` |
| FMI C headers from the same generator | `pyfmi c-headers ...` |
| — (no runtime sources were generated) | `pyfmi c-runtime ...`, the C++17 runtime and the `<stem>_model.cpp` seam |
| Modelica connector export | `pyfmi modelica ...`, now a partial model per component plus the `<Name>.mo` implementer seam |
| in-package FMU archive writer | `pyfmi package ...`, which delegates to `pyssp_standard`'s `FMU` facade |

The artifacts are migration-compatible: a container root keeps the `guid`
namespace string `pyssp_sysml2/<composition>/<component>` and the
`<composition>.<component>` `modelName`. A direct `:> FmuModel` definition uses
`pyssp_sysml2/<definition>` and the bare `<definition>` name, so rebuilding with
`pyfmi` does not change identity.
