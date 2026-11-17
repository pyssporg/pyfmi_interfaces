"""Modelica interface package generation and its ``pyfmi`` command."""

from __future__ import annotations

import argparse

from pyfmi_sysml2.core.cli import (
    Command,
    add_composition,
    add_output,
    add_source,
    print_paths,
)
from pyfmi_sysml2.modelica.package import DEFAULT_PACKAGE, generate_modelica


def _configure(parser: argparse.ArgumentParser) -> None:
    add_source(parser)
    add_output(parser, "Output directory (default: build).")
    add_composition(parser)
    parser.add_argument(
        "--package",
        metavar="NAME",
        default=DEFAULT_PACKAGE,
        help=f"Root Modelica package name (default: {DEFAULT_PACKAGE}).",
    )
    parser.add_argument(
        "--within",
        metavar="NAME",
        help="Enclosing Modelica scope for the root package.",
    )


def _run(args: argparse.Namespace) -> int:
    written = generate_modelica(
        args.source,
        args.output,
        package=args.package,
        within=args.within,
        composition=args.composition,
    )
    print_paths(written)
    return 0


COMMANDS = (
    Command(
        name="modelica",
        help="Write a Modelica interface package.",
        description=(
            "Write the Modelica interface package to an output directory."
        ),
        configure=_configure,
        handler=_run,
    ),
)
