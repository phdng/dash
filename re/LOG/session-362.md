# Session-362 — Prepared-host active-slot dimension prefix

Continued uncommitted Session-361 on `chore/reconstruction-build-ci`.

## Direct evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/218D8.c:229–236`: read a single scalar dimension for each slot while v19 < v12; any excess values beyond active-slot count are never checked. Previously compiled `DDHostPreparedSlotsReady` used `DDHostSwitchAllSlotSizesValid`, which required exactly the active count.

## Code change
- In compiled `HostFlowAdapter.m`, `DDHostPreparedSlotsReady` now validates that the measurement array has at least the active count and validates only the first active-count NSNumber values. Trailing elements are ignored. Existing prepared BID match and fail-closed type checks remain.
- Extended explicit Objective-C self-test with a two-slot valid prefix and an invalid third measurement, which should not block readiness.
- No private host state access, UI mutation, or automatic startup self-test.

## Checks
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. macOS executable self-test and arm64 Theos CI not run; no commit/push.
