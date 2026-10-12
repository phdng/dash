# Session-421 — macOS CI negative-width usable geometry regression fix

Started from clean `chore/reconstruction-build-ci` after Session-420. User supplied actual macOS compiled Objective-C smoke failure at 2026-10-12 11:12:21: `FAIL: invalid usable geometry vector 2`, exit 1. Vector 2 is `CGRectMake(10, 10, -1, 180)` in `scripts/hostflow_preflight_smoke.m`.

## Diagnosis
The `DDHostInitialGeometryBounds` input guard (and related helpers) checked finiteness and `CGRectIsEmpty` but did not explicitly reject negative width/height. On macOS CoreGraphics, negative-size CGRect handling differs from assumptions underlying the check. Harden the pipeline at ingress so a negative width cannot be accepted regardless of `CGRectIsEmpty` behavior. The local environment lacks a usable macOS native smoke runner; this is a targeted fix pending CI confirmation.

## Changes
- `HostFlowAdapter.m`: added static `DDHostRectHasFinitePositiveSize` checking finite x/y/w/h plus width > 0 and height > 0. Reused in 23D94 initial selection, dock measured inputs, usable fallback, 26654 edge detection and trim, 269FC covered adjacency and early guard, and geometry-for-rects. `DDHostTrimUsableBoundsForDock` now returns before calling `CGRectIntersection` on rejected/non-edge strips.
- `scripts/hostflow_preflight_smoke.m`: expanded rejected usable matrix with negative height; dynamic array length; validated four paths for each rejected vector: initial geometry failure and output preservation, dock edge and trim failure, covered `no-window` and output preservation, and packed-state resolver `invalid-geometry` and output preservation. Added diagnostic output of label, dimensions and guard results if CI still fails.
- `scripts/test_dock_geometry_vectors.py`: added negative-height vector and checked trimming/final coverage fallback for malformed usable bounds.

## Verification
PASS `python scripts/verify_reconstruction.py`: 30 reconstruction modules. PASS `python scripts/test_dock_geometry_vectors.py`: 8 tests. PASS `git diff --check`. Native `xcrun clang` smoke and Theos arm64 are not available here and have not been rerun. No commit or push. Next: re-run macOS GitHub Actions and inspect first failing vector if any.
