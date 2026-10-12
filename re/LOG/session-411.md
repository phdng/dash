# Session-411 — Packed-state CarPlay dock geometry pipeline

Started from clean `chore/reconstruction-build-ci` after Session-410, with user requesting multiple related processing paths per iteration.

## Implementation
- Exported/implemented `DDHostResolvedGeometryForDockState` as a pure-data end-to-end integration of original 83FC packed notification geometry, 23D94 initial CarPlay region selection, 26654 dock trimming, 269FC covered expansion, and final diagnostic labels.
- Successful packed state decoding supplies both measured and published flags. Zero state and state with invalid width/height are treated as unmeasured/unpublished. Caller owns all private notification calls; no runtime UI mutation.
- Tests check decoded left dock trimming, no-exit precedence, unmeasured/unpublished fallback, malformed packed state, and no output changes on invalid usable geometry. Export added to structural verifier.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 tests), PASS `git diff --check` (CRLF warnings only). Compiled macOS Objective-C smoke, Theos arm64, and physical CarPlay unverified. No commit/push.
