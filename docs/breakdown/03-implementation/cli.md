---
id: INFO-009
type: info
title: CLI
summary: The pyfmi entry point collects one COMMANDS registry per artifact family, has five subcommands, prints one written path per line, exits 1 on handled model or input errors, and 2 on argument errors.
date: 2026-11-17
status: current
---

# CLI

`pyproject.toml` maps `pyfmi = "pyfmi_sysml2.cli:main"`. `cli.py` is a thin
dispatcher: it imports each family's `COMMANDS` tuple, concatenates them in
`--help` order, and hands the result to `core.cli.run()`. It parses no
arguments of its own.

`core/cli.py` owns the shape every family registers against:

- `Command(name, help, description, configure, handler)`, one per artifact;
- the shared option helpers — `add_source`, `add_output`, `add_composition`,
  `add_base_index`, `add_generation_time` — and `print_paths`;
- `build_parser()` and `run()`, including the exit-code policy.

A family's `__init__.py` declares its options in a `configure` callback and its
work in a `handler` that calls one generator. The five subcommands:

- `pyfmi model-description SOURCE [-o OUT] [--composition NAME]
  [--base-index N] [--component NAME] [--generation-time ISO8601]`
- `pyfmi c-headers SOURCE [-o OUT] [--composition NAME] [--base-index N]
  [--prefix NAME]`
- `pyfmi c-runtime SOURCE [-o OUT] [--composition NAME] [--base-index N]
  [--prefix NAME] [--omit NAME[,NAME...]]`
- `pyfmi modelica SOURCE [-o OUT] [--composition NAME] [--package NAME]
  [--within NAME]`
- `pyfmi package -o OUT --model-description PATH --binary PATH
  [--platform NAME] [--header PATH] [--resource PATH] [--documentation PATH]`

Behaviour:

- `SOURCE` is a `.sysml` file or a directory of them, loaded by `pycps_sysml2`.
- The four generating subcommands default to `build/`; `package` requires an
  output path.
- `--header`, `--resource`, `--documentation`, and `--omit` are repeatable.
- Every written path is printed on stdout, one per line.
- `ValueError`, `KeyError`, and `FileNotFoundError` print `pyfmi: <message>` on
  stderr and return 1; argparse keeps exit 2; anything unexpected propagates.
- `--generation-time` accepts the emitted `...Z` form or an ISO 8601 form with
  an offset; a naive time is rejected.
- `--base-index` shifts the emitted array index; 0 is the default, 1 targets
  OMC-built Modelica FMUs.

The CLI adds no behaviour the API lacks: each handler calls one generator with
the parsed arguments, and a family that registers no command has no shell
surface.
