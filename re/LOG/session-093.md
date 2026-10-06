# LOG/session-093.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-092 commit 0dad59a; complete R-092 by promoting only data-only 4138C host/aux sceneHandle update routing and foreground-based original-callback suppression decisions. Per user workflow, commit locally but do not push._

## R-092 — 4138C host/aux sceneHandle update routing

Directly reviewed:
- `4138C.c`
- `3E4A8.c`
- `3FFC0.c`
- `3FBC8.c`
- `3F5C0.c`
- `3E670.c`

Raw ARM64 for `4138C` was cross-checked.

The callback has an outer hosting-active gate. Identity traversal through `3FBC8` remains outside reconstruction; callers supply the already-resolved bundle identifier.

### Host route

The first 4138C slot loop:
- requires identity length >0;
- compares against configured host slots 0..2;
- does NOT filter CarPlay-UI flags.

Therefore this route differs from the non-CarPlay-only host route used by 400D0/41E08.

For a matched host slot, the original requests `3F5C0` only when:
- a scene object exists;
- the corresponding `word_163E98[slot]` mark is clear;
- raw slot width is strictly >0.

Before the request it attempts to decrement the general counter `dword_162F1C`.

The target dimensions use the same accepted-landscape swap:
- landscape override active;
- swap flag enabled;
- height >0;
- width is already known >0.

Promoted:
- `DDAVCSceneHandleUpdateKind`;
- `DDAVCSceneHandleUpdateDecision`;
- `DDResolveAVCSceneHandleUpdateDecision(...)`.

Host decisions carry:
- matched slot index;
- landscape-adjusted target size;
- pending general-counter decrement.

No `3F5C0` invocation or counter mutation is performed.

### Aux fallback

Only when no configured slot matched does 4138C test exact aux identity equality.

If:
- scene exists;
- identity is aux;

the original calls `3E670(scene, settingsOrNil, "avc sceneHandle")`.

If the scene supports `settings`, the original reads it first.
If it does not, the aux executor is still called with nil settings.

The descriptor therefore reports:
- aux update pending independently of settings-selector support;
- whether the original would first read scene settings.

No settings selector or `3E670` invocation is performed.

## R-092 — foreground-based original callback suppression

After the update-routing half, 4138C separately decides whether to call its original callback.

Default behavior is to call original.

Suppression requires all of:
- hosting is active;
- scene exists;
- scene supports `settings`;
- settings object exists;
- settings supports `isForeground`;
- `isForeground` returns false;
- a second resolved identity check matches a configured NON-CarPlay host via 3E4A8 semantics.

This is deliberately narrower than the update host route:
- update route includes CarPlay-flagged configured slots;
- suppression route excludes them.

When suppression matches:
- original callback is not called;
- suppression remains true regardless of diagnostic count value;
- `qword_163EB8` increments only when its unsigned current value <=9;
- therefore 0..9 advance by one, and 10+ remain unchanged.

Promoted:
- `DDAVCSceneHandleCallbackDecision`;
- `DDResolveAVCSceneHandleCallbackDecision(...)`.

The descriptor exposes:
- call-original vs suppress-original;
- bounded count-increment eligibility;
- next count.

No original callback invocation/suppression or global count mutation is performed.

## Explicit exclusions

R-092 does not:
- reproduce `3FBC8` identity traversal;
- send `scene`, `settings`, or `isForeground`;
- invoke `3F5C0`;
- invoke `3E670`;
- decrement `dword_162F1C`;
- increment `qword_163EB8`;
- call or suppress the original callback itself.

## Scout for next batch

Reviewed `3F3F0.c`.

Useful next pure boundary after an accepted resize:
- `dword_163E88` is reset to 0 only when currently >=1;
- `dword_162F1C` is raised to a floor of 4 only when currently <=3;
- original probes the private scene for the slot;
- when a scene is returned, the resized dimensions receive the accepted-landscape swap and are passed to `3F5C0`.

## Next

R-093 after compiler green:
- promote data-only post-resize counter normalization;
- promote caller-supplied probeScene result to landscape-adjusted private-update request;
- do not invoke `probeSceneForSlot:`, `3F5C0`, or mutate private counters.
