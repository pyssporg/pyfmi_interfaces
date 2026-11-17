---
id: INFO-004
type: info
title: Determinism model
summary: A uuid5 guid from a frozen namespace string, a fixed default epoch, and an epoch-stamped sorted archive make every artifact reproducible.
date: 2026-11-17
status: current
---

# Determinism model

Three inputs could otherwise vary between runs; each is pinned.

`component_guid()` is `uuid5(NAMESPACE_URL,
"pyssp_sysml2/<composition>/<component>")`, formatted in braces, for a component
exported by a container root. A direct FMU model has no container level, so its
guid is `uuid5(NAMESPACE_URL, "pyssp_sysml2/<definition>")` and its `modelName`
is the bare definition name; `ExportIdentity` derives both. The `pyssp_sysml2/`
prefix is frozen: a migrated build keeps every guid, and changing the prefix or
the component spelling breaks stored guids.

`generation_time` is injected on the Python API and on
`pyfmi model-description --generation-time`; `None` means the fixed default
epoch `2000-01-01T00:00:00Z`, never a wall-clock read, so an un-injected build
is byte-reproducible. A naive datetime is refused, and `utc_now()` is the
opt-in wall clock. The document is stamped `YYYY-MM-DDTHH:MM:SSZ`; equal
injected times are byte-identical.

`pyfmi package` calls `pyssp_standard`'s `FMU.package`, which stages the tree
and calls `package_archive`: entries are sorted, every entry is stamped with the
FMI epoch (2000-01-01), and modes are normalized to `0o644`, with `0o755` under
`binaries/`. A fresh-stage repack is byte-identical; filesystem mtimes do not
leak into the bytes. Ordering is fixed outside the archive too: components are
exported sorted by name, ports and fields follow declaration order, and Modelica
package files are returned sorted.
