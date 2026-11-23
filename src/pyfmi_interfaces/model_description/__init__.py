"""FMI 2.0 ``modelDescription.xml`` generation from a Reduction.

One emitter renders the document: :mod:`.document` assembles the FMI fields,
adds ordered ``VendorAnnotations``, and serializes through the library codec.
"""

from __future__ import annotations

from pyfmi_interfaces.model_description.document import (
    ModelDescription,
    ModelDescriptionXmlCodec,
    generate_model_description,
)

__all__ = [
    "ModelDescription",
    "ModelDescriptionXmlCodec",
    "generate_model_description",
]
