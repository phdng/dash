# LOG/session-128.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-127 commit `f63a84d`; decode and promote exact data-only `3BBF0` spikeCreateSlot exception behavior from Mach-O LSDA/raw ARM64, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD at session start: `f63a84d`.
- Working tree: clean.
- Branch synchronized with origin.
- User confirmed the session-127 macOS CI/compiler build was green.

## Target

Next earlier LSDA-bearing function:
- `3BBF0 -> LSDA 0x114538`.
- Identity: `-[DDz2 spikeCreateSlot:index:native:]`.

Reviewed:
- `decompile/3BBF0.c`;
- raw ARM64 `0x3BBF0..0x3C1F0`;
- Mach-O LSDA bytes at `0x114538`;
- prior `3C1F0` degradeSlot exception contract from R-126.

The first arm64 FAT slice begins at file offset `0x4000`.

## Exact LSDA call-site table

The earlier scout note said “14 action-5 ranges”; direct recount in this session corrects that to **12**.

Decoded 19 entries:

1. `0x3BBF0..0x3BD48` -> no landing.
2. `0x3BD48..0x3BD58` -> `0x3C150`, action 5.
3. `0x3BD64..0x3BD74` -> `0x3C154`, action 5.
4. `0x3BDD8..0x3BDE8` -> `0x3C158`, action 5.
5. `0x3BDF8..0x3BE14` -> `0x3C14C`, action 5.
6. `0x3BE14..0x3BE20` -> no landing.
7. `0x3BE20..0x3BE34` -> `0x3C15C`, action 5.
8. `0x3BE34..0x3BE6C` -> no landing.
9. `0x3BE6C..0x3BEB4` -> `0x3C15C`, action 5.
10. `0x3BEC0..0x3BF00` -> `0x3C148`, action 5.
11. `0x3BF00..0x3BF48` -> `0x3C12C`, action 5.
12. `0x3BF48..0x3C018` -> no landing.
13. `0x3C018..0x3C030` -> `0x3C154`, action 5.
14. `0x3C038..0x3C060` -> `0x3C158`, action 5.
15. `0x3C068..0x3C090` -> `0x3C15C`, action 5.
16. `0x3C098..0x3C0C0` -> `0x3C148`, action 5.
17. `0x3C0C0..0x3C184` -> no landing.
18. `0x3C184..0x3C1C4` -> `0x3C1E0`, action 0.
19. `0x3C1C4..0x3C1F0` -> no landing.

There are:
- 12 action-5 ranges;
- 1 action-0 range;
- 6 no-landing ranges.

## State committed before every action-5 range

Raw ARM64 before the first protected range:
- `0x3BC38`: `byte_163D88 = 1` (spike-in-progress state);
- `0x3BC50..0x3BC6C`: copy incoming bid into `qword_163D30[slot]`, release old bid;
- `0x3BC70..0x3BC7C`: commit native width/height into the slot native-size array.

Therefore every local action-5 exception occurs after:
- spike-in-progress flag was set;
- hosted bid was committed;
- native size was committed.

Those are historical timing facts only; the data-only resolver does not mutate them.

## Per-range mapping

### Before controller ivar store — common degrade catch

`0x3BD48..0x3BD58`
- `SBApplicationController sharedInstance` + retain-autoreleased.

`0x3BD64..0x3BD74`
- `applicationWithBundleIdentifier:` + retain-autoreleased.

`0x3BDD8..0x3BDE8`
- allocate/init `SBDeviceApplicationSceneEntity`.

`0x3BDF8..0x3BE14`
- UUID + UUIDString acquisition.

`0x3BE20..0x3BE34`
- allocate/init `SBAppViewController`.

All five route to the common typed catch and occur before the controller is stored in the slot ivar.

### Controller ivar commit

After successful controller construction:
- `0x3BE58..0x3BE60` stores the controller strongly into the selected slot ivar.

### After controller ivar store — common degrade catch

`0x3BE6C..0x3BEB4`
- capability/send for `setIgnoresOcclusions:`;
- capability/send for `setAutomatesLifecycle:`.

`0x3BEC0..0x3BF00`
- controller `view` send + retain-autoreleased;
- optional `setRequestedMode:2`.

Both ranges occur after the controller ivar was stored and route to common degrade.

### Special private-device decoration catch

`0x3BF00..0x3BF48`
- resolve `_deviceAppViewController` through `9C4AC`;
- retain-autoreleased private device controller;
- capability probe for `setHomeGrabberDisplayMode:`;
- optional `setHomeGrabberDisplayMode:1`.

This range lands at `0x3C12C`, not the common catch.

Expected discriminator:
- begin/end catch only;
- branch to `0x3BF50`.

At `0x3BF50`:
- retain the already-obtained main view in `x28`;
- branch to normal cleanup at `0x3C0C0`;
- return that main view.

Therefore an expected private device/home-grabber decoration exception:
- is swallowed;
- skips any remaining private decoration;
- does **not** degrade the slot;
- continues returning the main controller view.

The controller ivar had already been stored before this protected call.

Nonmatching discriminator leaves the special catch path and resumes unwind via the shared unwind tail.

### Application-miss placeholder creation — common degrade catch

`0x3C018..0x3C030`
- on application lookup miss, hosted bid was already reset to the empty string immediately beforehand;
- call `36E98(slot,width,height)` and retain-autoreleased placeholder.

If this protected placeholder path throws the expected type, control goes to the common catch, which routes through `degradeSlot`.

The resolver models the catch route, not the exact current hosted-bid value at catch, because the site category is about continuation behavior.

### Normal failure-degrade calls — common catch retries degrade

Three ranges are normal failure branches that already invoke `degradeSlot:bid:native:why:`:

- `0x3C038..0x3C060`: scene entity could not be made.
- `0x3C068..0x3C090`: SBAppViewController could not be made.
- `0x3C098..0x3C0C0`: controller view is nil.

If any expected exception occurs anywhere in one of these ranges, the common catch invokes `degradeSlot` again with an exception-derived reason.

Therefore these sites have exact one catch-level degrade retry.

Historical controller-store timing differs:
- first two failure-degrade calls occur before controller ivar store;
- view-nil failure-degrade occurs after controller ivar store.

The first degrade attempt can itself mutate state before throwing, so the runtime metadata records only that the controller had been stored **before the protected call**, not that it is necessarily still stored at catch entry.

## Common typed catch 0x3C15C

Landing stubs:
- `0x3C148`;
- `0x3C14C`;
- `0x3C150`;
- `0x3C154`;
- `0x3C158`;

all converge at `0x3C15C`.

Expected type:
- save exception;
- begin catch;
- retain caught object;
- format an exception-derived reason string;
- invoke `degradeSlot:bid:native:why:` with original self/slot/bid/native size plus the formatted reason;
- retain degraded result;
- release temporary reason/caught exception;
- end catch;
- branch to `0x3C0F8` final cleanup;
- return degraded result.

Nonmatching type:
- resume unwind at `0x3C1E8`.

Thus eleven action-5 ranges have a common “expected exception -> degrade and return degraded result” continuation.

## Nested exception inside common catch

The catch-internal reason formatting and degrade invocation are covered by:
- `0x3C184..0x3C1C4` -> landing `0x3C1E0`, action 0.

If this nested work throws:
- landing preserves nested exception;
- calls `objc_end_catch`;
- falls through to resume unwind at `0x3C1E8`.

No second typed swallow is attempted.

For the three normal failure-degrade sites this proves the catch-induced retry is bounded to one retry: if the retry throws, it propagates.

## Promoted runtime contract

Added:
- `DDSpikeCreateSlotExceptionSite`:
  - `PreControllerPrivateWork`;
  - `PostControllerPrivateWork`;
  - `PrivateDeviceDecoration`;
  - `PlaceholderCreationAfterApplicationMiss`;
  - `FailureDegradeBeforeControllerStore`;
  - `FailureDegradeAfterControllerStore`;
  - `CatchDegrade`;
  - `UnprotectedRange`.
- `DDSpikeCreateSlotExceptionOutcome`.
- `DDResolveSpikeCreateSlotExceptionOutcome(site)`.

Common-degrade sites:
- swallow expected exception;
- record pre-existing spike-in-progress + hosted-bid/native commits;
- route through degrade from catch;
- return degraded result if catch degrade succeeds;
- nonmatching type resumes unwind.

Post-controller private work and failure-degrade-after-controller-store additionally record:
- controller ivar had been stored before the protected call.

Failure-degrade sites additionally record:
- retry degrade from catch.

Private-device-decoration site:
- swallow;
- record state commits + prior controller store;
- skip remaining private decoration;
- continue returning main view;
- do not route through degrade.

Catch-degrade/action-0 site:
- end active catch before resume unwind;
- propagate nested exception.

Unprotected range:
- propagate.

## Explicit exclusions

R-127 does not:
- query `SBApplicationController`;
- allocate/init scene entities or app view controllers;
- invoke private controller `view` or lifecycle setters;
- resolve `_deviceAppViewController`;
- mutate home-grabber mode;
- call `degradeSlot`;
- mutate live spike/hosted bid/native/controller state;
- format real caught exceptions;
- synthesize/catch exceptions;
- execute begin/end-catch or unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final verifier, CatDesk standard verification status, and `git diff --check` are run immediately before commit.

## Scout for next batch — 3B8F8

Next earlier LSDA-bearing function:
- `3B8F8 -> LSDA 0x1144C4`.
- Identity: `-[DDz2 cnabBuildSceneHostForBid:displaySize:]`.

Direct LSDA scout decoded 18 entries:
- 11 action-5 ranges;
- 1 action-0 range `0x3BBC4..0x3BBCC`;
- remaining no-landing gaps.

Action-5 ranges:
- `0x3B96C..0x3B97C`;
- `0x3B988..0x3B998`;
- `0x3B9A0..0x3B9B0`;
- `0x3B9C0..0x3B9DC`;
- `0x3B9E8..0x3B9FC`;
- `0x3BA18..0x3BA60`;
- `0x3BA68..0x3BAA4`;
- `0x3BAA4..0x3BAEC`;
- `0x3BAF8..0x3BB00`;
- `0x3BB08..0x3BB10`;
- `0x3BB18..0x3BB20`.

Raw tail shows:
- special typed catch `0x3BB74` begin/end-catches then rejoins `0x3BB24`;
- other landing stubs converge at common typed catch `0x3BBA4`;
- expected common catch retains exception, invokes `resetHostingState`, releases exception, ends catch, forces return object nil, then rejoins normal cleanup;
- nonmatching type resumes unwind at `0x3BBE8`;
- catch-internal `resetHostingState` is action 0 at `0x3BBC4..0x3BBCC`; landing `0x3BBE0` ends the active catch then resumes unwind.

R-128 should map the exact 11 protected ranges against controller-store/view/device-decoration timing, and identify the semantics of the special rejoin `0x3BB24` before promotion.

## Next

After the user pushes session-128 and confirms compiler green:
- R-128: decode/promote exact `3B8F8 -> LSDA 0x1144C4` exception outcomes;
- distinguish special continue-with-view behavior from common resetHostingState->nil behavior;
- keep private SpringBoard scene/controller/view construction and live reset execution excluded.

Known unresolved:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device runtime smoke testing.
