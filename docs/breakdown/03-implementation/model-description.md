---
id: INFO-005
type: info
title: modelDescription generation
summary: model_description/document.py is the one emitter: it assembles a pyssp_standard FMI 2 document from the reduction, serializes, validates, and writes it.
date: 2026-11-22
status: current
---

# modelDescription generation

`model_description_document()` builds an `Fmi2ModelDescriptionDocument`; nothing
in `model_description/document.py` writes XML by hand.

Document fields:

- `fmi_version="2.0"`, `model_name` = `<system>.<component>` for a
  container root or the bare definition name for a direct FMU model;
- `guid` from the frozen uuid5 key `pyssp_sysml2/<system>/<component>` or
  `pyssp_sysml2/<definition>`, frozen for byte-identical GUIDs from earlier
  releases; `generation_tool="pyfmi_interfaces tooling"`;
- `generation_date_and_time` from the injected clock; omitted means the fixed
  `2000-01-01T00:00:00Z` epoch, and a naive time is refused;
- `variable_naming_convention="structured"`;
- `interface_type="CoSimulation"` and `capabilities` with
  `model_identifier=<component>` — both are required for the codec to emit the
  interface element;
- one `Fmi2ScalarVariable` per reduction variable, with the reduction's
  `variability` and `Variable.start_text` (rendered from the typed `start`);
  non-`Real` ports are discrete and inputs carry their neutral start (`CP-002`);
- `ModelStructure` outputs and initial unknowns from `component.outputs`, using
  the 1-based `Variable.index`;
- `DefaultExperiment` from `Reduction.experiment`: `startTime`, `stopTime`,
  `stepSize`, and `tolerance` are the four optional FMI 2.0.5 doubles with no
  default, so every field the `Experiment` provides is emitted and an absent one
  is omitted; no `Experiment` means no element. A tolerance is rendered by the
  codec with `str(value)` (for example `tolerance="1e-06"`).

`render_model_description()` serializes with
`Fmi2ModelDescriptionXmlCodec` and validates the object and text with
`Fmi2ModelDescriptionValidator` before returning. `generate_model_description()`
accepts a `Reduction`; it writes
`<output>/<Component>/modelDescription.xml` per selected component and returns
the paths; a named component that is not exported is a `ValueError`.
`include_default_experiment: bool = True` on all three functions omits the
element when `False`; `True` keeps the existing bytes.

The typed `start` is stored as `Variable.start` and its FMI text as
`Variable.start_text`; both are supplied by the caller, so a Boolean is
`true`/`false`, never `str(True)`, and this module never formats a value.

FMI authoring attributes are not chosen here: guid policy, modelName override,
units, and declared variability or initial are a standing non-goal (`INFO-018`).

Tool annotations are a separate leaf (`INFO-020`).
