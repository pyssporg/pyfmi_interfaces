---
id: INFO-005
type: info
title: modelDescription generation
summary: model_description/document.py is the one emitter: it assembles a pyssp_standard FMI 2 document from the reduction, adds ordered tool-independent VendorAnnotations, serializes, validates, and writes it.
date: 2026-11-22
status: current
---

# modelDescription generation

`model_description_document()` builds an `Fmi2ModelDescriptionDocument`; nothing
in `model_description/document.py` writes XML by hand.

Document fields:

- `fmi_version="2.0"`, `model_name` = `<composition>.<component>` for a
  container root or the bare definition for a direct FMU model;
- `guid` from the frozen uuid5 key `pyssp_sysml2/<composition>/<component>` or
  `pyssp_sysml2/<definition>`, `generation_tool="pyfmi_interfaces tooling"`;
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
accepts a parser-free `Reduction`; it writes
`<output>/<Component>/modelDescription.xml` per selected component and returns
the paths; a named component that is not exported is a `ValueError`.

`model_description_document()`, `render_model_description()`, and
`generate_model_description()` take `include_default_experiment: bool = True`.
`False` omits the element; `True` keeps the existing bytes.

The typed `start` is stored as `Variable.start`; its FMI text is produced by the
reduction builder (through `pycps_sysml2.core.format_value` in `pyfmi_sysml`)
and stored as `Variable.start_text`, so a Boolean is `true`/`false`, never
`str(True)`, and this module never calls the dialect formatter.

FMI authoring attributes are not chosen here: guid policy, modelName override,
units, and declared variability or initial are a standing non-goal (`INFO-018`).

## Tool annotations

FMI 2.0's one extension point is `VendorAnnotations`, an ordered list of `Tool`
entries with a `name` (the tool id, data not an enum) and an opaque payload.
`core/annotations.py` defines the tool-independent value `Annotation(name,
payload)`; `model_description/document.py` is the one emitter and defines the
document view `ModelDescription(document, annotations)` and
`ModelDescriptionXmlCodec`.

**Payload type.** The payload is a verbatim XML fragment string, not an element
tree: `Annotation` validates it as well-formed (wrapping it in one synthetic
element) and the emitter emits it unchanged. This keeps a tool's own markup —
attribute order, line breaks, indentation, self-closing spelling — byte-stable;
no normalization is applied. An empty payload is allowed.

**Emission.** Annotations follow insertion order and each `name` is preserved
exactly; duplicate names are refused. There is one code path: the FMI document
is rendered by `Fmi2ModelDescriptionXmlCodec`, and when annotations exist the
`VendorAnnotations` block is inserted immediately before `ModelVariables`, the
schema position. With no annotations the bytes are exactly the library codec's
output. No layout switch exists, so there is no second spelling of the same
document.

The emitter reads no clock and no dict-order-dependent source; the document
model carries `ModelStructure/Outputs` and `InitialUnknowns` as ordered
`Fmi2Unknown` lists, rendered in stored order.

**Reading.** `ModelDescriptionXmlCodec.parse()` keeps the annotations, in order,
with their payload bytes. The raw fragment is recovered by byte offset from the
input (ElementTree re-spells a start tag on serialization), so parse →
serialize → parse is stable. An explicit `false` capability and a Real `start`
spelling are also restored, because the library parser drops the former and
normalizes the latter to a float.

**Schema.** Both a plain emitted document and an annotated one are validated
against `pyssp_standard`'s shipped `schema/FMI2/fmi2ModelDescription.xsd` in the
contract tests, so the `VendorAnnotations` insertion stays schema-valid.

**Public surface.** `Annotation` and `AnnotationError` are exported from
`pyfmi_interfaces.core` and the facade; `ModelDescription` and
`ModelDescriptionXmlCodec` from `pyfmi_interfaces.model_description` and the
facade. The reduction-driven `generate_model_description()` keeps its
signature and bytes.
