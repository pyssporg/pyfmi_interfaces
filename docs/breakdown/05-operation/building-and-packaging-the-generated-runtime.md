---
id: INFO-016
type: info
title: Building and packaging the generated runtime
summary: The library emits C++17 sources and never compiles them; the implementer builds the shared library, names it after modelIdentifier, and pyfmi package delegates to pyssp_standard.FMU.package for linux64.
date: 2026-11-17
status: current
---

# Building and packaging the generated runtime

The generated runtime becomes an FMU through the implementer's build, not this
library's.

- **Library output:** `<stem>_fmi.cpp`, `<stem>_hooks.h`, `<stem>_model.cpp`,
  and the FMI standard headers under `fmi2/`; no compiler invocation, no
  Makefile or CMake file, no `.so`.
- **Build:** compile the runtime and the model file as C++17 into a shared
  library whose stem equals the component's `modelIdentifier` (`CP-001`):
  `g++ -std=c++17 -shared -fPIC -I<out> -I<out>/fmi2 <out>/Controller_Controller_fmi.cpp <out>/Controller_Controller_model.cpp -o <out>/Controller.so`
- **Include roots:** `<out>` for the component header, `<out>/fmi2` for the FMI
  standard headers.
- **Refresh:** after an interface change, re-run the generator, rebuild, and
  repackage (`CP-004`); `<stem>_model.cpp` is the only artifact that survives.
- **Package:** `pyfmi package -o build/Controller.fmu --model-description
  build/Controller/modelDescription.xml --binary build/Controller.so --header
  build/Controller/Controller_Controller.h` delegates to
  `pyssp_standard.FMU.package`: the binary lands under `binaries/linux64/`,
  headers under `sources/`, and `--resource` and `--documentation` are optional.
- **Platform:** `--platform` accepts only `linux64`; the archive carries one
  binary directory.
