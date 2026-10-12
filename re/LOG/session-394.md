# Session-394 — 23D94 measured dock fallback branch

Continued uncommitted Sessions 390–393 on `chore/reconstruction-build-ci`.

## Evidence
Original `23D94.c` branches to `LABEL_15` on missing or undersized shell, or shell outside `CGRectInset(carPlayUsableBounds, -1, -1)` when `sub_83FC` supplies a measured dock; it then calls `sub_26654` with `carPlayUsableBounds` as the rectangle to clip. The original without-dock fallback is separate and this helper does not claim it.

## Changes
- Added `DDHostTrimFallbackCarPlayBoundsForDockState` to public header and HostFlowAdapter.m, requiring the evidenced invalid/outside shell condition and composed packed state/edge trim.
- Added smoke tests for empty/undersized/outside shell, valid contained shell rejection, invalid state and stable output on failure.
- Added helper to reconstruction verifier export contract. No private state reads or UI mutation.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `python -m py_compile scripts/verify_reconstruction.py`; PASS `git diff --check`. Compiled macOS, Theos arm64 and device tests unverified. No commit/push.
