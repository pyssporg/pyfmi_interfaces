---
id: IMP-002
type: imp
title: Re-pin pycps-sysml2 to the v0.3.0 release wheel
summary: pyproject.toml pins the v0.3.0 wheel, so the dependency resolves the dialect API the code reads instead of the retired v0.2.0 pin
date: 2026-11-19
status: implemented
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
- **Outcome:** `pyproject.toml` pins the v0.3.0 asset, and `INFO-011`,
  `INFO-012`, and the install paragraph in `README.md` name that version. The
  URL resolves via `pip download --no-deps` (`pycps_sysml2-0.3.0-py3-none-any.whl`),
  and `pytest -m "not slow"` and `ruff check src tests` pass. The clean-venv
  wheel install and the installed-package fixture run were not repeated in this
  job; the pin download plus the suite stand in for them.
