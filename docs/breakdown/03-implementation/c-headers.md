---
id: INFO-006
type: info
title: C header generation
summary: generate_c_headers writes one plain-C common header plus one header per component; c-runtime runs it too, so c-headers is the header-only command.
date: 2026-11-17
status: current
---

# C header generation

`generate_c_headers()` writes `<prefix>_InterfaceCommon.h`, then one
`<prefix>_<Component>.h` per exported component; `--component NAME` keeps one
plus the common header, and an unknown name raises `KeyError`. `c-runtime` calls
it, so both commands regenerate these headers and `c-headers` is header-only.
`prefix` defaults to the package name; `header_stem()` keeps a direct FMU model
at `Generator.h`, not `Generator_Generator.h`, and owns the file/identifier rule.

Common header: include guard, `stdbool.h`/`stddef.h`/`stdint.h`; one
`typedef struct <prefix>_<PortDefinition>` per distinct port definition in
first-use order; the `<prefix>_DataType` enum (`NONE`, `REAL`, `INTEGER`,
`BOOLEAN`, `STRING`); and `<prefix>_VrMapping` (`void* data`, `DataType type`,
`bool writable`) in plain C.

Component header: `<PREFIX>_<COMPONENT>_GUID` matching the modelDescription
guid, `<PREFIX>_<COMPONENT>_VR_<VARIABLE> = <vr>` per variable, `VrCount`, and
inside `#ifdef __cplusplus` a `<prefix>_<Component>_Instance` with `vr_map[]`,
parameter defaults, one payload per port, and `<stem>_initialize_vr_map()`.

Deliberate details:

- outputs map `writable=false`; parameters and inputs `true`;
- C/C++ keywords gain a trailing underscore on the struct member only;
- arrays are fixed-size, exactly `array` elements and always zero-based;
  `--base-index N` shifts only the FMI element names and VR enum labels;
- string defaults are C-escaped and quoted.

The common header is C11; only the instance helper needs C++17. Both are
checked with `-fsyntax-only` in `tests/test_c_headers.py`.
