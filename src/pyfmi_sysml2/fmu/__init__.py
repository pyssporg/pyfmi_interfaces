"""The ``pyfmi package`` command.

Packaging lives in ``pyssp_standard``'s ``FMU`` facade; this module only binds
the command line to it.
"""

from __future__ import annotations

import argparse

from pyssp_standard import FMU

from pyfmi_sysml2.core.cli import Command, print_paths


def _configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUT",
        required=True,
        help="Output .fmu archive path (required).",
    )
    parser.add_argument(
        "--model-description",
        metavar="PATH",
        required=True,
        help="FMI 2.0 modelDescription.xml for the archive root.",
    )
    parser.add_argument(
        "--binary",
        metavar="PATH",
        required=True,
        help="Built shared library; its stem must be the modelIdentifier.",
    )
    parser.add_argument(
        "--platform",
        metavar="NAME",
        choices=["linux64"],
        default="linux64",
        help="Platform directory under binaries/ (default: linux64).",
    )
    parser.add_argument(
        "--header",
        metavar="PATH",
        action="append",
        default=[],
        help="Generated header to include under sources/ (repeatable).",
    )
    parser.add_argument(
        "--resource",
        metavar="PATH",
        action="append",
        default=[],
        help="File or directory to include under resources/ (repeatable).",
    )
    parser.add_argument(
        "--documentation",
        metavar="PATH",
        action="append",
        default=[],
        help="File or directory to include under documentation/ (repeatable).",
    )


def _run(args: argparse.Namespace) -> int:
    archive = FMU.package(
        args.output,
        model_description=args.model_description,
        binaries={args.platform: args.binary},
        sources=args.header,
        resources=args.resource,
        documentation=args.documentation,
        fmi_version="2.0",
    )
    print_paths([archive])
    return 0


COMMANDS = (
    Command(
        name="package",
        help="Write a deterministic .fmu archive.",
        description="Write a deterministic .fmu archive to the output path.",
        configure=_configure,
        handler=_run,
    ),
)
