# Session-365 — Compose 3DD4C normalization and 218D8 prepared-host checks

## Evidence
- `DuoDash.dylib_export_for_ai/decompile/218D8.c:204–236` receives BID normalization from `sub_3DD4C` and then checks normalized versus hosted slot BIDs and one scalar dimension per active slot.
- `decompile/3DD4C.c` normalizes requested IDs and optionally validates non-CarPlay-UI application existence when the private controller is available.

## Code
- Added exported compiled Objective-C `DDHostPreparedRequestReady`, chaining `DDHostNormalizeBidsWithAvailability` and `DDHostPreparedSlotsReady` with caller-supplied application state, hosted BIDs and measurements; malformed source arrays are refused.
- Added explicit tests for available/unavailable apps, CarPlay UI exemption, invalid size and bad request type.
- No runtime SBApplicationController lookup, private hosting call, or UI mutation.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. No macOS Objective-C executable or Theos arm64 CI execution. No commit/push.
