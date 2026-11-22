"""Shared command-line plumbing for the ``pyfmi`` artifact families.

Each family registers one :class:`Command` per artifact it generates: the
subcommand name and parser text, a ``configure`` callback that adds the
family's options, and the handler that writes the artifact. This module owns
that shape, the error/report policy, and the dispatcher, so the shell surface
cannot drift from family to family. :mod:`pyfmi_interfaces.cli` only collects
the registries and dispatches.

Argument errors are argparse's (exit 2), generation and validation errors are
reported without a traceback (exit 1), and anything unexpected is left to
propagate.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

#: Handled failures: authored-model errors and missing inputs.
GENERATION_ERRORS = (ValueError, KeyError, FileNotFoundError)


@dataclass(frozen=True)
class Command:
    """One subcommand, as its artifact family declares it."""

    name: str
    help: str
    description: str
    configure: Callable[[argparse.ArgumentParser], None]
    handler: Callable[[argparse.Namespace], int]


def print_paths(written: list[Path]) -> None:
    """Report one written path per line, the output form every command shares."""
    for path in written:
        print(path)


def _message(error: BaseException) -> str:
    """``KeyError`` stringifies with quotes; the message is what matters."""
    if isinstance(error, KeyError) and error.args:
        return str(error.args[0])
    return str(error)


def build_parser(
    commands: Sequence[Command], *, prog: str = "pyfmi"
) -> argparse.ArgumentParser:
    """The parser with one subparser per registered command."""
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Generate FMI 2.0 CoSimulation artifacts.",
        epilog="Generators write to build/ unless -o/--output is given.",
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


def run(
    commands: Sequence[Command],
    argv: Sequence[str] | None = None,
    *,
    prog: str = "pyfmi",
) -> int:
    """Parse one command line, run its handler, and return the exit code."""
    args = build_parser(commands, prog=prog).parse_args(argv)
    try:
        return args.handler(args)
    except GENERATION_ERRORS as error:
        print(f"{prog}: {_message(error)}", file=sys.stderr)
        return 1
