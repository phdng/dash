# Session-397 — 269FC covered expanded rectangle gate

Continued dirty Sessions 390–396 on `chore/reconstruction-build-ci`.

## Original evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/269FC.c`: after dock adjacency matching (2pt), constructs expanded candidate rectangle reaching the dock, checks it against `CGRectInset(carPlayUsableBounds,-1,-1)` and labels the accepted result `covered`; otherwise `outside-usable`.

## Changes
- Exported `DDHostDockCoveredExpandedBounds` in DuoDashShared.h and implemented in compiled HostFlowAdapter.m, reusing prior `DDHostDockAdjacentEdge` and enforcing final CarPlay containment.
- Added macOS smoke coverage for left/right/top/bottom, rejected boundary exceedance and preservation of output on failure.
- Added structural verifier helper export contract. No private UI manipulation or notification acquisition.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python -m py_compile scripts/verify_reconstruction.py`, PASS `git diff --check`. macOS compiled smoke, Theos arm64 and CarPlay device unverified. No commit/push.
