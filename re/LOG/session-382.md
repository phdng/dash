# Session-382 — Original 218D8 prepared CarPlay UI flag parity

Continued uncommitted Sessions 379–381 on `chore/reconstruction-build-ci`.

## Decompiled source evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/218D8.c:264–295`: when prepared-host BIDs/geometry pass earlier gates, original code obtains `sub_22E40(hostedSlotBids, slotCount)` and compares each prepared flag's `boolValue` with corresponding `hostedSlotIsCarPlayUI` flag; absent entries become 0, and only the active slot count is visited. Any mismatch forces the full-host path rather than prepared reshow.

## Compiled implementation and tests
- Added exported pure-data `DDHostPreparedCarPlayFlagsMatch(preparedFlags, hostedFlags, expectedSlotCount)` to header and HostFlowAdapter.m. Requires 1–3 active slots; compares boolValue per slot, with absent slots false; ignores entries beyond active slot count; refuses malformed arrays.
- Extended `scripts/hostflow_preflight_smoke.m` with positive/negative regression assertions.
- Extended structural verifier to require the new header/implementation pair.
- Does not call private sub_22E40, mutate UI or hook host operations.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `git diff --check`. macOS compiled Objective-C tests, Theos arm64 and device CarPlay hosting unverified. No commit/push.
