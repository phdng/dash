# Session-359 — Nil requested-array parity with decoded 208F4

Continued uncommitted Sessions 357–358 on `chore/reconstruction-build-ci`.

Evidence: `Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/208F4.c:214–226` initializes the requested BID to the empty string and only subscripts when `v13 < [v5 count]`. Sending count to nil returns zero; thus a nil requested array compares empty BIDs at all hosted slots.

Changes:
- `DDHostSwitchBidsMatch` permits a nil requested array, using the existing per-index empty fallback, but rejects non-array non-nil requested inputs.
- Expanded the compiled Objective-C self-test to assert nil requested vs empty hosted BIDs succeeds, nil vs nonempty hosted fails, wrong-type requested input fails.
- Updated shared-header comment. Private normalization, geometry acquisition and UI execution remain excluded.

Checks: PASS `python scripts/verify_reconstruction.py` (30 modules), `git diff --check`. Objective-C smoke execution and arm64 Theos CI not confirmed. No commit/push.
