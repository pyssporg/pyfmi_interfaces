"""Shared ``pyfmi`` command-line plumbing for the artifact families.

Each family registers one :class:`Command` per artifact it generates: the
subcommand name and parser text, a ``configure`` callback that adds the
family's options, and the handler that writes the artifact. This module owns
that shape, the option spellings the families share, the ``--generation-time``
type, and the error/report policy, so the shell surface cannot drift from
family to family. :mod:`pyfmi_sysml2.cli` only collects the registries and
dispatches.

Argument errors are argparse's (exit 2), generation and validation errors are
reported without a traceback (exit 1), and anything unexpected is left to
propagate.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from pyfmi_sysml2.core.identity import GENERATION_TIME_FORMAT

#: Where the generators write when no ``-o/--output`` is given.
DEFAULT_OUTPUT = "build"

#: Handled failures: authored-model errors and missing inputs.
GENERATION_ERRORS = (ValueError, KeyError, FileNotFoundError)


@dataclass(frozen=True)
class Command:
    """One ``pyfmi`` subcommand, as its artifact family declares it."""

    name: str
    help: str
    description: str
    configure: Callable[[argparse.ArgumentParser], None]
    handler: Callable[[argparse.Namespace], int]


def _parse_generation_time(text: str) -> datetime:
    """The FMI ``dateTime`` forms accepted on the command line, as UTC.

    The canonical form is the one the generator emits. An ISO 8601 form with an
    explicit offset is also accepted. A naive time is refused, because the
    artifact would then depend on the host's locality.
    """
    value = text.strip()
    if value.endswith("Z"):
        try:
            moment = datetime.strptime(value, GENERATION_TIME_FORMAT)
        except ValueError:
            pass
        else:
            return moment.replace(tzinfo=timezone.utc)

    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid generation time {text!r}; use "
            "YYYY-MM-DDTHH:MM:SSZ or an ISO 8601 form with an offset"
        ) from None
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise argparse.ArgumentTypeError(
            f"generation time {text!r} must carry a timezone, for example "
            "2026-01-01T00:00:00Z"
        )
    return moment.astimezone(timezone.utc)


def print_paths(written: list[Path]) -> None:
    """Report one written path per line, the output form every command shares."""
    for path in written:
        print(path)


def _message(error: BaseException) -> str:
    """``KeyError`` stringifies with quotes; the message is what matters."""
    if isinstance(error, KeyError) and error.args:
        return str(error.args[0])
    return str(error)


def add_source(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help="A .sysml file or a directory containing them.",
    )


def add_output(parser: argparse.ArgumentParser, help_text: str) -> None:
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUT",
        default=DEFAULT_OUTPUT,
        help=help_text,
    )


def add_composition(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--composition",
        metavar="NAME",
        help="Composition part definition to export (default: the single root).",
    )


def add_base_index(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-index",
        metavar="N",
        type=int,
        default=0,
        help=(
            "First emitted array index (default: 0; 1 targets OMC-built "
            "Modelica FMUs, which declare arrays one-based)."
        ),
    )


def add_generation_time(parser: argparse.ArgumentParser) -> None:
    """Add the shared ``--generation-time`` option to a family parser."""
    parser.add_argument(
        "--generation-time",
        metavar="ISO8601",
        type=_parse_generation_time,
        help=(
            "Fixed generationDateAndTime, for example 2026-01-01T00:00:00Z "
            "(default: 2000-01-01T00:00:00Z, the fixed epoch)."
        ),
    )


def build_parser(commands: Sequence[Command]) -> argparse.ArgumentParser:
    """The ``pyfmi`` parser with one subparser per registered command."""
    parser = argparse.ArgumentParser(
        prog="pyfmi",
        description=(
            "Generate FMI 2.0 CoSimulation artifacts from a SysML v2 "
            "architecture."
        ),
        epilog=(
            "Generators write to build/ unless -o/--output is given; "
            "pyfmi package requires an output archive path."
        ),
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, metavar="COMMAND"
    )
    for command in commands:
        command_parser = subparsers.add_parser(
            command.name,
            help=command.help,
            description=command.description,
        )
        command.configure(command_parser)
        command_parser.set_defaults(handler=command.handler)
    return parser


def run(commands: Sequence[Command], argv: Sequence[str] | None = None) -> int:
    """Parse one command line, run its handler, and return the exit code."""
    args = build_parser(commands).parse_args(argv)
    try:
        return args.handler(args)
    except GENERATION_ERRORS as error:
        print(f"pyfmi: {_message(error)}", file=sys.stderr)
        return 1
