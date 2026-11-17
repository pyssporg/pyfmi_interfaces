<!-- GENERATED FILE — do not edit. Regenerate with `pb registers`. -->

# Decision Stream

Flat, dated history of every committed design choice. Current state lives
in the layer leaves named by each record's `state:` field.

Records live in the cold-storage archive; extract one with `pb archive read <ID>`.

## By Layer

### Intent

- **AD-003** — Generate the FMI runtime, keep model physics with the implementer · accepted · 2026-11-17 · `AD-003`
  The package emits a C++17 FMI 2.0 CoSimulation runtime from the variable set and leaves model behaviour to a file created once, while never compiling it.

### Product

- **AD-002** — inout and undirected ports become inputs · accepted · 2026-11-05 · `AD-002`
  FMI 2.0 has no bidirectional scalar, so inout and undirected ports are emitted as inputs and the Modelica connector keeps no direction qualifier.
- **AD-004** — Inputs carry neutral starts; non-Real ports are discrete · accepted · 2026-11-17 · `AD-004`
  FMI 2.0 requires an input start and forbids continuous variability for non-Real types, so the reduction emits 0/false/"" starts and discrete variability.

### Architecture

- **AD-001** — The guid namespace string stays literally pyssp_sysml2 · accepted · 2026-11-05 · `AD-001`
  The FMI guid is uuid5(NAMESPACE_URL, "pyssp_sysml2/<composition>/<component>") even though the package is named pyfmi_sysml2.
