# Tests

Five levels plus an orthogonal `slow` marker. Each level owns a fault the others
cannot see, so a green run at a lower level is not evidence for a higher one.

| Marker | Level | What it can fail on | Where |
| --- | --- | --- | --- |
| `static` | source and repository policy | a rule that holds without running the package: layering (family isolation, registration completeness), dependency shape, fixture records, golden coverage, provenance | `test_fixture_policy.py`, `test_layering.py` |
| `unit` | one object's behaviour | the bundled FMI 2.0 header set; the reduction from a parsed architecture to variables (identifiers, defaults, variable order) with no artifact written | `test_headers.py`; the reduction has no dedicated test module and is asserted through `pyfmi_sysml2.core` inside the artifact tests |
| `component` | one generated artifact | the bytes of `modelDescription.xml`, the C interface headers, the C++17 runtime sources, the Modelica package with its implementer model, or the packaged `.fmu` — compared against its golden; the runtime also compiles, links, and executes its harness | `test_model_description.py`, `test_c_headers.py`, `test_c_runtime.py`, `test_modelica.py`, `test_package.py`, `test_package_roots.py` |
| `contract` | two directions must agree | value-reference order between the XML and the C enum, the Modelica connector set against the FMI variables, and one component identity across XML, header, and archive | `test_cross_artifact.py`, recorded by `tests/golden/cross-artifact/case.md` |
| `system` | the CLI end to end | argument parsing, exit codes, files written by one `pyfmi` invocation; a compiled and packaged FMU loads, steps, and returns outputs through fmpy; the executable walkthroughs run | `test_cli.py`, `test_fmpy_load.py`, `test_iterative_example.py`, `test_simulink_prototype.py` |
| `slow` | runtime qualifier | a check too expensive for the default run, such as the `omc` compile gate or a MATLAB prototype run; combined with the level above, excluded with `-m "not slow"` | `test_modelica.py`, `test_iterative_example.py`, `test_simulink_prototype.py` |

`slow` combines with the level above; it never stands alone.

```bash
python -m pytest tests/                  # everything, slow included
python -m pytest tests/ -m "not slow"    # the CI subset
python -m pytest tests/ -m static        # policy only
```

## Where the evidence lives

- `tests/fixtures/<subject>/` — the architecture inputs. A fixture is the only
  input a golden has, so it is reviewed like a golden; see
  `tests/fixtures/README.md`.
- `tests/golden/<artifact>/<subject>/` — committed expected output, compared
  **byte for byte** by `tests/golden_utils.py`. A golden is not test output; it
  is a reviewed artifact.
- `case.md` — the record next to each fixture and each golden. It states the
  conversion, the requirement or fault the case guards, the level, the input,
  the expected bytes, the *independent* oracle, the comparison, what may be
  normalized, the volatile fields, the update policy, and the update history.
  Every golden is named by a backticked path in the record that governs it.

An artifact test that only asserts "a file was written" is not evidence; the
fault must be visible in a trajectory, a compiled header, a validated document,
or a byte diff.

## Regenerating goldens

Goldens are regenerated deliberately, never as a side effect of running the
suite:

```bash
UPDATE_GOLDENS=1 python -m pytest tests/test_c_headers.py
git diff tests/golden/        # read every line before committing
```

The rewrite is refused whenever `CI` is set: `conftest.update_goldens()` returns
`False` under `CI` regardless of `UPDATE_GOLDENS`, so CI can only compare. A
golden updated in CI would make the gate agree with whatever the code did.

Committing a fixture change and the goldens it moves happens in one commit, with
the `case.md` update history extended.
