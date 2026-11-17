---
id: CP-003
type: capability
title: Errors and refusals
summary: Ambiguous roots, flat parameters, non-fixed lists, flattened connectors, naive clocks, and platform or identifier mismatches are refused with an actionable message.
date: 2026-11-17
status: current
---

# Errors and refusals

Generation fails rather than guessing; each refusal names the offending model element or path.

Model errors:

- several part definitions could be the composition root — several marked
  `:> FmuModel` definitions, or several container roots — or none: pass
  `composition=`;
- an unresolved port definition on a leaf part;
- a flat parameter attribute where the parameter dialect is required;
- a port definition that sets the flat-connector control;
- a multiplicity that is not a fixed length, or is not an integer;
- a requested `component` that is not exported.

Time errors:

- a naive `generation_time`; the value must carry a timezone so the artifact does not depend on the host's locality;
- a malformed CLI generation time (exit 2 from argparse).

Packaging errors, raised by `pyssp_standard.FMU` and surfaced by `pyfmi package`:

- a platform token containing a path separator (the CLI admits only `linux64`);
- a `modelDescription.xml` that is missing, not UTF-8, not valid FMI 2.0 XML, or not `fmiVersion="2.0"`;
- no `CoSimulation`/`ModelExchange` element, or one without `modelIdentifier`;
- a `modelIdentifier` that does not equal the binary stem;
- a missing `--binary`, `--header`, `--resource`, or `--documentation` path;
- duplicate file names inside one archive folder.

The CLI reports handled errors as `pyfmi: <message>` on stderr with exit 1. Argument errors keep argparse's exit 2. Unexpected exceptions propagate.
