# Session-405 — Restore CoreGraphics declarations for iOS arm64 tweak compilation

## Reported build error
Theos iOS arm64 compiling `re/RECONSTRUCTION/HostFlowAdapter.m` fails with undeclared functions `CGRectIsEmpty`, `CGRectIntersection`, `CGRectGetMinX`, `CGRectMake` and related CGRect APIs. Shared header imported Foundation and CoreFoundation but not CoreGraphics.

## Fix
- `re/RECONSTRUCTION/DuoDashShared.h`: explicitly import `<CoreGraphics/CoreGraphics.h>` for declarations of CGRect geometry APIs used throughout the host adapter and shared header consumers.
- `Makefile`: add `CoreGraphics` to `DuoDashReconstruction_FRAMEWORKS` to link the iOS tweak against the framework.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `python scripts/test_dock_geometry_vectors.py` (2 tests); PASS `git diff --check`. Theos arm64 compilation not available in the Windows workspace; rerun macOS CI to confirm. No commit/push.
