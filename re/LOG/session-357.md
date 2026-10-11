# Session-357 — Direct decoded export_for_ai comparison

Three decoded source roots located:
- `Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai`
- `Applications/DuoDash.app/DuoDash_export_for_ai`
- `Applications/DuoDashKey.app/DuoDashKey_export_for_ai`

## Evidence compared
- `decompile/208F4.c` lines 207–237: hostedSlotBids count >= hosted slot count; requested BID missing at an index is empty; compare per index; both dimensions (`*(v14-1)` and `*v14`) must each be >=1.
- `decompile/217EC.c`: two ordered BIDs, nil -> empty; invokes private hostSlots:skipEvict:onHosted: (not implemented here).
- `decompile/218D8.c` lines ~203–238: 3DD4C normalization is performed upstream in a different branch; does not license inventing private normalization in switch preflight.

## Compiled changes
- `DDHostSwitchBidsMatch`: reject insufficient hosted BIDs but allow extra hosted entries; fill missing requested indexes with empty string; ignore extra requested entries beyond active count; retain type checking and ordered comparison.
- Added Objective-C regression assertions for short requested arrays, extra hosted arrays, missing hosted slots and mismatch with nonempty hosted BID.
- Updated API comment in `DuoDashShared.h`.

## Remaining behavior gap
- `208F4` validates TWO dimensions per slot; current `DDHostSwitchPreflightForSlots` takes one number per slot. A precise dimensions contract should be established before replacing existing callers.
- Real UI hosting and private state acquisition not implemented. The other two export roots were located but not exhaustively audited in this session.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 synthesis modules), `git diff --check`. No macOS Objective-C execution, arm64 CI or jailbroken device validation. No commit/push.
