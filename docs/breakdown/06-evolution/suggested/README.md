# Suggested — candidate improvements

Open IMP candidates, each a scoped suggestion with no approval attached. A
candidate moves to `selected/` when it takes a slot, and only then gets a plan.
`implemented/` is a closed lookup, never a backlog.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **IMP-001** [Interface hash for the exported artifact set](interface-hash-for-the-exported-artifact-set.md) — Emit a deterministic hash of the reduced variable set so a consumer can tell an interface changed while the guid stays frozen.
- **IMP-002** [Re-pin pycps-sysml2 to the v0.3.0 release wheel](re-pin-pycps-sysml2-to-v0-3-0.md) — The code reads the 0.3.0 experiment API while pyproject.toml still points at the v0.2.0 wheel, so a built wheel is importable only against a 0.3.0 dialect in the environment.
<!-- pb:index:end -->
