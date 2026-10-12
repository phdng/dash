# Session-409 — Source-derived 23D94 final dock label synthesis

Continued uncommitted Session-408 on `chore/reconstruction-build-ci`.

## Source evidence
Original `Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/23D94.c` checks `sub_269FC` label `covered` before selecting diagnostic names. It maps `carplay-subrect`, `measured-dock`, `measured-dock-nofrome`, `single-app` to suffixed `+dock` labels, otherwise `covered+dock`; non-covered cases retain the initial label.

## Changes
- Exported and implemented `DDHostFinalGeometryReason(initialReason, coverageReason)` as a pure-data label resolver.
- Added Objective-C smoke assertions covering all four specific labels, default and null input, and non-covered label preservation.
- Added helper to structural verifier export list.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 tests), PASS `git diff --check`. Compiled macOS smoke, Theos arm64 CI and CarPlay device not executed here. No commit/push.
