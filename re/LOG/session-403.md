# Session-403 — Link CoreGraphics for macOS smoke executables

## CI failure
arm64 linker reports undefined symbols `_CGRectContainsRect`, `_CGRectEqualToRect`, `_CGRectGet*`, `_CGRectInset`, `_CGRectIntersection`, `_CGRectIsEmpty`, `_CGRectIsNull`, `_CGRectZero` referenced by HostFlowAdapter.m and smoke harness.

## Fix
Updated `.github/workflows/build.yml` so BOTH macOS smoke link invocations link `-framework CoreGraphics` in addition to Foundation and CoreFoundation. The compile-only arm64 steps stay unchanged; no Objective-C source edits needed.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 test methods), PASS `git diff --check`. Verified both linker lines contain `-framework CoreGraphics`. Actual macOS clang link, Theos arm64 build and physical device remain unverified. No commit/push.
