# Session-389 — Remaining usable rectangle after dock clipping

Continued uncommitted Sessions 385–388 on `chore/reconstruction-build-ci`.

## Decompiled evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/26654.c` intersects dock strip with usable bounds, checks coverage within 2pt and residual dimension >=40pt. Accepted left/right/top/bottom strip yields a surviving area; the return values in original decompilation are ABI-split and therefore source semantics are modeled as a pure-data CGRect helper, not as a private call.

## Changes
- Exported `DDHostTrimUsableBoundsForDock` in DuoDashShared.h and implemented in compiled HostFlowAdapter.m. Derives surviving CGRect from the original bounds and the overlap for each accepted edge.
- Refuses nonedge, outside, degenerate strips and preserves caller's output on failure.
- Added smoke coverage for each edge, middle/nonedge, degenerate, and stable output on failure.
- Registered new helper in structural reconstruction verifier.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python -m py_compile scripts/verify_reconstruction.py`, PASS `git diff --check`. macOS compiled Objective-C test, Theos arm64, and device CarPlay unconfirmed. No commit/push.
