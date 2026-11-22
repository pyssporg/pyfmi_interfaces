"""FMI 2.0 CoSimulation ``modelDescription.xml`` generation.

The variable set, the causalities, and the start values come from
:mod:`pyfmi_interfaces.core`; this module only maps that reduction onto the
``pyssp_standard`` FMI 2 document model and serializes it. The document is
validated before it reaches disk, so a file this module writes is one the
library's own XSD and semantic validators accept.

The generation clock and the component ``guid`` live in
:mod:`pyfmi_interfaces.core.identity`: identity is frozen for cross-library
reproducibility, because the two generators write into the same model
directories during migration.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

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
)
from pyfmi_interfaces.core.identity import format_generation_time, guid

#: FMI version emitted for every generated document.
FMI_VERSION = "2.0"

#: ``generationTool`` stamped into every document.
GENERATION_TOOL = "pyfmi_interfaces tooling"


def default_experiment(
    experiment: Experiment | None,
) -> Fmi2DefaultExperiment | None:
    """The composition's ``DefaultExperiment``, or ``None`` when unset.

    The experiment is the typed container the dialect recognizes, never an
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


def _select_component(reduction: Reduction, name: str) -> Component:
    for candidate in reduction.components:
        if candidate.name == name:
            return candidate
    raise ValueError(f"No exported component named {name!r}")


def model_description_document(
    reduction: Reduction,
    component: Component | str,
    *,
    generation_time: datetime | None = None,
) -> Fmi2ModelDescriptionDocument:
    """The FMI 2.0 document for one component, before serialization.

    ``reduction`` is the parser-free interface model; it already fixes the
    composition and the array index base.
    """
    if isinstance(component, str):
        component = _select_component(reduction, component)
    identity = reduction.identity

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
        default_experiment=default_experiment(reduction.experiment),
    )


def render_model_description(
    reduction: Reduction,
    component: Component | str,
    *,
    generation_time: datetime | None = None,
) -> str:
    """Serialize and validate one component's model description."""
    document = model_description_document(
        reduction,
        component,
        generation_time=generation_time,
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
) -> list[Path]:
    """Write ``<output_dir>/<Component>/modelDescription.xml`` per leaf.

    ``reduction`` is the parser-free interface model; it already fixes the
    composition and the array index base. ``component`` narrows the run to one
    component and fails when it is not exported. ``generation_time`` fixes
    ``generationDateAndTime``; ``None`` stamps the fixed default epoch
    (2000-01-01T00:00:00Z), so an un-injected build is byte-reproducible, a
    naive time is refused.
    """
    if generation_time is not None:
        format_generation_time(generation_time)

    selected = list(reduction.components)
    if component is not None:
        selected = [
            candidate for candidate in selected if candidate.name == component
        ]
        if not selected:
            raise ValueError(f"No exported component named {component!r}")

    root = Path(output_dir)
    written: list[Path] = []
    for candidate in selected:
        document = model_description_document(
            reduction,
            candidate,
            generation_time=generation_time,
        )
        xml = Fmi2ModelDescriptionXmlCodec().serialize(document)
        Fmi2ModelDescriptionValidator().validate(document, xml)

        path = root / candidate.name / "modelDescription.xml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml, encoding="utf-8")
        written.append(path)
    return written
