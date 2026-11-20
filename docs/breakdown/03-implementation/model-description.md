---
id: INFO-005
type: info
title: modelDescription generation
summary: model_description/document.py assembles a pyssp_standard FMI 2 document from the reduction, stamps the injected clock, serializes, validates, then writes one file per component.
date: 2026-11-17
status: current
---

# modelDescription generation

`model_description_document()` builds an `Fmi2ModelDescriptionDocument`; nothing
in `model_description/document.py` writes XML by hand.

Document fields:

- `fmi_version="2.0"`, `model_name` = `<composition>.<component>` for a
  container root or the bare definition for a direct FMU model;
- `guid` from the frozen uuid5 key `pyssp_sysml2/<composition>/<component>` or
  `pyssp_sysml2/<definition>`, `generation_tool="pyfmi_sysml2 tooling"`;
- `generation_date_and_time` from the injected clock; omitted means the fixed
  `2000-01-01T00:00:00Z` epoch, and a naive time is refused;
- `variable_naming_convention="structured"`;
- `interface_type="CoSimulation"` and `capabilities` with
  `model_identifier=<component>` — both are required for the codec to emit the
  interface element;
- one `Fmi2ScalarVariable` per reduction variable, with the reduction's
  `variability` and `start` already rendered as FMI text; non-`Real` ports are
  discrete and inputs carry their neutral start (`CP-002`);
- `ModelStructure` outputs and initial unknowns from `component.outputs`, using
  the 1-based `Variable.index`;
- `DefaultExperiment` from the export unit's `Reduction.experiment`, captured
  once by `to_reduction()` from the typed container
  (`read_experiment(..., required=False)`): `startTime` and `stopTime` are the
  base fields, and `stepSize` and `tolerance` are the FMI fields that the
  packaged `Experiment` specialization adds. FMI 2.0.5 defines all four as
  optional doubles with no default, so every field the container's effective
  members provide is emitted and an absent one is omitted; a plain
  `DefaultExperiment` contributes start and stop only, and no container means
  no element. An authored tolerance is rendered by the codec with `str(value)`
  (for example `tolerance="1e-06"`).

`render_model_description()` serializes with
`Fmi2ModelDescriptionXmlCodec` and validates the object and text with
`Fmi2ModelDescriptionValidator` before returning. `generate_model_description()`
accepts a `Reduction`, an architecture, or its path; it writes
`<output>/<Component>/modelDescription.xml` per selected component and returns
the paths; a named component that is not exported is a `ValueError`.

The `start` text is produced by `pycps_sysml2.core.format_value` inside the
reduction and stored as `Variable.start_text`, so a Boolean is `true`/`false`,
never `str(True)`, and this module never calls the dialect formatter.

FMI authoring attributes are not chosen here: guid policy, modelName override,
units, and declared variability or initial are a standing non-goal (`INFO-018`).
