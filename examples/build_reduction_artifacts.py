"""Build a ``Reduction`` by hand and write all four artifact families.

Run from the repository root:

    python examples/build_reduction_artifacts.py [OUTPUT_DIR]

Only the standard library and ``pyfmi_interfaces`` are used. The script writes
modelDescription.xml, C headers, C++17 runtime sources, and Modelica text; it
does not compile or package anything.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from pyfmi_interfaces import (
    Component,
    Experiment,
    ExportIdentity,
    Reduction,
    Variable,
    generate_c_headers,
    generate_c_runtime,
    generate_model_description,
    generate_modelica,
)
from pyfmi_interfaces.core import Field, PortGroup

GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def scale_reduction() -> Reduction:
    """One component with a parameter, an input port, and an output port."""
    component = Component(
        name="Scale",
        doc=None,
        parameters=(Field("gain", "Real"),),
        ports=(
            PortGroup(
                name="u",
                definition="Signal",
                direction="in",
                causality="input",
                fields=(Field("value", "Real"),),
                doc=None,
            ),
            PortGroup(
                name="y",
                definition="Signal",
                direction="out",
                causality="output",
                fields=(Field("value", "Real"),),
                doc=None,
            ),
        ),
        variables=(
            Variable(
                name="gain",
                type_name="Real",
                causality="parameter",
                variability="fixed",
                value_reference=0,
                index=1,
                description=None,
                member="gain",
                start=2.0,
                start_text="2.0",
            ),
            Variable(
                name="u",
                type_name="Real",
                causality="input",
                variability=None,
                value_reference=1,
                index=2,
                description=None,
                member="u.value",
                start=0.0,
                start_text="0",
            ),
            Variable(
                name="y",
                type_name="Real",
                causality="output",
                variability=None,
                value_reference=2,
                index=3,
                description=None,
                member="y.value",
            ),
        ),
    )
    return Reduction(
        components=(component,),
        identity=ExportIdentity("Root", False),
        package="Demo",
        experiment=Experiment(start_time=0.0, stop_time=1.0, step_size=0.1),
        root="Root",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=Path("build/examples"),
        help="Output directory (default: build/examples).",
    )
    args = parser.parse_args()

    reduction = scale_reduction()
    written: list[Path] = []
    written += generate_model_description(
        reduction, args.output / "model-description", generation_time=GENERATION_TIME
    )
    written += generate_c_headers(reduction, args.output / "c")
    written += generate_c_runtime(reduction, args.output / "runtime")
    written += generate_modelica(reduction, args.output / "modelica")

    for path in written:
        print(path)


if __name__ == "__main__":
    main()
