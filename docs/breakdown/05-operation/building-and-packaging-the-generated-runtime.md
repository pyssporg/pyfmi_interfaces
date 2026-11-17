---
id: INFO-016
type: info
title: Building and packaging the generated runtime
summary: The library emits C++ sources and never compiles them; the implementer builds the shared library, names it after modelIdentifier, and packages it.
date: 2026-11-17
status: current
---

# Building and packaging the generated runtime

The generated runtime becomes an FMU through the implementer's build, not this
library's.

- **Library output:** C++ sources in the output directory; no compiler
  invocation, no Makefile or CMake file, no `.so`.
- **Build:** compile the runtime and the model file as C++17 into a shared
  library whose stem equals the interface `modelIdentifier` (`CP-001`):
  `g++ -std=c++17 -shared -fPIC -Ibuild -Ibuild/fmi2 build/Controller_Controller_fmi.cpp build/Controller_Controller_model.cpp -o build/Controller.so`
- **Include roots:** `-I<out>` for the component header, `-I<out>/fmi2` for the
  FMI standard headers.
- **Refresh:** after an interface change, re-run the generator, rebuild, and
  repackage (`CP-004`); the model file is the only artifact that survives.
- **Package:** `pyfmi package` takes the built binary, the modelDescription,
  and optional headers; runtime sources are not yet packaged because the
  upstream facade cannot carry `SourceFiles` (`INFO-014`).
