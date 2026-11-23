---
id: INFO-011
type: info
title: Release process
summary: Tag the single-sourced 0.5.1 version after a green matrix, let wheels.yml publish the wheel and sdist, and smoke-test the wheel in a clean venv.
date: 2026-11-19
status: current
---

# Release process

The version is single-sourced: `pyfmi_interfaces.__version__` in
`src/pyfmi_interfaces/__init__.py`, read by `setuptools` through
`dynamic = ["version"]`. The current version is 0.5.1.

Steps:

1. Confirm `main` is green on 3.11 and 3.12 and the tree is clean.
2. Set `__version__` to the release version and commit.
3. Tag `v<version>` and push the tag; `wheels.yml` triggers on `v*`.
4. `wheels.yml` builds `python -m build --wheel --sdist`, asserts exactly one
   wheel and one sdist and no `0.0.0`, compares the sdist version to the wheel
   version, checks the tag against the imported `__version__`, uploads `dist/`,
   and creates the GitHub release with `fail_on_unmatched_files: true`.
5. Install the built wheel into a clean virtual environment, then run the
   suite and `examples/build_reduction_artifacts.py` from the installed package,
   not the source tree.

The dependency is a direct-URL wheel pinned to a sibling release
(`experimental-pyssp-standard` v0.9.4.dev0). A wheel is installable only when
that release asset exists; a tag that points at a missing asset is not a
release.
