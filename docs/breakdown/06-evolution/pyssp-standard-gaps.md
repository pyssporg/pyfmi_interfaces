---
id: INFO-014
type: info
title: Which pyssp_standard gaps stay open
summary: SourceFiles stays unmodelled upstream; VendorAnnotations is bridged locally by the tool-independent annotation layer in the one document emitter, and the FMU facade owns staging, layout, and packaging.
date: 2026-11-22
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
- **Open upstream:** the FMI 2.0 model allows `SourceFiles` (`fileName`,
  `language`, and related attributes); the pinned document model exposes it
  nowhere.
- The generated modelDescription therefore carries no `SourceFiles` entry.
  Listing the generated C++17 runtime sources and their language stays blocked;
  the fix belongs upstream, and hand-written XML is not an acceptable
  workaround.
- **Bridged locally:** the pinned document model also exposes no
  `VendorAnnotations`. `core/annotations.py` and the one emitter in
  `model_description/document.py` add the ordered, tool-independent annotation
  view and its codec (`INFO-020`); no tool name is known there and the payload
  is opaque. This is a deliberate local bridge, not a claim that upstream models
  the element: the reduction-driven `generate_model_description()` still emits
  no annotation because it has none to carry.
- **Verification:** re-check both gaps after any `pyssp_standard` version bump;
  the pinned URL is v0.9.4.dev0.
