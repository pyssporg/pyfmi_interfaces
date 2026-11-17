# Simulink and the generated/interface split

The Modelica artifact is an interface plus a scaffold: a generated package that
compiles on its own, a hand-written model file the generator creates once and
never rewrites, and a build that fails at exactly the member an interface change
broke (`commitments.md:29-31`). Simulink has no `partial model` and no
`extends`, and a model must compile before it can be saved, so there is no
"incomplete but honest" generated half. Its model files are also containers:
`.slx` is an OPC zip of XML that MathWorks classes as binary, and two identical
programmatic builds differ in `dcterms:created`, `dcterms:modified`,
`ModelUUID`, and `BDUuid`, with no documented path to byte-identical output.
`.mdl` is a diffable but noisy text container of embedded XML, timestamps, and
UUIDs, and the format may change; an `.m` build script is deterministic and
line-diffable but is a recipe, not a model. Any Simulink seam is therefore drawn
around what can be generated reproducibly, not around a generated model file.

## The five candidate designs

| Design | Seam shape | What is generated | What the human owns | Opportunities | Shortcomings |
| --- | --- | --- | --- | --- | --- |
| Contract only | Generated types and a manifest; models are entirely human | `Simulink.Bus` hierarchy, `Simulink.Bus.save` text, variable manifest, a check script | Every model, harness, and block | Deterministic output; no binary in the loop; works with any model; the manifest drives a drift oracle | No scaffold and no plumbing; nothing to simulate; drift detection is bespoke |
| Model reference | Generated content is referenced by a human parent model | A referenced model shell with generated root ports, or the port contract the shell must meet | The parent harness and the referenced model internals | Composition is native; referenced model can be built and checked alone; schemas stay in one place | Model block ports mirror the referenced root, so a port change rewrites the parent; a deleted port leaves a dangling line that `update` and `sim` still pass |
| Generated library of masked subsystems | Generated masked subsystems with typed ports, hand models place links | Library `.slx`, masks, port and parameter definitions, `Simulink.Bus` types | Each model that links the library and fills the masks | Encapsulation and reuse; port changes reach every instance; parameters get a typed surface | Library file is binary; links can be disabled or broken silently; a port change can disconnect existing lines |
| Variant subsystems | One model, generated variant configurations | `Simulink.Variant` objects and variant subsystem scaffolding | Every variant implementation and the choice between them | Switch configurations without touching the harness; a single model file to review | A configuration switch, not a regeneration seam; variants must share a port subset; regenerating is still a model edit |
| FMU route | The `.fmu` this repository already generates is imported as a block | `modelDescription.xml`, headers, runtime, archive; optionally an import harness via `add_block(...,'FMUName',...)` | The C++ model inside the FMU and the surrounding Simulink model | Reuses the shipped artifact; one interface definition on both sides; the built FMU is the unit under test | Needs a compiled binary for the host, so Windows needs FMU Builder and WSL2; CS runs its own solver, so hand logic outside the FMU is decoupled and tight algebraic coupling is poor |

## Recommendation

1. **Contract only** is the first seam to build. It is the only design whose
   outputs are deterministic text, and it is the smallest honest version of the
   promise: the architecture produces types and a variable list, the human
   builds the model, and a check tells both sides when they disagree. It also
   survives model-file churn, since no model file is generated.
2. **Model reference** is second. It is the closest thing Simulink has to a
   generated interface half, and semantic diff (`mlDiff`, `mlMerge`,
   `mlAutoMerge`) makes review of the parent possible. It earns its place only
   with the loud check: `sim(...,'StopTime',0)` with `UnconnectedInputMsg`,
   `UnconnectedOutputMsg`, and `UnconnectedLineMsg` set to `error`, because the
   default is silence on a dangling line.
3. **The FMU route** is orthogonal rather than third. The artifact already
   exists, so an `FMU Import` block is a way to consume this repository's output
   in Simulink, not a new way to generate Simulink content. Its solver and
   platform constraints make it a composition tool, not an authoring seam.

Byte-stable `.slx` is not on the list because no supported path produces it;
generating model files would trade the reproducibility commitment for a
scaffold.

## What this prototype proves

`run.sh` walks four stages and stops if any of them regresses:

| Stage | Action | Expected outcome |
| --- | --- | --- |
| 1 | `generate_types.py` reads `tests/fixtures/minimal/minimal.sysml` | Bus types and a variable manifest are written under `build/`, in plain text |
| 2 | `hand_model.m` builds the model and `simulate_model.m` runs it | The hand model simulates and produces `gain * input` |
| 3 | `check_interface.m` compares the model against the manifest | The interface check passes, so the contract and the model agree |
| 4 | The port is renamed in `v2.sysml` and types are regenerated | The check fails with a message naming both the old and the new name |

The scope is explicit. This validates the contract, the generated text, and the
drift oracle. It does not implement a Simulink generator, and it does not show a
hand model that a tool rewrites later: the human model is never touched by
regeneration, which is the point. The Modelica walkthrough in `tests/iterative/`
is the precedent for this shape, and `docs/breakdown/00-intent/intent.md:38-41`
still limits shipped artifacts to FMI, so this stays a proof, not a backend.

## Unverified

- Byte-stable `.slx`. No supported path is known; the observed differences are
  not proven to be exhaustive.
- Bus-element rename behaviour in a parent model. Element ports are name-based,
  so a rename should break, but it was not exercised here; plain inport renames
  stayed connected by port number.
- `exportToFMU` licensing wording across releases. It is documented as requiring
  Simulink Coder on R2023b; other releases were not checked.
- Comparison Tool licensing. Three-way merge and `mlDiff`/`mlMerge` availability
  by licence tier were not checked.
- Whether base Model Advisor checks suffice for interface assertions.
  `ModelAdvisor.run` and referenced-model analysis need Simulink Check; the base
  checks were not compared against a hand-written port check.

## How to run it

```bash
./tests/simulink/run.sh
```

`MATLAB=` and `PYTHON=` override the executables when they are not on `PATH`,
for example `MATLAB=/opt/MATLAB/R2023b/bin/matlab ./tests/simulink/run.sh`.
The run needs `python3` with this package installed, and MATLAB with Simulink.

The pytest entry point drives the same script, marked `slow` so it stays out of
the CI subset, and skips with a reason when MATLAB is not found. Generated
outputs land in `tests/simulink/build/`, which the repository already ignores.
