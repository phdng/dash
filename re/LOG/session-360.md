# Session-360 — Prepared-host BID matching parity with decoded 218D8

Continued from uncommitted sessions 357–359.

## Evidence
- `Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/218D8.c:208–235`: private sub_3DD4C normalizes request BIDs before comparison; per-index logic uses empty string when normalized OR hosted BID array is too short. This differs from `208F4.c:207–237`, which refuses hosted BID count below hostedSlotCount.

## Compiled changes
- Added `DDHostPreparedBidsMatch` to `DuoDashShared.h` and `HostFlowAdapter.m`; it compares caller-normalized BIDs against hosted BIDs for active slot indices, padding absent positions on either side with empty strings, failing closed on malformed non-array types/values.
- Extended explicit Objective-C preflight selftest to exercise empty arrays, matching and mismatching BIDs and bad inputs.
- Kept `DDHostSwitchBidsMatch` unchanged for 208F4. No private normalization or UI operations added.

## Verification
PASS reconstruction verifier (30 modules), git diff --check. Objective-C executable and Theos arm64 CI not verified here. No commit/push.
