---
id: INFO-014
type: info
title: pyssp_standard gaps blocking v0.2.0
summary: One upstream gap remains: SourceFiles and vendor annotation content is not modelled. The FMU facade now owns staging and packaging.
date: 2026-11-05
status: current
---

# pyssp_standard gaps blocking v0.2.0

One limitation in the pinned `experimental-pyssp-standard` build shapes what
this library can emit. It is not worked around by hand-writing XML.

## Sources and the FMU facade (resolved)

`FMU.stage` carries every group, including `sources/`, and owns validation,
layout, and placement; `FMU.package` owns staging and archive verification. This
package therefore keeps no packaging module, no local layout or validation code,
and no policy wrapper: the CLI calls `FMU.package` directly and pins `linux64`
and FMI 2.0 at the call site. Determinism stays with `package_archive`.

## SourceFiles and annotations

The FMI 2.0 model allows `SourceFiles` (`fileName`, `language`, and related
attributes) and vendor annotations. The pinned document model exposes neither,
so the generated modelDescription carries no `SourceFiles` entry and no
`VendorAnnotations`. That is acceptable for v0.1.0 because the binary is built
outside this library, but it blocks two v0.2.0 goals:

- declaring the C source and its language alongside the binary;
- carrying author, version, and license annotations that a consumer may read.

The fix belongs upstream: extend the model objects and the codec, then consume
them here. Until then neither element is emitted, and adding one by hand-written
XML is not an acceptable workaround.

## Verification

Re-check the `SourceFiles`/annotation gap after any `pyssp_standard` version
bump; the pinned URL is v0.9.3.dev0. Source placement is no longer a gap: the
facade accepts `sources/`, and no local wrapper remains between the CLI and the
facade.
