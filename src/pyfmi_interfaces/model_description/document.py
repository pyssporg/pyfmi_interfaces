"""FMI 2.0 CoSimulation ``modelDescription.xml`` generation.

The variable set, the causalities, and the start values come from
:mod:`pyfmi_interfaces.core`; this module maps that reduction onto the
``pyssp_standard`` FMI 2 document model, adds the one extension point that model
does not represent — ordered, tool-independent ``VendorAnnotations`` — and
serializes the result. The document is validated before it reaches disk, so a
file this module writes is one the library's own XSD and semantic validators
accept.

The generation clock and the component ``guid`` live in
:mod:`pyfmi_interfaces.core.identity`: identity is frozen for cross-library
reproducibility, because the two generators write into the same model
directories during migration.

There is one emitter. The FMI document itself is rendered by the
``pyssp_standard`` codec, which owns the canonical FMI spelling; when
annotations exist the ``VendorAnnotations`` block is inserted at the schema
position immediately before ``ModelVariables``. Neither step reads a clock or
an unordered mapping, so equal inputs always produce equal bytes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.parsers import expat
from xml.sax.saxutils import escape

from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import (
    Fmi2DefaultExperiment,
    Fmi2ElementInfo,
    Fmi2InterfaceAttributes,
    Fmi2ModelDescriptionDocument,
    Fmi2ModelStructure,
    Fmi2ScalarVariable,
    Fmi2Unknown,
)
from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionValidator

from pyfmi_interfaces.core import (
    Component,
    Experiment,
    Reduction,
    select_component,
)
from pyfmi_interfaces.core.annotations import Annotation, AnnotationError
from pyfmi_interfaces.core.identity import format_generation_time, guid

#: FMI version emitted for every generated document.
FMI_VERSION = "2.0"

#: ``generationTool`` stamped into every document.
GENERATION_TOOL = "pyfmi_interfaces tooling"


def default_experiment(
    experiment: Experiment | None,
) -> Fmi2DefaultExperiment | None:
    """The export unit's ``DefaultExperiment``, or ``None`` when unset.

    The experiment is the typed container the caller supplies, never an
    attribute name. A plain ``DefaultExperiment`` supplies ``startTime`` and
    ``stopTime``; the packaged ``Experiment`` specialization adds ``stepSize``
    and ``tolerance``. FMI 2.0.5 defines all four as optional doubles, so every
    field the reduction provides is emitted and an absent one is omitted.
    """
    if experiment is None:
        return None
    return Fmi2DefaultExperiment(
        start_time=experiment.start_time,
        stop_time=experiment.stop_time,
        tolerance=experiment.tolerance,
        step_size=experiment.step_size,
    )


def model_description_document(
    reduction: Reduction,
    component: Component | str,
    *,
    generation_time: datetime | None = None,
    include_default_experiment: bool = True,
) -> Fmi2ModelDescriptionDocument:
    """The FMI 2.0 document for one component, before serialization.

    ``reduction`` is the interface model; it already fixes the export root and
    the array index base. ``include_default_experiment=False``
    omits ``DefaultExperiment`` even when the reduction carries an experiment.
    """
    if isinstance(component, str):
        component = select_component(reduction, component)
    identity = reduction.identity
    experiment = (
        default_experiment(reduction.experiment)
        if include_default_experiment
        else None
    )

    outputs = [Fmi2Unknown(index=variable.index) for variable in component.outputs]
    return Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version=FMI_VERSION,
        model_name=identity.model_name(component.name),
        guid=guid(identity.guid_key(component.name)),
        description=component.doc or None,
        generation_tool=GENERATION_TOOL,
        generation_date_and_time=format_generation_time(generation_time),
        variable_naming_convention="structured",
        # Both fields are required: the codec emits the interface element only
        # when it has an interface type *and* its attributes.
        interface_type="CoSimulation",
        capabilities=Fmi2InterfaceAttributes(model_identifier=component.name),
        variables=[
            Fmi2ScalarVariable(
                name=variable.name,
                value_reference=variable.value_reference,
                type_name=variable.type_name,
                description=variable.description,
                causality=variable.causality,
                variability=variable.variability,
                start=variable.start_text,
            )
            for variable in component.variables
        ],
        model_structure=Fmi2ModelStructure(
            outputs=outputs,
            initial_unknowns=[
                Fmi2Unknown(index=variable.index) for variable in component.outputs
            ],
        ),
        default_experiment=experiment,
    )


def render_model_description(
    reduction: Reduction,
    component: Component | str,
    *,
    generation_time: datetime | None = None,
    include_default_experiment: bool = True,
) -> str:
    """Serialize and validate one component's model description."""
    document = model_description_document(
        reduction,
        component,
        generation_time=generation_time,
        include_default_experiment=include_default_experiment,
    )
    xml = Fmi2ModelDescriptionXmlCodec().serialize(document)
    Fmi2ModelDescriptionValidator().validate(document, xml)
    return xml


def generate_model_description(
    reduction: Reduction,
    output_dir: Path | str,
    *,
    component: str | None = None,
    generation_time: datetime | None = None,
    include_default_experiment: bool = True,
) -> list[Path]:
    """Write ``<output_dir>/<Component>/modelDescription.xml`` per leaf.

    ``reduction`` is the interface model; it already fixes the export root and
    the array index base. ``component`` narrows the run to one
    component and fails when it is not exported. ``generation_time`` fixes
    ``generationDateAndTime``; ``None`` stamps the fixed default epoch
    (2000-01-01T00:00:00Z), so an un-injected build is byte-reproducible, a
    naive time is refused. ``include_default_experiment=False`` omits
    ``DefaultExperiment`` from every written document.
    """
    if generation_time is not None:
        format_generation_time(generation_time)

    selected = list(reduction.components)
    if component is not None:
        selected = [select_component(reduction, component)]

    root = Path(output_dir)
    written: list[Path] = []
    for candidate in selected:
        document = model_description_document(
            reduction,
            candidate,
            generation_time=generation_time,
            include_default_experiment=include_default_experiment,
        )
        xml = Fmi2ModelDescriptionXmlCodec().serialize(document)
        Fmi2ModelDescriptionValidator().validate(document, xml)

        path = root / candidate.name / "modelDescription.xml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml, encoding="utf-8")
        written.append(path)
    return written


@dataclass
class ModelDescription:
    """An FMI 2.0 document plus its ordered, tool-independent annotations."""

    document: Fmi2ModelDescriptionDocument
    annotations: list[Annotation] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.annotations = list(self.annotations)
        self._check_names()

    def _check_names(self) -> None:
        names = [annotation.name for annotation in self.annotations]
        if len(set(names)) != len(names):
            raise AnnotationError(
                "annotation names must be unique within one document: "
                f"{names}"
            )

    @property
    def annotation_names(self) -> tuple[str, ...]:
        """Annotation names in emission order."""
        return tuple(annotation.name for annotation in self.annotations)

    def add_annotation(self, annotation: Annotation) -> ModelDescription:
        """Append one annotation, preserving insertion order."""
        if not isinstance(annotation, Annotation):
            raise TypeError(
                f"expected Annotation, got {type(annotation).__name__}"
            )
        self.annotations.append(annotation)
        try:
            self._check_names()
        except AnnotationError:
            self.annotations.pop()
            raise
        return self

    def with_annotation(self, annotation: Annotation) -> ModelDescription:
        """A copy with one annotation appended."""
        return ModelDescription(
            self.document,
            [*self.annotations, annotation],
        )


_VENDOR_ANNOTATIONS = "VendorAnnotations"
_TOOL = "Tool"


def _render_vendor_annotations(annotations: list[Annotation]) -> str:
    """The ``VendorAnnotations`` block, indented for a two-space document."""
    tools = "\n".join(
        f"    <{_TOOL} name=\"{escape(annotation.name)}\">\n"
        f"{annotation.payload}\n"
        f"    </{_TOOL}>"
        for annotation in annotations
    )
    return f"  <{_VENDOR_ANNOTATIONS}>\n{tools}\n  </{_VENDOR_ANNOTATIONS}>"


def _raw_tool_payloads(xml_text: str) -> list[tuple[str | None, str]]:
    """Every ``VendorAnnotations/Tool`` name and its payload, byte for byte.

    ``ElementTree`` re-spells a start tag when it serializes, so it cannot keep
    a caller's payload faithful. Expat reports byte offsets; slicing the input
    between a ``Tool`` start tag and its end tag preserves the fragment exactly,
    including attribute whitespace. Only the outer newline the emitter adds and
    the indentation before ``</Tool>`` are removed.
    """
    data = xml_text.encode("utf-8")
    parser = expat.ParserCreate()
    vendor_depth = 0
    current: dict[str, object] | None = None
    captures: list[tuple[str | None, str]] = []

    def start(name: str, attributes: dict[str, str]) -> None:
        nonlocal vendor_depth, current
        index = parser.CurrentByteIndex
        if name == _VENDOR_ANNOTATIONS:
            vendor_depth += 1
        elif name == _TOOL and vendor_depth:
            current = {"name": attributes.get("name"), "content": None}
        elif current is not None and current["content"] is None:
            current["content"] = index

    def characters(text: str) -> None:
        nonlocal current
        if current is not None and current["content"] is None and text:
            current["content"] = parser.CurrentByteIndex

    def end(name: str) -> None:
        nonlocal vendor_depth, current
        if name == _TOOL and current is not None:
            start_index = current["content"]
            if start_index is None:
                start_index = parser.CurrentByteIndex
            raw = data[int(start_index):parser.CurrentByteIndex].decode("utf-8")
            raw = raw.removeprefix("\n")
            # The emitter frames the payload with exactly this suffix; remove
            # only that, so a caller's own trailing whitespace survives.
            suffix = "\n    "
            if raw.endswith(suffix):
                raw = raw[: -len(suffix)]
            captures.append((current["name"], raw))
            current = None
        elif name == _VENDOR_ANNOTATIONS:
            vendor_depth -= 1

    parser.StartElementHandler = start
    parser.CharacterDataHandler = characters
    parser.EndElementHandler = end
    parser.Parse(data, True)
    return captures


#: Interface attributes the ``pyssp_standard`` parser turns into booleans.
_KNOWN_BOOLEAN_ATTRIBUTES = frozenset(
    {
        "canGetAndSetFMUstate",
        "canSerializeFMUstate",
        "providesDirectionalDerivative",
        "needsExecutionTool",
        "completedIntegratorStepNotNeeded",
        "canBeInstantiatedOnlyOncePerProcess",
        "canNotUseMemoryManagementFunctions",
    }
)


def _restore_spelled_capabilities(
    xml_text: str,
    document: Fmi2ModelDescriptionDocument,
) -> None:
    """Keep every spelled interface attribute the typed flags drop.

    The library parser turns a known boolean into ``True``/``False`` and omits
    an explicit ``false``. The emitter spells the caller's attributes, so the
    raw interface attributes are kept in ``extra_attributes`` when the flag is
    already ``False``; this makes parse → serialize preserve the spelling.
    """
    root = ET.fromstring(xml_text)
    interface = root.find("CoSimulation")
    if interface is None:
        interface = root.find("ModelExchange")
    if interface is None or document.capabilities is None:
        return
    extras: dict[str, str] = {}
    for key, value in interface.attrib.items():
        if key == "modelIdentifier":
            continue
        if (
            key in _KNOWN_BOOLEAN_ATTRIBUTES
            and value.strip().lower() == "true"
        ):
            continue
        extras[key] = value
    document.capabilities.extra_attributes = extras


def _restore_real_start_text(
    xml_text: str,
    document: Fmi2ModelDescriptionDocument,
) -> None:
    """Keep a Real ``start`` as spelled; the library parser makes it a float.

    The emitter preserves the author's spelling, so ``start="2"`` must not come
    back as ``2.0`` after a round trip. The typed value is still available to
    callers that re-parse numerically.
    """
    root = ET.fromstring(xml_text)
    model_variables = root.find("ModelVariables")
    if model_variables is None:
        return
    elements = model_variables.findall("ScalarVariable")
    for variable, element in zip(document.variables, elements):
        type_element = next(
            (child for child in element if child.tag != "Annotations"),
            None,
        )
        if (
            type_element is not None
            and type_element.tag == "Real"
            and "start" in type_element.attrib
        ):
            variable.start = type_element.attrib["start"]


def _parse_annotations(xml_text: str) -> list[Annotation]:
    annotations: list[Annotation] = []
    for name, payload in _raw_tool_payloads(xml_text):
        if name is None:
            raise AnnotationError("VendorAnnotations/Tool is missing its name")
        annotations.append(Annotation(name=name, payload=payload))
    return annotations


def _serialize(model: ModelDescription) -> str:
    """Render the FMI document, inserting annotations at the schema position."""
    xml = Fmi2ModelDescriptionXmlCodec().serialize(model.document)
    if not model.annotations:
        return xml
    marker = "\n  <ModelVariables"
    index = xml.find(marker)
    if index < 0:
        raise AnnotationError(
            "cannot place VendorAnnotations: document has no ModelVariables"
        )
    return (
        xml[:index]
        + "\n"
        + _render_vendor_annotations(model.annotations)
        + xml[index:]
    )


class ModelDescriptionXmlCodec:
    """Serialize and parse :class:`ModelDescription`."""

    def serialize(self, model: ModelDescription) -> str:
        if not isinstance(model, ModelDescription):
            raise TypeError(
                f"expected ModelDescription, got {type(model).__name__}"
            )
        return _serialize(model)

    def parse(self, xml_text: str) -> ModelDescription:
        document = Fmi2ModelDescriptionXmlCodec().parse(xml_text)
        _restore_spelled_capabilities(xml_text, document)
        _restore_real_start_text(xml_text, document)
        return ModelDescription(document, _parse_annotations(xml_text))


__all__ = [
    "ModelDescription",
    "ModelDescriptionXmlCodec",
]
