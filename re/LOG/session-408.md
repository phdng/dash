# Session-408 — Compose 23D94 initial output and 269FC covered adjustment

Starting from clean `chore/reconstruction-build-ci` after Session-407.

## Evidence
Original `23D94.c` first stores initial bounds through its `a3` pointer, then invokes `sub_269FC` and uses the covered adjustment separately. The initial geometry source-order decisions and pure-data coverage classifier already existed.

## Changes
- Exported and implemented `DDHostResolvedGeometryForDock`, composing initial bounds with the source-derived covered decision while preserving both original initial and later resolved rectangles.
- If invalid usable geometry prevents calculation, returns `invalid-geometry` without writing either caller output. Other non-covered reasons keep `resolvedRect` equal to `initialRect`.
- Added Objective-C smoke checks for covered expansion, unavailable dock, non-adjacent strip, and invalid-input no mutation; registered helper with structural verifier.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `python scripts/test_dock_geometry_vectors.py` (2 tests); PASS `git diff --check`. macOS Objective-C smoke, Theos arm64 and device CarPlay not run here. No commit/push.
