---
id: CP-003
type: capability
title: Errors and refusals
summary: A naive clock, an unexported component, and platform or identifier mismatches are refused with an actionable message.
date: 2026-11-19
status: current
---

# Errors and refusals

Generation fails rather than guessing; each refusal names the offending model element or path.

Generation errors:

- a requested `component` that is not exported.

Time errors:

- a naive `generation_time`; the value must carry a timezone so the artifact does not depend on the host's locality.

Packaging errors, raised by `pyssp_standard.FMU` and surfaced by `pyfmi package`:

- a platform token containing a path separator (the CLI admits only `linux64`);
- a `modelDescription.xml` that is missing, not UTF-8, not valid FMI 2.0 XML, or not `fmiVersion="2.0"`;
- no `CoSimulation`/`ModelExchange` element, or one without `modelIdentifier`;
- a `modelIdentifier` that does not equal the binary stem;
- a missing `--binary`, `--header`, `--resource`, or `--documentation` path;
- duplicate file names inside one archive folder.

The CLI reports handled errors as `pyfmi: <message>` on stderr with exit 1. Argument errors keep argparse's exit 2. Unexpected exceptions propagate.
