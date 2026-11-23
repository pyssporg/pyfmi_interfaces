---
title: Implementation
summary: Per-module notes for the four artifact families and the CLI, plus the pyssp_standard API facts the code depends on.
---

# Implementation

What each module does, and the library behaviours it relies on.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **INFO-005** [modelDescription generation](model-description.md) — model_description/document.py is the one emitter: it assembles a pyssp_standard FMI 2 document from the reduction, serializes, validates, and writes it.
- **INFO-006** [C header generation](c-headers.md) — generate_c_headers writes one plain-C common header plus one header per component; generate_c_runtime runs it too, so generate_c_headers is the header-only entry point.
- **INFO-007** [Modelica generation](modelica.md) — generate_modelica writes a configurable root package with undirected connectors plus, per component, a generated partial model whose port instances carry direction, and an implementer-owned model created once.
- **INFO-008** [FMU packaging](packaging.md) — pyfmi_interfaces has no archive writer and no local staging layer; pyssp_standard's FMU.stage and FMU.package own layout, validation, staging, archive verification, and determinism, and the CLI calls FMU.package directly.
- **INFO-009** [CLI](cli.md) — The pyfmi entry point registers the package family and has one subcommand; it prints one written path per line, exits 1 on handled input errors, and 2 on argument errors.
- **INFO-010** [pyssp_standard API facts](pyssp-standard-api.md) — The codec returns str, interface type and capabilities are both required, Boolean starts are text, ModelStructure indexes are 1-based, and package_archive normalizes modes and epoch.
- **INFO-015** [C++ runtime generation and model hooks](c-runtime-generation-and-model-hooks.md) — c/runtime.py writes a C++17 FMI 2.0 CoSimulation runtime with 38 entry points and a five-hook model seam plus implementer-owned user_data, regenerates the C headers, copies the FMI headers, and creates the model file once.
- **INFO-020** [Tool annotations](tool-annotations.md) — The ordered, tool-independent VendorAnnotations layer in the one modelDescription emitter, with verbatim payloads, one code path, and schema validation.
<!-- pb:index:end -->
