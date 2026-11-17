"""C headers and the C++17 FMI runtime, with their ``pyfmi`` commands."""

from __future__ import annotations

import argparse

from pyfmi_sysml2.c.headers import generate_c_headers
from pyfmi_sysml2.c.runtime import generate_c_runtime
from pyfmi_sysml2.core.cli import (
    Command,
    add_base_index,
    add_composition,
    add_output,
    add_source,
    print_paths,
)

_PREFIX_HELP = "Header prefix and C type prefix (default: the package name)."


def _configure_headers(parser: argparse.ArgumentParser) -> None:
    add_source(parser)
    add_output(parser, "Output directory (default: build).")
    add_composition(parser)
    add_base_index(parser)
    parser.add_argument("--prefix", metavar="NAME", help=_PREFIX_HELP)


def _configure_runtime(parser: argparse.ArgumentParser) -> None:
    add_source(parser)
    add_output(parser, "Output directory (default: build).")
    add_composition(parser)
    add_base_index(parser)
    parser.add_argument("--prefix", metavar="NAME", help=_PREFIX_HELP)
    parser.add_argument(
        "--omit",
        metavar="NAME[,NAME...]",
        action="append",
        default=[],
        help=(
            "Skip the definition of an FMI function and leave a marker; "
            "repeatable and comma-separated."
        ),
    )


def _run_headers(args: argparse.Namespace) -> int:
    written = generate_c_headers(
        args.source,
        args.output,
        composition=args.composition,
        prefix=args.prefix,
        base_index=args.base_index,
    )
    print_paths(written)
    return 0


def _run_runtime(args: argparse.Namespace) -> int:
    written = generate_c_runtime(
        args.source,
        args.output,
        composition=args.composition,
        prefix=args.prefix,
        base_index=args.base_index,
        omit=args.omit,
    )
    print_paths(written)
    return 0


COMMANDS = (
    Command(
        name="c-headers",
        help="Write C interface headers.",
        description="Write the C interface headers to an output directory.",
        configure=_configure_headers,
        handler=_run_headers,
    ),
    Command(
        name="c-runtime",
        help="Write the C headers and a C++17 FMI runtime.",
        description=(
            "Write the C interface headers, a C++17 FMI 2.0 CoSimulation "
            "runtime, and a user-owned model file to an output directory."
        ),
        configure=_configure_runtime,
        handler=_run_runtime,
    ),
)
