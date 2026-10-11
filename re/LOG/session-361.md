# Session-361 — Prepared-host BID + dimension gate from 218D8

Clean workspace at start on `chore/reconstruction-build-ci`.

## Direct evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/218D8.c:208–236` shows private 3DD4C BID normalization, BID comparison per index (missing BIDs normalize to empty), and one scalar from v20 for each slot, with v20 stepping by two. In contrast, `208F4.c:228` requires both adjacent dimensions per slot for a switch.

## Compiled Objective-C changes
- Exported `DDHostPreparedSlotsReady` in `DuoDashShared.h` and implemented in `HostFlowAdapter.m`.
- Composes existing prepared BID comparison with caller-supplied one-dimension-per-slot size validation. No private geometry reads, 3DD4C invocation, or UI mutation.
- Added compiled self-test assertions: successful matching BIDs plus sizes, undersized second slot, missing slot measurement and mismatched BIDs.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `git diff --check`. macOS executable and arm64 Theos CI not run. No commit/push.
