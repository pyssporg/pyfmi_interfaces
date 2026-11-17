---
id: INFO-014
type: info
title: Which pyssp_standard gaps stay open
summary: Two upstream elements are unmodelled — SourceFiles and VendorAnnotations; the FMU facade owns staging, layout, and packaging.
date: 2026-11-17
status: current
---

# Which pyssp_standard gaps stay open

- **Question:** which limits in the pinned `experimental-pyssp-standard` build
  still shape what this package can emit?
- **Resolved:** `FMU.stage` carries every group, including `sources/`, and owns
  validation, layout, and placement; `FMU.package` owns staging and archive
  verification.
- This package therefore keeps no packaging module, no local layout or
  validation code, and no policy wrapper.
- The CLI calls `FMU.package` directly and pins `linux64` and FMI 2.0 at the
  call site; determinism stays with `package_archive`.
- **Open:** the FMI 2.0 model allows `SourceFiles` (`fileName`, `language`, and
  related attributes) and vendor annotations; the pinned document model exposes
  neither.
- The generated modelDescription therefore carries no `SourceFiles` entry and no
  `VendorAnnotations` element.
- Two capabilities stay blocked: listing the generated C++17 runtime sources and
  their language in `SourceFiles`, and carrying author, version, and license
  annotations a consumer may read.
- The fix belongs upstream: extend the model objects and the codec, then consume
  them here.
- Adding either element by hand-written XML is not an acceptable workaround.
- **Verification:** re-check both gaps after any `pyssp_standard` version bump;
  the pinned URL is v0.9.3.dev0.
