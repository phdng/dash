# Session-395 — 269FC early dock coverage classifications

Continued uncommitted Sessions 390–394 on `chore/reconstruction-build-ci`.

## Original evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/269FC.c`: returns early with `no-exit` when flag a2 is off, `no-strip-published` when `sub_83FC` cannot read valid dock state, `no-window` for empty usable/candidate bounds, and `already-inside` when dock rect is contained within `CGRectInset(candidate,-2,-2)`. Later covered/adjacent geometry depends on further calculations and remains separate.

## Changes
- Exported `DDHostDockCoverageEarlyReason` to DuoDashShared.h and implemented in compiled HostFlowAdapter.m. Accepts caller-supplied availability flags and bounds; returns early label or nil for later geometry.
- Added smoke regression assertions for precedence, zero-area geometry, contained dock and an outlying dock that needs later analysis.
- Added new helper to structural reconstruction verifier.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python -m py_compile scripts/verify_reconstruction.py`, PASS `git diff --check`. macOS compiled Objective-C smoke, iOS arm64 Theos CI and live CarPlay unconfirmed. No commit/push.
