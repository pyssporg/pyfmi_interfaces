---
id: INFO-009
type: info
title: CLI
summary: The pyfmi entry point registers the package family and has one subcommand; the four source-taking generators moved to pyfmi-sysml, print one written path per line, exit 1 on handled input errors, and 2 on argument errors.
date: 2026-11-17
status: current
---

# CLI

`pyproject.toml` maps `pyfmi = "pyfmi_interfaces.cli:main"`. `cli.py` is a thin
dispatcher: it imports each family's `COMMANDS` tuple, concatenates them in
`--help` order, and hands the result to `core.cli.run()`. It parses no
arguments of its own.

`core/cli.py` owns the shape every family registers against:
`Command(name, help, description, configure, handler)`, `print_paths`,
`build_parser()`, and `run()` with the exit-code policy. A family's
`__init__.py` declares its options in `configure` and its work in a `handler`
that calls one generator.

The one subcommand:

- `pyfmi package -o OUT --model-description PATH --binary PATH
  [--platform linux64] [--header PATH] [--resource PATH] [--documentation PATH]`

Behaviour:

- `package` requires an output path, a `modelDescription.xml`, and the built
  shared library; its stem must be the modelIdentifier.
- `package --platform` accepts only `linux64` (default `linux64`).
- `--header`, `--resource`, and `--documentation` are repeatable.
- The written path is printed on stdout, one per line.
- `ValueError`, `KeyError`, and `FileNotFoundError` print `pyfmi: <message>` on
  stderr and return 1; argparse keeps exit 2; anything unexpected propagates.

The CLI adds no behaviour the API lacks: the handler calls the generator with
the parsed arguments.

The four source-taking commands (`model-description`, `c-headers`, `c-runtime`,
`modelica`) live in `pyfmi_sysml` as `pyfmi-sysml`. They load the source there,
build the `Reduction`, and call these generators; nothing here parses SysML.
