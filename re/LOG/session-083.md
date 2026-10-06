# LOG/session-083.md
_Date: 2026-10-06. Objective: continue from committed session-082 and implement R-082 using caller-supplied identity/settings snapshots only, with raw ARM64 used to resolve the bad 41E94 decompiler prototype._

## R-082 — identity size/orientation/settings decisions

Directly reviewed:
- `41D80.c`
- `41E94.c`
- `40514.c`
- `3FAF8.c`
- `41F50.c`
- `42124.c`
- `9C3BC.c`

Cross-checked callers:
- `400D0.c`
- `40C5C.c`
- `40DA8.c`

Also inspected next callback candidates:
- `40F0C.c`
- `40FF4.c`
- `41730.c`
- `41BA0.c`

## Raw ARM64 correction for 41D80 / 41E94

The exported decompile incorrectly types `41E94` as `void`, while callers consume two floating-point return registers.

Disassembling the original arm64 slice of `DuoDash.dylib` confirms:

### 41D80

At `0x41DF0/0x41DF4`, the function explicitly returns:
- `d0 = width`
- `d1 = height`

Selection order is:
1. `41E08` matching configured non-CarPlay host slot -> slot size from `xmmword_163D90[index]`;
2. otherwise, if `3FB54` says aux -> aux native size at `xmmword_163DD0`;
3. otherwise -> `CGSizeZero`.

Promoted:
- `DDResolveIdentityNativeSize(bundleIdentifier)`.

Identity must already be supplied by the caller; no `3FBC8` traversal is reconstructed.

### 41E94 aux branch

Raw instructions at `0x41ECC..0x41EF8` show:
- branch is selected when identity is aux;
- test aux orientation with `orientation - 3 < 2`, exactly orientations 3/4;
- compare width > height;
- swap only when both are true.

Therefore aux adjusted size portrait-normalizes landscape-shaped native dimensions only for aux orientation 3/4.

### 41E94 non-aux branch

Raw instructions at `0x41EFC..0x41F3C` show:
- no transform when landscape override state is zero;
- otherwise swap only when the recovered swap flag is enabled and both dimensions are positive.

This is the same transform already represented by `DDApplyLandscapeSwapToSize`.

Promoted:
- `DDResolveIdentityAdjustedSize(bundleIdentifier)`.

## 3FAF8 raw settings orientation

Once identity is known:
- if aux orientation is nonzero and identity is aux -> aux orientation;
- otherwise -> host orientation.

Promoted:
- `DDResolveIdentityRawSettingsOrientation(bundleIdentifier)`.

This intentionally differs from `DDResolvePaneSettingsOrientation`, which also applies the 3F75C nopane/landscape/direct-ivar suppression path.

## 40514 non-aux direct orientation repair decision

In the non-aux branch, 40514 may call private `9C3BC` to write `_interfaceOrientation` when:
- force-IO is enabled; or
- landscape override is active; or
- desired raw orientation differs from host orientation.

The private ivar writer remains excluded.

Promoted as data-only:
- `DDShouldAttemptDirectInterfaceOrientationRepair(bundleIdentifier, forceInterfaceOrientation)`.

The caller supplies the already-resolved force-IO toggle result.

## 40514 aux snapshot comparison

Before and after the private 41F50 mutation, 40514 compares effective settings snapshots.

Exact equivalence rule:
- orientation equal;
- foreground equal;
- absolute frame-width delta <= 0.5;
- absolute frame-height delta <= 0.5.

Missing private selectors are represented by caller-supplied zero/default snapshot values.

Promoted:
- `DDSceneSettingsSnapshot`;
- `DDSceneSettingsSnapshotsEquivalent(before, after)`.

## 40514 settingsDiff clear decision

Original aux path clears `settingsDiff` only when:
- a diff is treated as present;
- before/after snapshots changed;
- `duodash_kp_noapplydiff` is not active;
- the private setter is supported.

Promoted:
- `DDShouldClearAuxSceneSettingsDiff(settingsDiffPresent, settingsDiffSetterSupported, before, after)`.

This function returns only the decision. The reconstruction never sends `setSettingsDiff:` and does not construct `FBSSceneSettingsDiff`.

## Explicit exclusions

R-082 does not:
- traverse private scene/client identity objects;
- call `9C3BC` or write private ivars;
- call `41F50`;
- construct `FBSSceneSettingsDiff`;
- send `setSettingsDiff:`;
- invoke any private settings/layout executor.

## Next

R-083 after compiler green:
- inspect pure callback argument rewrites in `40C5C/40DA8/40F0C`;
- promote exact dimension substitution and orientation-equality decisions when contracts are complete;
- keep `40FF4` private `setForeground:` mutation excluded unless represented only as a caller-driven decision descriptor.
