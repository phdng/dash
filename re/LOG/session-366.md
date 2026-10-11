# Session-366 — Count-driven 3DD4C BID normalization parity

Continued uncommitted Sessions 361–365 on `chore/reconstruction-build-ci`.

## Direct source evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/3DD4C.c` allocates `arrayWithCapacity:` using non-negative a2 and iterates all a2 slots when a2 >= 1. Its 3DD4C normalization loop does NOT share the `208F4.c:188` 1..3 in-place switch gate.

## Compiled changes
- `DDHostNormalizeBidsWithoutLookup` and `DDHostNormalizeBidsWithAvailability` now accept any non-negative slot count rather than applying the unrelated `208F4` max of 3. Negative counts are refused.
- Added compiled self-test cases exercising four ordered distinct BIDs through both lookup-free and availability-fed normalizers.
- Did not relax DDHostSwitchSlotCountIsValid or switch preflight limits; private app controller and hosting calls remain excluded.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `git diff --check`. macOS Objective-C runtime and arm64 Theos CI not executed here. No commit/push.
