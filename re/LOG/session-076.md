# LOG/session-076.md
_Date: 2026-10-06. Objective: continue after session-075 GitHub Actions build GREEN; close the SpringBoard UIApp request/per-slot geometry gap without guessing slot sizes._

## R-069 — host-slot mirror + 3F224 responder
The previous blocker was exact per-slot render size for slots 1/2: DDz2 exposes `renderSize` only for slot 0, while `3F224` directly indexes `xmmword_163D90[slot]`.

Direct reads:
- `3F224.c` — onUIAppRequest:
  - read `bundleIdentifier` from notification userInfo;
  - require active host;
  - scan exactly 3 slots;
  - skip empty bids and slots marked CarPlay UI;
  - exact bid match selects that slot's width/height;
  - publish 89D8 only when matched width > 0.
- `41D80.c` / `41E08.c` — confirmed no clean bundle-id→size accessor; they still depend on raw slot globals and scene/object→bid extraction.
- `3CC44.c` / `3DD4C.c` — recovered the safe post-normalization slot-state contract:
  - effective count is min(bids,native sizes), valid only for 1..3;
  - with 3DD4C validation flag 0, non-NSString entries become empty strings;
  - duplicate non-empty bids become empty strings;
  - order is preserved;
  - three CarPlay flags default false when missing;
  - host generation increments when a new host-slot state is installed;
  - split state and per-slot size arrays are independent raw state.
- `3DFC8.c` — orientation override file `/var/tmp/duodash_ab_orient`; integer values 1..4 accepted, otherwise 1.

Promoted:
- `DDHostSlotSize`.
- `DDUpdateHostSlotMirror`: compile-safe mirror of the raw state consumed by 3F224/3B738/3D4FC.
- `DDResetHostSlotMirror`: clears active/count/split/bids/sizes/flags without advancing generation, matching reset-state stale-retry behavior.
- `DDCurrentHostSlotMirror` for tests/debugging.
- `DDReadHostOrientation` exact 3DFC8 semantics.
- `DDReconstructionHostUIAppResponder` + SpringBoard subscription to `com.sensetechlab.appbridge.uiapp.request`.
- `DDConsumeHostUIAppRequestUserInfo` mirrors 3F224 over the reconstruction slot state.

The mirror is intentionally a boundary after size/orientation decisions. It does not instantiate SpringBoard private scene/view classes.

## R-070 — exact handshake + geometry retry schedulers
Direct reads:
- `3B738.c` and block `3ED88.c`.
- `3D4FC.c` and block `3DC38.c`.
- `__objc_arraydata` / constant-double objects backing `off_154160`.

Recovered retry array exactly:
- 0.0 s
- 0.4 s
- 0.9 s
- 1.8 s
- 3.5 s

`3B738/3ED88` semantics:
- capture slot-0 bid, slot-0 size, orientation, generation;
- schedule all five retries on main queue;
- each callback requires same generation and active host;
- current slot-0 bid must still equal captured bid;
- publish uiapp.state with shouldBridge=YES, isSplit=NO, captured size/orientation.

`3D4FC/3DC38` semantics:
- only schedule slots 0..2 with non-empty bid and CarPlay flag OFF;
- capture bid, size, orientation, generation;
- callback requires same generation and active host;
- re-find captured bid among current non-CarPlay slots;
- use current matching slot size when both dimensions >= 1; otherwise fall back to captured size;
- publish uiapp.state with shouldBridge=YES and isSplit=YES.

Promoted:
- `DDScheduleAppSideHandshake`.
- `DDScheduleGeometryPushesForSlot`.
- exact retry delay table and generation/active/bid gates.

## R-071 — CarPlay slot state
Direct reads:
- `3D6EC.c`: slot 0..2 direct CarPlay flag setter.
- `3D704.c`: convert slot to CarPlay UI.

Promoted:
- `DDSetHostSlotCarPlayUI` exact raw flag semantics for physical slots 0..2.
- `DDConvertHostSlotToCarPlayUI` evidence-safe state/IPC half:
  - valid only on main thread, slot < 3 and slot < slotCount;
  - return value is the validity gate even when slot already CarPlay UI;
  - when converting a non-CarPlay slot, copy/retain bid;
  - if bid non-empty, publish uiapp.state with shouldBridge=NO, isSplit=YES, width=height=0 and current host orientation;
  - leave bid in slot and set its CarPlay flag true.

Explicit omission:
- original 3D704 removes the hosted view and invalidates its private scene/view controller. The reconstruction mirror owns no such object, so that private view teardown remains outside the buildable runtime.

## Integration
- Existing fontfloor/keypane per-host broadcasts now fall back to the reconstruction host-slot mirror when runtime-resolved DDz2 is absent. This makes the standalone reconstruction state model useful without requiring the original DDz2 class.
- No hard private framework linkage was added.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier = NOT_CONFIGURED, expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest.

Session-075 GitHub Actions build was GREEN per user. Session-076 Objective-C host-mirror/responder/block changes require the next pushed macOS CI compiler run.

## Next
R-072 after CI green:
- inspect evidence-safe pre-private portions of `3B2D8` and `3CC44`;
- recover pure render-size scaling/orientation/mirror-population boundaries where exact;
- do not instantiate or hard-link `SBApplicationController`, `SBDeviceApplicationSceneEntity`, `SBAppViewController`, or private hosted-view teardown;
- keep 73E8/80D0 and full 7E908 unresolved until missing contracts are recovered.
