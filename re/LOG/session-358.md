# Session-358 — Two-dimensional switch slot validation from decoded 208F4

Continued with uncommitted Session-357 on `chore/reconstruction-build-ci`.

## Direct source evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/208F4.c:207-238`: source compares each index BID then checks `*(v14 - 1) < 1.0 || *v14 < 1.0` and advances `v14 += 2`. Thus TWO dimensions of EACH active hosted slot must pass the threshold.

## Compiled Objective-C changes
- `DuoDashShared.h`: declare `DDHostSwitchSlotDimensionsValid` and `DDHostSwitchPreflightForDimensions`.
- `HostFlowAdapter.m`: validate ordered pairs of width and height for each slot using caller-supplied `NSArray<NSArray<NSNumber *> *>`; malformed, missing and undersized dimensions fail closed. New staged preflight composes early state flags, normalized ordered BID comparison, full dimensional validation and shell-bounds result. Existing scalar and one-value-per-slot APIs preserved.
- Extended explicit Objective-C self-test with valid pairs, too-small width and height, missing pair, malformed pair, preflight accept/reject.
- No private selectors or live hosting calls.

## Verification
PASS reconstruction verifier (30 modules) and git diff --check. macOS runtime self-test/arm64 Theos CI not confirmed. No commit/push.
