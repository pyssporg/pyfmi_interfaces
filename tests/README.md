# Tests

Five levels plus an orthogonal `slow` qualifier. Each level owns a fault the
others cannot see, so a green run at a lower level is not evidence for a higher
one.

| Marker | Level | What it can fail on | Where |
| --- | --- | --- | --- |
| `static` | source and repository policy | a rule that holds without running the package: layering (family isolation, registration completeness), the input rule (no module imports a parser), dependency shape, the documented facade, and the deprecated import name | `test_layering.py`, `test_import_shim.py` |
| `unit` | one object's behaviour | the bundled FMI 2.0 header set; the component-selection rule and the frozen export identity | `test_headers.py`, `test_interface_model.py` |
| `component` | one generated artifact | the bytes of `modelDescription.xml` and the deterministic archive layout and metadata | `test_model_description.py`, `test_package.py` |
| `contract` | two directions must agree | the one document emitter (parse → serialize stability, ordered annotation payloads, XSD validity) and a generator run from a hand-built `Reduction` producing the same bytes every time | `test_model_description_annotations.py`, `test_reduction_inputs.py` |
| `system` | the CLI end to end | argument parsing, exit codes, and the files written by one `pyfmi package` invocation | `test_cli.py` |
| `slow` | runtime qualifier | a check too expensive for the default run; combined with the level above and excluded with `-m "not slow"`; no current test carries it | — |

`slow` combines with the level above; it never stands alone.

```bash
python -m pytest tests/                  # everything, slow included
python -m pytest tests/ -m "not slow"    # the CI subset
python -m pytest tests/ -m static        # policy only
```

## Where the evidence lives

- `tests/golden/<artifact>/<subject>/` — committed expected output, compared
  **byte for byte** by `tests/golden_utils.py`. A golden is not test output; it
  is a reviewed artifact.
- `case.md` — the record next to each golden. It states the
  conversion, the requirement or fault the case guards, the level, the input,
  the expected bytes, the *independent* oracle, the comparison, what may be
  normalized, the volatile fields, the update policy, and the update history.
  Every golden is named by a backticked path in the record that governs it.
- Test inputs are constructed inline in each module. A `Reduction` is the only
  input a generator receives.

An artifact test that only asserts "a file was written" is not evidence; the
fault must be visible in a compiled header, a validated document, or a byte
diff.

## Regenerating goldens

Goldens are regenerated deliberately, never as a side effect of running the
suite:

```bash
UPDATE_GOLDENS=1 python -m pytest tests/test_package.py
git diff tests/golden/        # read every line before committing
```

The rewrite is refused whenever `CI` is set: `conftest.update_goldens()` returns
`False` under `CI` regardless of `UPDATE_GOLDENS`, so CI can only compare. A
golden updated in CI would make the gate agree with whatever the code did.

Committing a fixture change and the goldens it moves happens in one commit, with
the `case.md` update history extended.
