# Session-385 — 23D94 carplay-subrect branch

Began with clean `chore/reconstruction-build-ci` working tree (previous sessions committed externally).

## Direct source evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/23D94.c` checks for nonempty shell >=40pt, containment within `CGRectInset(carPlayUsableBounds, -1, -1)`, then `shellWidth < usableWidth - 1` OR `shellHeight < usableHeight - 1` and assigns branch label `carplay-subrect`. Private calls to measured dock geometry and final layout are not safe to infer from this isolated branch.

## Changes
- Added `DDHostGeometryIsCarPlaySubrect` to DuoDashShared.h and HostFlowAdapter.m, accepting dimension scalar values and a caller-provided containment result; rejects nonfinite numbers.
- Added smoke test for width/height subrect, exact 1-point threshold, containment false and undersized shell.
- Registered new function with structural reconstruction verifier.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `git diff --check`. macOS Objective-C smoke and arm64 Theos CI not executed. No commit/push.
