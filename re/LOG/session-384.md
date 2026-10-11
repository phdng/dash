# Session-384 — Port geometry mismatch guard from original 22D64

Continued uncommitted Sessions 379–383 on `chore/reconstruction-build-ci`.

## Original decompiled evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/22D64.c` (used by `208F4` and `218D8`): if saved shell width or height is below 40, or both shell dimension differences are <=1 point, compare the current CarPlay display dimensions to layout dimensions recalculated by `sub_23D94`; otherwise mismatch immediately. The display comparison uses <=1 point per axis. Private measurements/calculation are outside this port.

## Changes
- Exported `DDHostDisplayGeometryMismatch` (eight double input dimensions) in DuoDashShared.h and implemented in compiled HostFlowAdapter.m, using fabs and original comparison thresholds.
- Added macOS Objective-C smoke checks for exact matches, 1-point inclusive tolerances, >1-point mismatches, and saved shell below 40 forcing display comparison.
- Registered helper with structural verifier.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. macOS Objective-C smoke, arm64 Theos CI and live CarPlay not executed. No commit/push.
