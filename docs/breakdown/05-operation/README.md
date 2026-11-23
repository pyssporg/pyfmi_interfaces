---
title: Operation
summary: Install, run, build, test, and release the package.
---

# Operation

Local setup, the day-to-day commands, the implementer's build and packaging
step, the iterative walkthrough, and the release path.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **INFO-011** [Release process](release.md) — Tag the single-sourced 0.5.1 version after a green matrix, let wheels.yml publish the wheel and sdist, and smoke-test the wheel in a clean venv.
- **INFO-012** [Local setup](local-setup.md) — Create a venv with Python 3.11 or newer, install the editable package with the dev extra, and use that interpreter for every command.
- **INFO-016** [Building and packaging the generated runtime](building-and-packaging-the-generated-runtime.md) — The library emits C++17 sources and never compiles them; the implementer builds the shared library, names it after modelIdentifier, and pyfmi package delegates to pyssp_standard.FMU.package for linux64.
- **INFO-019** [Iterative development example](iterative-development-example.md) — tests/iterative/run.sh generates the Modelica interface, adds the model logic, renames a port, and shows the build failing at the model line; tests/test_iterative_example.py runs it as a slow system test.
<!-- pb:index:end -->
