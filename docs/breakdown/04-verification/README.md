---
title: Verification
summary: The five test levels plus the slow qualifier, the cross-artifact gate, the compiler and Modelica oracles, and the fixture and golden policy.
---

# Verification

How the artifacts are proven: the test ladder over modelDescription, headers,
the C++17 runtime, the Modelica package, and the packed `.fmu`; the
consistency gate; the external oracles; and the rules a fixture follows.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **TEST-001** [Test strategy](test-strategy.md) — Six pytest markers, five levels plus a slow qualifier; each owns a distinct fault class, the component level covers modelDescription, headers, the C++17 runtime, the Modelica package, and the packed .fmu, and goldens are the default gate.
- **TEST-002** [Cross-artifact consistency gate](cross-artifact-gate.md) — check_artifacts() reads modelDescription, the C header, and the packed FMU with independent parsers and proves they describe one component; mutation tests prove it fails when one is broken.
- **TEST-003** [Oracles, fixtures, and goldens](oracles-and-fixtures.md) — gcc and g++ syntax-check the headers, g++ compiles, links, and executes the runtime harness, fmpy validates and loads the packaged FMU, omc checkModel proves the Modelica package and buildModel the model seam, and seven shared fixtures carry case records and byte-compared goldens.
<!-- pb:index:end -->
