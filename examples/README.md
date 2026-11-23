# pyfmi_interfaces examples

Build a `Reduction` by hand and write all four FMI 2.0 artifact families: the
model description, C headers, C++17 runtime sources, and the Modelica package.
The library writes sources and never compiles or packages an FMU.

## Run

From the workspace root, in the workspace venv:

```bash
python repos/pyfmi_interfaces/examples/build_reduction_artifacts.py
```

Everything lands under the gitignored `build/examples/reduction-artifacts/`:

| Path | What |
| --- | --- |
| `model-description/Scale/modelDescription.xml` | FMI 2.0 model description |
| `c/` | C interface headers |
| `runtime/` | C++17 runtime, headers, hook stub, and bundled `fmi2/` headers |
| `modelica/GeneratedInterfaces/` | Modelica package |

Expected output from a clean `build/examples/reduction-artifacts/`. The hook
stub and the Modelica model are write-if-absent, so a rerun does not reprint
them:

```text
build/examples/reduction-artifacts/model-description/Scale/modelDescription.xml
build/examples/reduction-artifacts/c/Demo_InterfaceCommon.h
build/examples/reduction-artifacts/c/Demo_Scale.h
build/examples/reduction-artifacts/runtime/Demo_InterfaceCommon.h
build/examples/reduction-artifacts/runtime/Demo_Scale.h
build/examples/reduction-artifacts/runtime/Demo_Scale_fmi.cpp
build/examples/reduction-artifacts/runtime/Demo_Scale_hooks.h
build/examples/reduction-artifacts/runtime/Demo_Scale_model.cpp
build/examples/reduction-artifacts/runtime/fmi2/fmi2FunctionTypes.h
build/examples/reduction-artifacts/runtime/fmi2/fmi2Functions.h
build/examples/reduction-artifacts/runtime/fmi2/fmi2TypesPlatform.h
build/examples/reduction-artifacts/modelica/GeneratedInterfaces/GeneratedInterfaces.mo
build/examples/reduction-artifacts/modelica/GeneratedInterfaces/Interfaces.mo
build/examples/reduction-artifacts/modelica/GeneratedInterfaces/Scale.mo
build/examples/reduction-artifacts/modelica/GeneratedInterfaces/Scale_Interface.mo
build/examples/reduction-artifacts/modelica/GeneratedInterfaces/package.mo
build/examples/reduction-artifacts/modelica/GeneratedInterfaces/package.order
```

Pass `--out DIR` to write elsewhere.

## Setup

The workspace venv:

```bash
python -m venv .venv-experimental
source .venv-experimental/bin/activate
pip install --no-deps -r requirements-experimental.txt
pip install -r requirements-thirdparty.txt
```

`requirements-experimental.txt` installs `pyfmi_interfaces` and its
`pyssp_standard` provider.
