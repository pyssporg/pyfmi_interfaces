---
id: IMP-002
type: imp
title: Re-pin pycps-sysml2 to the v0.3.0 release wheel
summary: The code reads the 0.3.0 experiment API while pyproject.toml still points at the v0.2.0 wheel, so a built wheel is importable only against a 0.3.0 dialect in the environment
date: 2026-11-19
status: suggested
---

# Re-pin pycps-sysml2 to the v0.3.0 release wheel

- **Question:** can the published wheel install a working environment on its
  own?
- **Evidence:** no. `model_description/document.py` reads `read_experiment` and
  `core/reduction.py` reads `classify_attribute`, both added in
  `pycps_sysml2` 0.3.0, while `pyproject.toml` still pins the v0.2.0 release
  URL. The break is deliberate; the pin was left alone because the v0.3.0 tag
  must exist before the direct-URL wheel can resolve.
- **Change:** replace the `pycps-sysml2` URL in `pyproject.toml` with the
  `v0.3.0` release asset, and update the version named in `INFO-012` and
  `INFO-011`. No source change is expected.
- **Risk:** a tag that points at a missing asset makes the wheel uninstallable,
  so the pin lands only after the sibling release is published; a stale pin
  keeps `pip install` resolving 0.2.0 and failing at the first import of the
  removed API.
- **Acceptance:** `pip install` of the built wheel in a clean venv resolves
  `pycps-sysml2` 0.3.0 from the URL, and one fixture end to end runs from the
  installed package.
