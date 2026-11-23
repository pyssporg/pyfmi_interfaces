"""Tool-independent annotations for an FMI 2.0 model description.

FMI 2.0 gives an implementation one extension point: the ``VendorAnnotations``
element, a sequence of ``Tool`` entries, each with a required ``name`` and an
opaque payload. The name is data — the tool id — and this module attaches no
meaning to it. The payload is a verbatim XML fragment: it is validated as
well-formed when the annotation is constructed and emitted unchanged, so a tool
keeps byte-for-byte control of its own markup. An empty payload is allowed and
means the tool is present with no content.

No clock, no tool knowledge, and no normalization live here; ordering is the
insertion order of the collection that holds the annotations.
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree as ET


class AnnotationError(ValueError):
    """An annotation name or payload that cannot be emitted faithfully."""


def validate_fragment(payload: str) -> None:
    """Raise :class:`AnnotationError` unless ``payload`` is an XML fragment.

    A fragment may hold zero or more elements and text. It is validated by
    wrapping it in one synthetic element; an XML declaration (which is not
    allowed inside an element) therefore fails, as does malformed markup. The
    payload is never rewritten.
    """
    if not isinstance(payload, str):
        raise AnnotationError(
            f"annotation payload must be str, got {type(payload).__name__}"
        )
    try:
        ET.fromstring(f"<annotation-fragment>{payload}</annotation-fragment>")
    except ET.ParseError as exc:
        raise AnnotationError(f"annotation payload is not well-formed XML: {exc}") from exc


@dataclass(frozen=True)
class Annotation:
    """One ``VendorAnnotations/Tool`` entry.

    ``name`` is the tool id, preserved exactly. ``payload`` is a well-formed
    XML fragment emitted verbatim; callers own its whitespace, so equal inputs
    always produce equal bytes.
    """

    name: str
    payload: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise AnnotationError("annotation name must be a non-empty string")
        validate_fragment(self.payload)
