# Session-406 — Recover 23D94 initial geometry branch precedence

Started from clean `chore/reconstruction-build-ci`, after user confirmed preceding build was stable.

## Original evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/23D94.c`: invalid shell (empty or under 40pt), or shell outside usable bounds inset(-1pt), selects `display-unmeasured-dock` vs `measured-dock-nofrome`; contained shell with width < usableWidth-1 or height < usableHeight-1 selects `carplay-subrect` before checking measured dock; otherwise selects `measured-dock` or `carplay-fullscreen`.

## Changes
- Exported `DDHostInitialGeometryReason` in DuoDashShared.h; implemented source-order pure-data classifier in compiled HostFlowAdapter.m.
- Added Objective-C smoke checks for missing shell with/without dock, valid subrect priority with dock, fullscreen with/without dock, outside and undersized shell.
- Added structural verifier registry entry.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 tests), PASS `git diff --check`. macOS compiled Objective-C, Theos arm64 and physical CarPlay unverified this turn. No commit/push.
