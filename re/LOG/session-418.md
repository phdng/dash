# Session-418 — Native smoke parity for malformed usable bounds and dock states

Continued uncommitted Sessions 411–417 on `chore/reconstruction-build-ci`.

## Changes
Extended `scripts/hostflow_preflight_smoke.m` with a four-vector malformed CarPlay usable bounds loop (NaN x, infinite y, negative width and zero height), verifying `invalid-geometry` does not write initial/resolved geometry or coverage label. Added a three-vector packed dock state failure loop (absent state, zero width/height and zero height) checking full usable fallback, final `display-unmeasured-dock`, intermediate `no-strip-published` and matching CGRect output.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (6 methods), PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. Objective-C smoke is source-updated but compiled macOS run, arm64 Theos and CarPlay hardware remain unverified. No commit or push.
