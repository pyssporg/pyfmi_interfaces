"""The ``pyfmi`` command line: the package family.

This module is the only place that knows which artifact families exist. Each
family exports a :class:`~pyfmi_interfaces.core.cli.Command` registry; collecting
them here in ``--help`` order is the whole dispatcher. The shared option
spellings live in :mod:`pyfmi_interfaces.core.cli`.

The four generators are Python functions; ``pyfmi package`` is the only command.
An output location in and one written path on stdout is the shape. Argument
errors are argparse's (exit 2), packaging errors are reported without a traceback
(exit 1), and anything unexpected propagates.
"""

from __future__ import annotations

from collections.abc import Sequence

from pyfmi_interfaces.core.cli import Command, run
from pyfmi_interfaces.fmu import COMMANDS as FMU_COMMANDS

#: Every subcommand, in ``--help`` order.
COMMANDS: tuple[Command, ...] = (*FMU_COMMANDS,)


def main(argv: Sequence[str] | None = None) -> int:
    """Run one ``pyfmi`` command and return its process exit code."""
    return run(COMMANDS, argv)


if __name__ == "__main__":
    raise SystemExit(main())
