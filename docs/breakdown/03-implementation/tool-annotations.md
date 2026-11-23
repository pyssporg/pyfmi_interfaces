---
id: INFO-020
type: info
title: Tool annotations
summary: The ordered, tool-independent VendorAnnotations layer in the one modelDescription emitter, with verbatim payloads, one code path, and schema validation.
date: 2026-11-23
status: current
---

# Tool annotations

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
facade. The reduction-driven `generate_model_description()` keeps its signature
and bytes.
