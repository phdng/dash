# Session-416 — Match portable 269FC coverage classification to Objective-C

Continued Sessions 411–415 uncommitted on `chore/reconstruction-build-ci`.

## Fixes and scope
- Found `resolve_state` in `scripts/test_dock_geometry_vectors.py` incorrectly returned synthetic `not-covered` for several source-distinct 269FC outcomes.
- Added `coverage_decision`, a standalone coordinate-based reference returning `no-exit`, `no-strip-published`, `already-inside`, `strip-not-adjacent`, `outside-usable` or `covered`.
- End-to-end oracle now forwards these branch reasons and preserves initial result for non-covered states.
- Added branch-matrix and packed-state path tests to ensure final diagnostic label and initial/final CGRect do not change on already-inside/nonadjacent rejection.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (5 tests), PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. macOS compiled Objective-C smoke, Theos arm64 CI and CarPlay device unverified. No commit/push.
