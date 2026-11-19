<!-- GENERATED FILE — do not edit. Regenerate with `pb registers`. -->

# Traceability Map

Generated from record front-matter: each decision names the leaf that
holds its outcome (`state:`). The breakdown never references a record —
the leaf is the source of truth; the record is how the state got there.

### Intent

- **AD-003** — State: `docs/breakdown/03-implementation/c-runtime-generation-and-model-hooks.md` (docs/breakdown/03-implementation/c-runtime-generation-and-model-hooks.md) · Artifacts: `src/pyfmi_sysml2/c_runtime.py`, `src/pyfmi_sysml2/cli.py`, `tests/test_c_runtime.py`, `tests/c_runtime_harness.cpp`

### Product

- **AD-002** — State: `docs/breakdown/01-product/variable-model.md` (docs/breakdown/01-product/variable-model.md) · Artifacts: `src/pyfmi_sysml2/interface.py`, `src/pyfmi_sysml2/modelica.py`
- **AD-004** — State: `docs/breakdown/01-product/variable-model.md` (docs/breakdown/01-product/variable-model.md) · Artifacts: `src/pyfmi_sysml2/interface.py`, `tests/test_model_description.py`, `tests/test_fmpy_load.py`

### Architecture

- **AD-001** — State: `docs/breakdown/02-architecture/determinism.md` (docs/breakdown/02-architecture/determinism.md) · Artifacts: `src/pyfmi_sysml2/model_description.py`
- **AD-005** — State: `docs/breakdown/02-architecture/module-map.md` (docs/breakdown/02-architecture/module-map.md) · Artifacts: `src/pyfmi_sysml2/core/model.py`, `src/pyfmi_sysml2/core/reduction.py`, `src/pyfmi_sysml2/core/spelling.py`, `src/pyfmi_sysml2/core/identity.py`, `src/pyfmi_sysml2/c/headers.py`, `src/pyfmi_sysml2/c/runtime.py`, `src/pyfmi_sysml2/model_description/document.py`, `src/pyfmi_sysml2/modelica/package.py`, `src/pyfmi_sysml2/fmu/archive.py`, `tests/test_layering.py`
- **AD-006** — State: `docs/breakdown/03-implementation/model-description.md` (docs/breakdown/03-implementation/model-description.md) · Artifacts: `src/pyfmi_sysml2/model_description/document.py`, `src/pyfmi_sysml2/core/reduction.py`, `src/pyfmi_sysml2/__init__.py`, `tests/test_model_description.py`, `tests/test_fixture_policy.py`, `tests/fixtures/README.md`, `tests/fixtures/applied/applied.sysml`, `tests/fixtures/applied/case.md`
- **AD-007** — State: `02-architecture/interface-reduction.md` (Interface reduction) · Artifacts: `src/pyfmi_sysml2/core/reduction.py`
- **AD-008** — State: `03-implementation/model-description.md` (modelDescription generation) · Artifacts: `src/pyfmi_sysml2/model_description/document.py`
