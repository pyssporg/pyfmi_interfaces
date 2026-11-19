---
id: INFO-011
type: info
title: Release process
summary: Tag the single-sourced 0.3.0 version after a green matrix, let wheels.yml publish the wheel and sdist, and smoke-test the wheel in a clean venv.
date: 2026-11-19
status: current
---

# Release process

The version is single-sourced: `pyfmi_sysml2.__version__` in
`src/pyfmi_sysml2/__init__.py`, read by `setuptools` through
`dynamic = ["version"]`. The current version is 0.3.0.

Steps:

1. Confirm `main` is green on 3.11 and 3.12 and the tree is clean.
2. Set `__version__` to the release version and commit.
3. Tag `v<version>` and push the tag; `wheels.yml` triggers on `v*`.
4. `wheels.yml` builds `python -m build --wheel --sdist`, asserts exactly one
   wheel and one sdist and no `0.0.0`, compares the sdist version to the wheel
   version, checks the tag against the imported `__version__`, uploads `dist/`,
   and creates the GitHub release with `fail_on_unmatched_files: true`.
5. Install the built wheel into a clean virtual environment and run a fixture
   end to end from the installed package, not the source tree.

The dependencies are direct-URL wheels pinned to sibling releases
(`pycps-sysml2` v0.2.0 and `experimental-pyssp-standard` v0.9.3.dev0). A wheel
is installable only when both release assets exist; a tag that points at a
missing asset is not a release.

The `pycps-sysml2` pin is behind the dialect: 0.3.0 removed the `pyssp_*`
control vocabulary this package no longer reads, so the code needs the v0.3.0
wheel. Re-pinning is a release chore that waits for that release asset (`IMP-002`);
until then a wheel built from this tree is importable only against a 0.3.0
`pycps_sysml2` in the environment.
