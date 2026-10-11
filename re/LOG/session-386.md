# Session-386 — 23D94 CGRect expanded usable bounds containment

Continued Session-385 on `chore/reconstruction-build-ci` with uncommitted local edits.

## Decompiled source evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/23D94.c`: shell rect `v46` is compared with `CGRectInset(carPlayUsableBounds, -1, -1)` using `CGRectContainsRect`. Only on a contained shell of >=40pt dimensions does the direct carplay-subrect branch apply if either dimension is >1pt smaller.

## Implementation
- Added exported `DDHostGeometryIsCarPlaySubrectForRects(CGRect shellBounds, CGRect usableBounds)` to header and compiled HostFlowAdapter.m; checks finite/empty rectangles then delegates to 385 subrect threshold helper with real CGRectContainsRect outcome.
- Added mock smoke assertions for inside, outside, inclusive 1-point boundary, and undersized shell.
- Registered new export in verifier. Private dock measurement or final geometry calculation is still not implemented.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. macOS Objective-C compiled tests and Theos arm64 CI unverified. No commit/push.
