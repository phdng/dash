# Session-407 — Compose initial 23D94 CarPlay rectangle

Continued Session-406 on `chore/reconstruction-build-ci`.

## Evidence
Original `23D94.c` chooses shell vs usable rectangle by initial reason, then invokes `26654.c` to trim only on measured-dock and measured-dock-nofrome routes. A valid `carplay-subrect` is preserved before dock trimming. `26654.c` non-edge strips leave base geometry unchanged. The later `269FC` covered adjustment is not included here.

## Changes
- Added `DDHostInitialGeometryBounds(shellBounds,usableBounds,dockMeasured,dockBounds,outRect)` to public header and compiled HostFlowAdapter.m, composing prior source-derived decision and clip helpers.
- Extended Objective-C smoke for unmeasured fallback, measured dock fallback, preserved subrect, fullscreen dock clipping, measured non-edge retention and rejected unusable CGRect.
- Added helper to structural verifier export list.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py`, PASS `git diff --check`. macOS Objective-C compile/run, Theos arm64 and physical CarPlay remain unverified. No commit/push.
