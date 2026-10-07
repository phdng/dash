# LOG/session-129.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-128 commit `3e36eaa`; decode and promote exact data-only `3B8F8` cnabBuildSceneHost exception behavior from Mach-O LSDA/raw ARM64, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD at session start: `3e36eaa`.
- Working tree: clean.
- Branch synchronized with origin.
- User confirmed the session-128 macOS CI/compiler build was green.

## Target

Next earlier LSDA-bearing function:
- `3B8F8 -> LSDA 0x1144C4`.
- Identity: `-[DDz2 cnabBuildSceneHostForBid:displaySize:]`.

Reviewed:
- `decompile/3B8F8.c`;
- raw ARM64 `0x3B8F8..0x3BBF0`;
- Mach-O LSDA bytes at `0x1144C4`;
- existing `DDResetHostSlotMirror` evidence for `3AAF8 resetHostingState`;
- prior `3BBF0` and `3C1F0` exception-outcome conventions.

The first arm64 FAT slice begins at file offset `0x4000`.

## Exact LSDA call-site table

Decoded 18 entries:

1. `0x3B8F8..0x3B96C` -> no landing.
2. `0x3B96C..0x3B97C` -> landing `0x3BB98`, action 5.
3. `0x3B988..0x3B998` -> landing `0x3BB9C`, action 5.
4. `0x3B9A0..0x3B9B0` -> landing `0x3BBA0`, action 5.
5. `0x3B9C0..0x3B9DC` -> landing `0x3BB94`, action 5.
6. `0x3B9DC..0x3B9E8` -> no landing.
7. `0x3B9E8..0x3B9FC` -> landing `0x3BBA4`, action 5.
8. `0x3B9FC..0x3BA18` -> no landing.
9. `0x3BA18..0x3BA60` -> landing `0x3BBA4`, action 5.
10. `0x3BA68..0x3BAA4` -> landing `0x3BB90`, action 5.
11. `0x3BAA4..0x3BAEC` -> landing `0x3BB74`, action 5.
12. `0x3BAEC..0x3BAF8` -> no landing.
13. `0x3BAF8..0x3BB00` -> landing `0x3BB9C`, action 5.
14. `0x3BB08..0x3BB10` -> landing `0x3BBA0`, action 5.
15. `0x3BB18..0x3BB20` -> landing `0x3BBA4`, action 5.
16. `0x3BB20..0x3BBC4` -> no landing.
17. `0x3BBC4..0x3BBCC` -> landing `0x3BBE0`, action 0.
18. `0x3BBCC..0x3BBF0` -> no landing.

There are:
- 11 action-5 ranges;
- 1 action-0 range;
- 6 no-landing ranges.

## Per-range mapping

### Pre-controller private work -> common reset/nil catch

`0x3B96C..0x3B97C`
- `SBApplicationController sharedInstance`;
- retain-autoreleased result.

`0x3B988..0x3B998`
- `applicationWithBundleIdentifier:`;
- retain-autoreleased result.

`0x3B9A0..0x3B9B0`
- allocate/init `SBDeviceApplicationSceneEntity`.

`0x3B9C0..0x3B9DC`
- UUID acquisition + UUIDString acquisition.

`0x3B9E8..0x3B9FC`
- allocate/init `SBAppViewController`.

These five ranges occur before `_appVC` is stored.

### Controller ivar commit

After successful controller construction:
- `0x3BA04`: address `self + 8` (the `_appVC` strong ivar);
- `0x3BA08`: controller argument;
- `0x3BA0C`: `objc_storeStrong`.

### Post-controller private work -> common reset/nil catch

`0x3BA18..0x3BA60`
- capability/send for `setIgnoresOcclusions:`;
- capability/send for `setAutomatesLifecycle:`.

`0x3BA68..0x3BAA4`
- controller `view` send + retain-autoreleased main view;
- capability/send for `setRequestedMode:2`.

Both occur after `_appVC` store and route to the common typed catch.

### Special private-device decoration catch

`0x3BAA4..0x3BAEC`
- resolve `_deviceAppViewController` via `9C4AC`;
- retain-autoreleased private device controller;
- capability probe for `setHomeGrabberDisplayMode:`;
- optional `setHomeGrabberDisplayMode:1`.

This range occurs:
- after `_appVC` store;
- after main view was acquired into `x26`.

It lands at special catch `0x3BB74`.

Expected discriminator:
- begin catch;
- end catch;
- branch to `0x3BB24`.

At `0x3BB24` normal cleanup releases the controller/UUID/entity/application intermediates and finally returns `x26`, the already-acquired main view.

Therefore an expected exception from private device/home-grabber decoration:
- is swallowed;
- skips the rest of device decoration;
- preserves and returns the main view;
- does not call `resetHostingState`.

Because the normal device-controller release is at `0x3BAEC`, outside the protected range, a throw after the private device controller has already been retained can bypass that release when the catch jumps directly to `0x3BB24`.

## Normal failure reset calls -> common catch retries reset

Three action-5 ranges are themselves normal calls to `resetHostingState`:

- `0x3BAF8..0x3BB00`: application lookup returned nil.
- `0x3BB08..0x3BB10`: scene entity creation failed.
- `0x3BB18..0x3BB20`: app view controller creation failed.

All occur before the controller ivar store.

If one of these reset calls throws the expected type, its landing stub converges at the common catch, which invokes `resetHostingState` again.

Therefore the original has one catch-level reset retry for these failure-reset sites.

## Common typed catch 0x3BBA4

Landing stubs:
- `0x3BB90`;
- `0x3BB94`;
- `0x3BB98`;
- `0x3BB9C`;
- `0x3BBA0`;

all branch to `0x3BBA4`.

Expected type:
- preserve exception;
- begin catch;
- retain caught object;
- invoke `[self resetHostingState]` at `0x3BBC4`;
- release caught object;
- end catch;
- set return object register `x26 = 0`;
- branch to final cleanup at `0x3BB4C`;
- return nil.

Nonmatching type:
- resume unwind at `0x3BBE8`.

Thus ten of the eleven action-5 ranges have an exact “expected exception -> reset hosting state -> nil return” continuation.

## Common-catch local lifetime bypass

Normal successful/failure cleanup paths release intermediate retained objects through:
- `0x3BB24..0x3BB48`.

The common catch instead jumps directly to `0x3BB4C`, which starts at releasing the retained input bid.

Depending on the protected site and throw timing, retained:
- application controller;
- application;
- scene entity;
- UUID/UUID string;
- app view controller;
- main view or related intermediates

may have been acquired before the throw but have their normal local releases bypassed.

R-128 records this only as:
- `retainedIntermediateReleasesCouldBeBypassed = YES`.

It does not claim a guaranteed leak or model private ARC/unwind runtime ownership beyond the observed local control flow.

## Nested exception from reset inside the catch

Catch-internal reset call:
- `0x3BBC4..0x3BBCC` -> landing `0x3BBE0`, action 0.

If catch-level `resetHostingState` throws:
- preserve nested exception;
- `objc_end_catch`;
- resume unwind at `0x3BBE8`.

No second local typed swallow is attempted.

For the three failure-reset ranges, this proves the catch-induced retry is bounded to one retry.

## Unprotected behavior

All no-landing ranges propagate normally.

R-128 exposes a generic unprotected propagation outcome rather than inventing per-instruction cleanup behavior outside the LSDA-protected sites.

## Promoted runtime contract

Added:
- `DDCNABBuildSceneHostExceptionSite`:
  - `PreControllerPrivateWork`;
  - `PostControllerPrivateWork`;
  - `PrivateDeviceDecoration`;
  - `FailureReset`;
  - `CatchReset`;
  - `UnprotectedRange`.
- `DDCNABBuildSceneHostExceptionOutcome`.
- `DDResolveCNABBuildSceneHostExceptionOutcome(site)`.

For pre-controller private work:
- swallow expected exception;
- invoke reset from catch;
- force nil return;
- retained-intermediate releases may be bypassed;
- nonmatching type resumes unwind.

For post-controller private work:
- same, plus controller ivar had already been stored before protected call.

For failure reset:
- same common reset/nil behavior;
- retry reset from catch.

For private device decoration:
- swallow;
- controller ivar already stored;
- main view already acquired;
- skip remaining private decoration;
- continue returning main view;
- retained device-controller release may be bypassed;
- nonmatching type resumes unwind.

For catch reset:
- end active catch before resume unwind;
- propagate nested exception.

For unprotected:
- propagate.

Unknown/None returns all false.

## Explicit exclusions

R-128 does not:
- query SpringBoard application classes;
- allocate/init private scene entities or app view controllers;
- invoke private lifecycle/view/requested-mode selectors;
- resolve `_deviceAppViewController`;
- mutate home-grabber mode;
- invoke `resetHostingState`;
- mutate real `_appVC` or host globals;
- alter real object lifetimes through the resolver;
- synthesize/catch exceptions;
- invoke Objective-C catch/unwind runtime machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final verifier, CatDesk standard verification status, and `git diff --check` are run immediately before commit.

## Scout for next batch — 3AE50

Next earlier LSDA-bearing function:
- `3AE50 -> LSDA 0x114424`.
- Identity: `-[DDz2 evictFromPhoneThen:]`.

Direct LSDA scout decoded 25 entries:
- 12 action-5 ranges;
- 3 action-0 ranges;
- remaining no-landing gaps.

Action-0 ranges:
- `0x3AEE4..0x3AF00` -> `0x3B2C0`;
- `0x3AF14..0x3AF50` -> `0x3B2C0`;
- `0x3B29C..0x3B2A4` -> `0x3B2B4`.

Action-5 landing stubs:
- `0x3B25C`;
- `0x3B260`;
- `0x3B264`;
- `0x3B268`;
- `0x3B26C`;
- `0x3B270`;
- `0x3B274`;

all converge at common typed catch `0x3B278`.

Expected common catch:
- begin catch;
- retain caught object;
- invoke the retained completion/fallback block through its invoke pointer;
- release caught object;
- end catch;
- branch to `0x3B0BC` final outer cleanup.

Nonmatching type resumes unwind after block/dispose cleanup.

The catch-internal fallback-block invoke `0x3B29C..0x3B2A4` is action 0; if it throws, landing `0x3B2B4` ends the active catch and continues unwind cleanup.

R-129 must map each protected range against:
- no-evict/skip-frontmost file probes;
- SpringBoard workspace/request construction;
- application-context mutation;
- completion-handler selector setup;
- dispatch-after fallback scheduling;
- executeTransitionRequest;
- whether the fallback/completion block may already have been scheduled or invoked before each catch.

Only after that per-range timing is exact should any data-only exception outcome be promoted.

## Next

After the user pushes session-129 and confirms compiler green:
- R-129: decode/promote exact `3AE50 -> LSDA 0x114424` per-site eviction exception outcomes;
- preserve completion/fallback invocation ordering and scheduled-fallback timing;
- keep SpringBoard transition request construction/execution, dispatch scheduling, file I/O, and live callback invocation excluded from the resolver.

Known unresolved:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device runtime smoke testing.
