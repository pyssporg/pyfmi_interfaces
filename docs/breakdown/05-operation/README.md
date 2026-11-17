---
title: Operation
summary: Install, run, build, test, and release the package.
---

# Operation

Local setup, the day-to-day commands, the implementer's build step, and the
release path.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **INFO-011** [Release process](release.md) — Tag v0.1.0 after a green matrix, build wheel and sdist, install the wheel into a clean venv, and attach the artifacts to the GitHub release.
- **INFO-012** [Local setup](local-setup.md) — Create the venv, install the editable package with the dev extra, and use the repo-local interpreter for every command.
- **INFO-016** [Building and packaging the generated runtime](building-and-packaging-the-generated-runtime.md) — The library emits C++ sources and never compiles them; the implementer builds the shared library, names it after modelIdentifier, and packages it.
- **INFO-019** [Iterative development example](iterative-development-example.md) — tests/iterative/run.sh generates the interface, adds the model logic, renames a port, and shows the build failing at the model line; a slow test runs it.
<!-- pb:index:end -->
