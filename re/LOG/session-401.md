# Session-401 — Portable dock geometry vectors in CI

Continued uncommitted Sessions 390–400 on `chore/reconstruction-build-ci`.

## Changes
- Added `scripts/test_dock_geometry_vectors.py`, a pure Python implementation of 269FC geometry-vector checks independent of the Objective-C helper: four sides, 1pt expanded usable region, 2pt adjacency, 2.1pt non-adjacency, out-of-bounds exclusion.
- Added `Verify dock geometry vectors` job step before the compiled macOS smoke step in `.github/workflows/build.yml` and added the script to both push and PR path filters.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (2 unittest methods), PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. macOS Objective-C compiled smoke, Theos arm64 and physical CarPlay unverified. No commit/push.
