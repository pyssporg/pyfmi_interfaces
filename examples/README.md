# Examples

Minimal, runnable examples. They need only the standard library,
`pyfmi_interfaces`, and its `pyssp_standard` dependency; packaging also needs a
C++17 compiler and the `pyfmi` console script.

- [`build_reduction_artifacts.py`](build_reduction_artifacts.py) — builds a
  `Reduction` by hand and writes all four artifact families into one directory.
- The packaging block below — compiles the generated runtime and writes a
  deterministic `.fmu` with `pyfmi package`.

## Build the artifacts

From the repository root:

```bash
python examples/build_reduction_artifacts.py build/examples
```

The script writes `modelDescription.xml`, the C headers, the C++17 runtime
sources, and the Modelica package under `build/examples/`:

```text
build/examples/model-description/Scale/modelDescription.xml
build/examples/c/Demo_InterfaceCommon.h
build/examples/c/Demo_Scale.h
build/examples/runtime/Demo_Scale_fmi.cpp
build/examples/runtime/Demo_Scale_hooks.h
build/examples/runtime/Demo_Scale_model.cpp
build/examples/runtime/fmi2/
build/examples/modelica/GeneratedInterfaces/
```

## Package the FMU

The library writes sources but never compiles them. Build the shared library so
its stem equals the `modelIdentifier` (`Scale` in this example), then package:

```bash
g++ -std=c++17 -shared -fPIC \
    -Ibuild/examples/runtime -Ibuild/examples/runtime/fmi2 \
    build/examples/runtime/Demo_Scale_fmi.cpp \
    build/examples/runtime/Demo_Scale_model.cpp \
    -o build/examples/Scale.so

pyfmi package -o build/examples/Scale.fmu \
    --model-description build/examples/model-description/Scale/modelDescription.xml \
    --binary build/examples/Scale.so \
    --header build/examples/c/Demo_Scale.h
```

The archive contains `modelDescription.xml` at its root,
`binaries/linux64/Scale.so`, and `sources/Demo_Scale.h`. Without an editable
install, replace `pyfmi` with
`python -m pyfmi_interfaces.cli`.
