"""Contract tests for the single annotation-aware FMI 2.0 document emitter."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from lxml import etree

from pyfmi_interfaces import (
    Annotation,
    AnnotationError,
    ModelDescription,
    ModelDescriptionXmlCodec,
)
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

pytestmark = pytest.mark.contract


def _document() -> Fmi2ModelDescriptionDocument:
    return Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version="2.0",
        model_name="Demo",
        guid="{00000000-0000-0000-0000-000000000000}",
        generation_tool="pyfmi_interfaces tooling",
        generation_date_and_time="2000-01-01T00:00:00Z",
        interface_type="CoSimulation",
        capabilities=Fmi2InterfaceAttributes(
            model_identifier="Demo",
            extra_attributes={
                "canHandleVariableCommunicationStepSize": "false",
                "canInterpolateInputs": "false",
            },
        ),
        variables=[
            Fmi2ScalarVariable(
                name="gain",
                value_reference=0,
                type_name="Real",
                causality="parameter",
                variability="fixed",
                initial="exact",
                start=2,
            ),
        ],
        model_structure=Fmi2ModelStructure(
            outputs=[Fmi2Unknown(index=2), Fmi2Unknown(index=4)],
            initial_unknowns=[Fmi2Unknown(index=2)],
        ),
    )


def _tool_payload() -> str:
    return (
        '      <CsFmuPackager solverType="fixed_step">\n'
        "        <InternalConnections>\n"
        '          <Connection source="src.y" target="tgt.u" />\n'
        "        </InternalConnections>\n"
        "      </CsFmuPackager>"
    )


def _xsd() -> etree.XMLSchema:
    path = files("pyssp_standard") / "schema" / "FMI2" / "fmi2ModelDescription.xsd"
    return etree.XMLSchema(etree.parse(str(path)))


def _assert_valid(xml: str) -> None:
    schema = _xsd()
    document = etree.fromstring(xml.encode("utf-8"))
    assert schema.validate(document), schema.error_log


def test_annotation_rejects_malformed_payload() -> None:
    with pytest.raises(AnnotationError):
        Annotation("tool", "<NotClosed>")


def test_annotation_rejects_empty_name() -> None:
    with pytest.raises(AnnotationError):
        Annotation("", "<Empty />")


def test_annotation_allows_an_empty_payload() -> None:
    assert Annotation("tool").payload == ""


def test_no_annotations_is_the_library_bytes() -> None:
    document = _document()
    expected = Fmi2ModelDescriptionXmlCodec().serialize(document)

    model = ModelDescription(document)

    assert ModelDescriptionXmlCodec().serialize(model) == expected


def test_plain_golden_round_trips_byte_identically() -> None:
    """The existing plain golden survives parse → serialize unchanged."""
    path = Path(__file__).parent / "golden" / "package" / "Scale.xml"
    text = path.read_text(encoding="utf-8")
    codec = ModelDescriptionXmlCodec()

    assert codec.serialize(codec.parse(text)) == text


def test_annotations_keep_order_name_and_payload() -> None:
    payload_one = '<ToolA a="1"><Child /></ToolA>'
    payload_two = "<ToolB>text</ToolB>"
    model = ModelDescription(
        _document(),
        [Annotation("a", payload_one), Annotation("b", payload_two)],
    )

    xml = ModelDescriptionXmlCodec().serialize(model)

    root = ET.fromstring(xml)
    tools = root.find("VendorAnnotations").findall("Tool")
    assert [tool.get("name") for tool in tools] == ["a", "b"]
    assert payload_one in xml
    assert payload_two in xml
    assert xml.index("VendorAnnotations") < xml.index("<ModelVariables>")


def test_annotations_sit_after_default_experiment() -> None:
    document = _document()
    document.default_experiment = Fmi2DefaultExperiment(
        start_time=0.0, stop_time=1.0
    )
    model = ModelDescription(document, [Annotation("tool", "<Tool />")])

    xml = ModelDescriptionXmlCodec().serialize(model)

    assert (
        xml.index("<DefaultExperiment")
        < xml.index("<VendorAnnotations>")
        < xml.index("<ModelVariables>")
    )


def test_annotation_round_trip_preserves_payloads() -> None:
    codec = ModelDescriptionXmlCodec()
    first = ModelDescription(
        _document(),
        [Annotation("a", '<A x="1" />'), Annotation("b", "<B><C /></B>")],
    )
    first_xml = codec.serialize(first)

    parsed = codec.parse(first_xml)
    second_xml = codec.serialize(parsed)

    assert parsed.annotation_names == ("a", "b")
    assert codec.parse(second_xml).annotations == parsed.annotations
    assert second_xml == first_xml


def test_annotation_round_trip_preserves_trailing_whitespace() -> None:
    payload = '<A x="1" />\n'
    codec = ModelDescriptionXmlCodec()
    first_xml = codec.serialize(
        ModelDescription(_document(), [Annotation("a", payload)])
    )

    parsed = codec.parse(first_xml)

    assert parsed.annotations[0].payload == payload
    assert codec.serialize(parsed) == first_xml


def test_model_structure_keeps_unknown_order() -> None:
    model = ModelDescription(_document())

    xml = ModelDescriptionXmlCodec().serialize(model)

    root = ET.fromstring(xml)
    outputs = root.find("ModelStructure/Outputs")
    initial = root.find("ModelStructure/InitialUnknowns")
    assert [unknown.get("index") for unknown in outputs] == ["2", "4"]
    assert [unknown.get("index") for unknown in initial] == ["2"]


def test_duplicate_annotation_names_are_refused() -> None:
    with pytest.raises(AnnotationError):
        ModelDescription(
            _document(),
            [Annotation("tool", "<A />"), Annotation("tool", "<B />")],
        )


def test_add_annotation_preserves_insertion_order() -> None:
    model = ModelDescription(_document())
    model.add_annotation(Annotation("first", "<First />"))
    model.add_annotation(Annotation("second", "<Second />"))

    assert model.annotation_names == ("first", "second")


def test_plain_document_validates_against_fmi2_xsd() -> None:
    xml = ModelDescriptionXmlCodec().serialize(ModelDescription(_document()))

    _assert_valid(xml)


def test_annotated_document_validates_against_fmi2_xsd() -> None:
    model = ModelDescription(
        _document(),
        [Annotation("cs-fmu-packager", _tool_payload())],
    )

    xml = ModelDescriptionXmlCodec().serialize(model)

    _assert_valid(xml)
    assert "<InternalConnections>" in xml
