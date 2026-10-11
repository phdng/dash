# Session-383 — Compose recovered 218D8 prepared-host gates

Continued uncommitted Sessions 379–382 on `chore/reconstruction-build-ci`.

## Source evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/218D8.c:213–295` compares normalized vs hosted Bundle IDs and first dimensions, then (subject to additional private guards) compares desired per-slot CarPlay UI booleans from `sub_22E40` against current hosted flags. A difference forces the full-host path.

## Implementation
- Added `DDHostPreparedSlotsAndFlagsMatch` in DuoDashShared.h and HostFlowAdapter.m combining `DDHostPreparedSlotsReady` and `DDHostPreparedCarPlayFlagsMatch`, with no access to private host state.
- Added smoke assertions covering success, flag disagreement, BID mismatch, and undersized first dimension.
- Added header/implementation export contract to reconstruction structural verifier.
- Do not claim this fully authorizes reuse: `sub_22D64`, private flags, and actual display/presentation state remain external.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. macOS Objective-C smoke and arm64 Theos CI not executed here. No commit/push.
