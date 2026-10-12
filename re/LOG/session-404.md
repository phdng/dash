# Session-404 — Fix lipo arm64 verification argument order

## CI failure
macOS Xcode 26.6 `lipo` rejects `xcrun lipo -verify_arch arm64 "$RUNNER_TEMP/hostflow_preflight_smoke_arm64"` because the executable path is parsed as an additional architecture flag.

## Changes
- `.github/workflows/build.yml`: `xcrun lipo "$RUNNER_TEMP/hostflow_preflight_smoke_arm64" -verify_arch arm64`.
- `scripts/verify_reconstruction.py`: updated hardcoded CI contract to expect the valid argument order.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 tests), PASS `git diff --check`. Native macOS CI rerun pending. No commit/push.
