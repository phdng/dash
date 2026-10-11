# Session-364 — 3DD4C conditional application-availability normalization

Continued Sessions 361–363 uncommitted.

## Decompiled evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/3DD4C.c`: a3=1 obtains SBApplicationController if available and responds to `applicationWithBundleIdentifier:`; for each deduplicated nonempty BID, if matching CarPlay UI flag is false and controller is present, nonexistent app becomes empty. If controller absent or flag true, lookup is skipped.

## Compiled Objective-C change
- Added `DDHostNormalizeBidsWithAvailability` to `DuoDashShared.h` and `HostFlowAdapter.m`. The app-availability set supplied by caller models already-resolved private application existence: nil set => no available private controller; otherwise only known BIDs survive when the slot flag is false. Existing ordered first-occurrence deduplication, padding and type validation remain.
- Added explicit self-test cases for CarPlay UI bypass, unknown app rejection, nil availability/controller behavior.
- Does not directly invoke private selector or modify CarPlay UI.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `git diff --check`. macOS Objective-C and Theos arm64 CI not run. No commit/push.
