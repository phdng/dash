# Session-351 — Per-slot hosted size validation

Workspace clean at session start. Continued evidence-backed 208F4:207-237 guard implementation in compiled Objective-C.

## Implementation
- `DuoDashShared.h`: export `DDHostSwitchAllSlotSizesValid(NSArray<NSNumber *> * _Nullable sizes, NSInteger expectedSlotCount)`.
- `HostFlowAdapter.m`: reject slot count outside 1..3, nil/wrong array/cardinality, non-NSNumber values, and any hosted size below 1.0; scan all slots so a valid first pane does not hide invalid subsequent panes.
- Extended explicit `DDHostSwitchPreflightSelfTest` to cover two valid sizes, too-small second slot, missing entry, nil and count mismatch.
- The legacy single-size preflight remains unchanged for ABI compatibility. Private slot measurement and UI mutation still excluded.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. Objective-C self-test and Theos arm64 CI have not run in current session. No commit/push.
