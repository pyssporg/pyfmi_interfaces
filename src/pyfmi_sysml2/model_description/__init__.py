"""FMI 2.0 ``modelDescription.xml`` generation and its ``pyfmi`` command."""

from __future__ import annotations

import argparse

from pyfmi_sysml2.core.cli import (
    Command,
    add_base_index,
    add_composition,
    add_generation_time,
    add_output,
    add_source,
    print_paths,
)
from pyfmi_sysml2.model_description.document import generate_model_description


def _configure(parser: argparse.ArgumentParser) -> None:
    add_source(parser)
    add_output(parser, "Output directory (default: build).")
    add_composition(parser)
    add_base_index(parser)
    parser.add_argument(
        "--component",
        metavar="NAME",
        help="Restrict the output to one exported component.",
    )
    add_generation_time(parser)


def _run(args: argparse.Namespace) -> int:
    written = generate_model_description(
        args.source,
        args.output,
        composition=args.composition,
        component=args.component,
        generation_time=args.generation_time,
        base_index=args.base_index,
    )
    print_paths(written)
    return 0


COMMANDS = (
    Command(
        name="model-description",
        help="Write modelDescription.xml per component.",
        description=(
            "Write modelDescription.xml per component to an output directory."
        ),
        configure=_configure,
        handler=_run,
    ),
)
