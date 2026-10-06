# LOG/session-094.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-093 commit f553b45; complete R-093 by promoting only data-only 3F3F0 post-resize counter normalization and caller-supplied probeScene-result to landscape-adjusted private-update request. Per user workflow, commit locally but do not push._

## R-093 — 3F3F0 post-accepted-resize follow-up

Directly reviewed:
- `3F3F0.c`
- `3F5C0.c`

Raw ARM64 for `3F3F0` was used to confirm signed counter comparisons and the private-scene follow-up ordering.

This batch intentionally starts after the resize has already passed the existing reconstruction's acceptance gates:
- slot index unsigned <=2;
- main thread;
- hosting active;
- slot count > index;
- hosted bundle non-empty;
- non-CarPlay slot;
- width >=1;
- height >=1;
- raw size already stored;
- `uiapp.state` already published.

The previously reconstructed state/IPC half remains unchanged.

## Exact counter normalization

After the accepted resize, the original performs:

1. Attempt count `dword_163E88`
- signed compare against 1;
- if current value >=1, write 0;
- if current value <1, leave unchanged.

2. General counter `dword_162F1C`
- signed compare against 3;
- if current value <=3, write 4;
- if current value >3, leave unchanged.

This means negative general-counter values are also raised to 4.

Promoted:
- `DDHostSlotResizePrivateFollowup`;
- `DDResolveHostSlotResizePrivateFollowup(...)`.

The descriptor carries:
- reset-attempt eligibility;
- next attempt count;
- general-counter floor eligibility;
- next general counter.

No global counter is mutated.

## Private scene probe and update request

After counter normalization, the original always:
- obtains `[DDz2 shared]`;
- calls `probeSceneForSlot:slotIndex`;
- releases the shared/controller object.

The reconstruction does not perform those private calls. Instead the caller supplies whether a private scene was returned.

If no scene is returned:
- no private-update request is produced.

If a scene is returned:
- the accepted raw resize dimensions are transformed by the same landscape-swap rule used elsewhere:
  - accepted landscape override active;
  - swap bit enabled;
  - positive width and height;
- because the resize was already accepted with dimensions >=1, this becomes the expected width/height swap whenever the accepted landscape/swap state is active;
- the transformed size becomes the pending `3F5C0(scene, slot, width, height)` request.

The descriptor therefore reports:
- `shouldProbePrivateScene = YES`;
- `shouldRequestPrivateSceneUpdate` from caller-supplied scene presence;
- slot index;
- landscape-adjusted target size when a scene exists.

No `DDz2 shared`, `probeSceneForSlot:`, or `3F5C0` invocation occurs in the reconstruction helper.

## Raw ARM64 details

ARM64 confirms:
- attempt reset: `cmp w9,#1; b.lt ...; str wzr`;
- general floor: `cmp w9,#3; b.gt ...; mov w9,#4; str`;
- private scene probe occurs after both normalizations;
- nil scene skips the private-update block;
- landscape update uses the same positive-dimension + swap-bit decision before `3F5C0`.

## Explicit exclusions

R-093 does not:
- repeat the outer 3F3F0 resize acceptance/state/IPC logic already reconstructed;
- mutate `dword_163E88`;
- mutate `dword_162F1C`;
- invoke `+[DDz2 shared]`;
- invoke `probeSceneForSlot:`;
- invoke `3F5C0`;
- mutate private scene/settings state.

## Scout for next batch

Reviewed:
- `40DA8.c`
- `40C5C.c`

The two callbacks share the existing size-rewrite behavior, but only `40DA8` has an additional success-side counter effect:
- after routing and positive original dimensions;
- after native-size resolution and accepted-landscape swap;
- only when the replacement width and height are both >0;
- `40DA8` attempts to decrement `dword_162F40` when it is >=1;
- then substitutes the callback dimensions.
`40C5C` performs the same successful substitution without this counter decrement.

## Next

R-094 after compiler green:
- attach the exact 40DA8 substitution-success counter outcome to the existing size-rewrite descriptor;
- do not invoke the original callback;
- do not reproduce private identity traversal;
- do not mutate `dword_162F40`.
