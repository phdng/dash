# Session-396 — 269FC adjacent dock edge classification

Continued Sessions 390–395 on `chore/reconstruction-build-ci`.

## Source evidence
Original `Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/269FC.c` checks dock extent across candidate height or width within 2pt and adjacency of its opposite edge to a candidate edge within 2pt, before expanding and checking against CarPlay usable bounds. Those subsequent checks remain separate.

## Changes
- Added `DDHostDockAdjacentEdge` to public header and compiled HostFlowAdapter.m, returning left/right/top/bottom or nil with fail-closed finite/empty and already-inside guards.
- Added smoke tests for four edges, separation >2pt, insufficient span and already-contained dock.
- Updated structural reconstruction verifier export check.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python -m py_compile scripts/verify_reconstruction.py`, PASS `git diff --check`. macOS Objective-C smoke and Theos arm64/device not executed. No commit/push.
