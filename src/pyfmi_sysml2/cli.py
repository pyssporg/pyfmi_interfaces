"""The ``pyfmi`` command line: one subcommand per generated artifact.

This module is the only place that knows which artifact families exist. Each
family exports a :class:`~pyfmi_sysml2.core.cli.Command` registry; collecting
them here in ``--help`` order is the whole dispatcher. The shared option
spellings and the ``--generation-time`` parsing live in
:mod:`pyfmi_sysml2.core.cli`.

A source path in, an output location out, and one line per written path on
stdout: every family keeps that shape. Argument errors are argparse's (exit 2),
generation and validation errors are reported without a traceback (exit 1), and
anything unexpected is left to propagate.
"""

from __future__ import annotations

from collections.abc import Sequence

from pyfmi_sysml2.c import COMMANDS as C_COMMANDS
from pyfmi_sysml2.core.cli import Command, run
from pyfmi_sysml2.fmu import COMMANDS as FMU_COMMANDS
from pyfmi_sysml2.model_description import (
    COMMANDS as MODEL_DESCRIPTION_COMMANDS,
)
from pyfmi_sysml2.modelica import COMMANDS as MODELICA_COMMANDS

#: Every subcommand, in ``--help`` order.
COMMANDS: tuple[Command, ...] = (
    *MODEL_DESCRIPTION_COMMANDS,
    *C_COMMANDS,
    *MODELICA_COMMANDS,
    *FMU_COMMANDS,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Run one ``pyfmi`` command and return its process exit code."""
    return run(COMMANDS, argv)


if __name__ == "__main__":
    raise SystemExit(main())
