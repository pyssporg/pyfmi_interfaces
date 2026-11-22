"""Export identity: the generation clock and the stable FMI ``guid``.

Identity is frozen for cross-library reproducibility: the ``guid`` and the
``modelName`` of a component must match pyssp_sysml2 v0.3.0, because the two
generators write into the same model directories during migration. The clock is
an injected parameter, never an ambient read, so the same architecture and the
same ``generation_time`` produce byte-identical artifacts.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pyfmi_interfaces.core.model import ExportIdentity

#: FMI ``dateTime`` form: UTC, second precision.
GENERATION_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

#: Fixed epoch stamped when no ``generation_time`` is injected, so an
#: un-injected build is byte-reproducible without a wall-clock read.
DEFAULT_GENERATION_TIME = datetime(2000, 1, 1, tzinfo=timezone.utc)

#: Namespace the FMI ``guid`` is derived from.
GUID_NAMESPACE = uuid.NAMESPACE_URL


def utc_now() -> datetime:
    """Current UTC time; pass it as ``generation_time`` for a wall-clock stamp."""
    return datetime.now(timezone.utc)


def format_generation_time(moment: datetime | None) -> str:
    """Render a timezone-aware time as an FMI ``dateTime``.

    ``None`` means :data:`DEFAULT_GENERATION_TIME`, never the wall clock, so a
    default build is reproducible. A naive time is rejected rather than guessed
    at, because the artifact would then depend on the host's locality.
    """
    if moment is None:
        moment = DEFAULT_GENERATION_TIME
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError(
            "generation_time must be timezone-aware, e.g. "
            "datetime(2026, 1, 1, tzinfo=timezone.utc)"
        )
    return moment.astimezone(timezone.utc).strftime(GENERATION_TIME_FORMAT)


def guid(key: str) -> str:
    """Format one uuid5 namespace key as an FMI ``guid``."""
    return "{" + str(uuid.uuid5(GUID_NAMESPACE, key)) + "}"


def component_guid(
    composition: str, component: str, *, direct: bool = False
) -> str:
    """Stable FMI ``guid`` for one component of one export unit.

    The namespace string is frozen verbatim from pyssp_sysml2 v0.3.0
    (``artifacts/fmi.py:183-185``): the ``pyssp_sysml2/`` prefix stays even
    though this package is named differently, so migrating a build from one
    generator to the other does not change a single guid. A direct FMU model
    has no container level; ``direct=True`` drops the composition from the key,
    exactly as :class:`ExportIdentity` derives the modelDescription guid.
    """
    return guid(ExportIdentity(composition, direct).guid_key(component))
