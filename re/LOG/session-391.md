# Session-391 — Compose dock state decoding and clipped usable area

Continued uncommitted Session 390 on `chore/reconstruction-build-ci`.

## Original decompiled evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/83FC.c` decodes a packed 64-bit `com.sensetechlab.appbridge/dockrect` notify state into four one-tenth-point rectangle coordinates. `23D94.c` supplies that rectangle to `26654.c` for edge-strip clipping of a usable area.

## Changes
- Added `DDHostTrimUsableBoundsForDockState(CGRect usableBounds, uint64_t dockState, CGRect *outRect)` to public header and compiled HostFlowAdapter.m, composing existing 83FC decode and 26654 dock trim helpers without private state I/O.
- Added smoke regressions for correct packed left dock, zero state and invalid size; assert unchanged output on failure.
- Updated structural verifier export/definition contract.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python -m py_compile scripts/verify_reconstruction.py`, PASS `git diff --check`. macOS Objective-C compiled smoke, arm64 Theos CI and live CarPlay remain unverified. No commit/push.
