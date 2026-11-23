"""System tests for the ``pyfmi`` packaging command.

This module pins the shell contract of the one command: ``pyfmi package`` and
its argparse surface.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from pyfmi_interfaces.cli import main

pytestmark = pytest.mark.system

GOLDEN_XML = Path(__file__).parent / "golden" / "package" / "Scale.xml"


def test_package_subcommand_writes_an_fmu(tmp_path: Path) -> None:
    binary = tmp_path / "lib" / "Scale.so"
    binary.parent.mkdir()
    binary.write_bytes(b"\x7fELF\x02\x01\x01\x00")

    archive = tmp_path / "Scale.fmu"
    argv = [
        "package",
        "-o",
        str(archive),
        "--model-description",
        str(GOLDEN_XML),
        "--binary",
        str(binary),
    ]

    assert main(argv) == 0
    assert archive.is_file()
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
    assert "modelDescription.xml" in names
    assert "binaries/linux64/Scale.so" in names


@pytest.mark.parametrize("command", [None, "package"])
def test_help_succeeds_and_mentions_the_output(command, capsys) -> None:
    argv = ["--help"] if command is None else [command, "--help"]

    with pytest.raises(SystemExit) as raised:
        main(argv)

    assert raised.value.code == 0
    assert "output" in capsys.readouterr().out


def test_unsupported_platform_is_a_usage_error(tmp_path: Path, capsys) -> None:
    with pytest.raises(SystemExit) as raised:
        main(
            [
                "package",
                "-o",
                str(tmp_path / "Tank.fmu"),
                "--model-description",
                str(tmp_path / "absent.xml"),
                "--binary",
                str(tmp_path / "Tank.so"),
                "--platform",
                "windows64",
            ]
        )

    assert raised.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--platform" in captured.err
    assert "Traceback" not in captured.err


def test_missing_binary_is_reported_without_a_traceback(
    tmp_path: Path, capsys
) -> None:
    assert (
        main(
            [
                "package",
                "-o",
                str(tmp_path / "Scale.fmu"),
                "--model-description",
                str(GOLDEN_XML),
                "--binary",
                str(tmp_path / "absent.so"),
            ]
        )
        == 1
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "pyfmi:" in captured.err
    assert "absent.so" in captured.err
    assert "Traceback" not in captured.err


def test_console_script_is_installed() -> None:
    executable = Path(sys.executable).with_name("pyfmi")
    assert executable.is_file(), f"missing console script {executable}"

    result = subprocess.run(
        [str(executable), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "usage: pyfmi" in result.stdout
