# LOG/session-153.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-152 commit `1299df0`; decode and promote exact data-only `365D4` display-configuration/resolution-quality publish exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `1299df0`.
- Working tree clean.
- User confirmed session-152 macOS CI/compiler GREEN.
- Local tracking ref reported ahead 1; assistant did not fetch/push.

## Target
- Function: `sub_365D4`.
- LSDA: `0x113FFC`.
- Role: retain the caller input, obtain a display object, probe optional FBSDisplayConfiguration pixel/scale data plus display bounds/frame fallback, commit geometry globals, format resolution/quality labels, deduplicate/persist them, and post the BLE-status Darwin notification.

## Exact LSDA call-site table
1. `0x365D4..0x36608` -> no landing.
2. `0x36608..0x36614 -> 0x369A0`, action 5.
3. `0x3661C..0x36628 -> 0x36998`, action 5.
4. `0x3663C..0x36678 -> 0x369A4`, action 5.
5. `0x3667C..0x36688 -> 0x3698C`, action 5.
6. `0x366B0..0x366CC -> 0x369A4`, action 5.
7. `0x366CC..0x366E4` -> no landing.
8. `0x366E4..0x36734 -> 0x369B8`, action 5.
9. `0x36814..0x3682C -> 0x36994`, action 5.
10. `0x3682C..0x3688C` -> no landing.
11. `0x3688C..0x368A8 -> 0x3699C`, action 5.
12. `0x368A8..0x368CC` -> no landing.
13. `0x368CC..0x36938 -> 0x3699C`, action 5.
14. `0x36938..0x369E8` -> no landing.

There are nine typed action-5 ranges and three distinct expected-catch continuation families.

## Catch family A — FBS config / pixel / scale -> display-bounds fallback
Landings:
- `0x369A4`;
- `0x3698C` first executes `fmov d8,d9`, then joins `0x369A4`.

Expected type at `0x369A4`:
- begin catch;
- end catch;
- branch to `0x366DC`.

`0x366DC` begins display `bounds`/frame fallback probing.

Nonmatching type routes onward to common unwind `0x369E4`.

This family does not force the function result false.

## Catch family B — display bounds/frame -> geometry validity gate
Landing:
- `0x369B8`.

Expected type:
- begin catch;
- end catch;
- branch directly to `0x36758`.

`0x36758` is the geometry validity gate.

This skips:
- remaining bounds/frame protected work;
- scale fallback derivation `0x3673C..0x36754`.

Nonmatching type ultimately resumes unwind.

## Catch family C — acquisition / class / format / dedup / publication -> false
Aliases:
- `0x36994`;
- `0x36998`;
- `0x3699C`;
- `0x369A0`.

These branch to common `0x369CC`.

Expected type:
- begin catch;
- end catch;
- set `w22 = 0`;
- branch to `0x36958`.

The target `0x36958` releases retained caller input x19 and performs epilogue.

It deliberately skips normal releases at:
- `0x36940`: x24 quality label;
- `0x36948`: x23 resolution string;
- `0x36950`: x20 display object.

Thus any of those locals already committed at the failing site can have their normal release bypassed.

Nonmatching type resumes unwind at `0x369E4`.

## Common input lifetime
The prefix is unprotected:
```
36600 objc_retain(input)
36604 mov x19,x0
```

Therefore every protected site begins with retained caller input x19 committed.

Forced-false catches still execute the x19 release at `0x36958..0x3695C`.

## Semantic site — display acquisition
Protected:
```
36608 sub_34250
36610 retain-autoreleased
```
Range ends before:
```
36614 mov x20,x0
```

Expected catch:
- force false;
- final input cleanup still runs;
- display acquisition/retain may already have started;
- no committed retained display x20 is asserted;
- temporary display cleanup can be bypassed.

## Semantic site — FBSDisplayConfiguration class lookup
Protected `objc_getClass("FBSDisplayConfiguration")` at `0x36624`.

At entry:
- retained display x20 definitely committed.

Expected catch:
- force false;
- x20 normal release at `0x36950` is bypassed;
- x19 input cleanup still runs.

## Semantic site — FBSDisplayConfiguration construction
The typed `0x3663C..0x36678` range begins with zero geometry fallback already loaded:
- d9/d11 from CGSizeZero;
- d12 = 0;
- d8 = d9.

It covers:
- `objc_alloc(FBSDisplayConfiguration)`;
- `initWithCADisplay:isMainDisplay:`;
- x22 commit at `0x36654`;
- initial pixelSize capability send at `0x36674`.

For construction exceptions before x22 commit:
- temporary config acquisition may have started;
- config cleanup can be bypassed;
- expected catch resumes at display-bounds fallback `0x366DC`;
- scale remains zero fallback.

## Semantic site — pixelSize capability
At `respondsToSelector:pixelSize`:
- retained display x20 committed;
- retained config x22 committed.

Expected catch:
- continues at `0x366DC`;
- x22 normal release `0x366D0..0x366D4` is skipped;
- zero scale fallback remains.

## Semantic site — pixelSize read
Protected `pixelSize` send is `0x36684`.

Expected landing first executes:
```
3698C fmov d8,d9
```
then common typed catch -> `0x366DC`.

Therefore:
- pixelSize capability definitely passed;
- x22 config committed;
- x22 release can be bypassed;
- working pixel width is explicitly restored to the fallback width before continuation;
- d11 remains the previously initialized fallback height when the read itself throws;
- scale stays zero fallback.

## Semantic site — scale capability/read
Typed range `0x366B0..0x366CC` covers:
- scale capability send;
- conditional scale send.

Normal scale result is not committed to d10 until `0x366CC`, outside protection, and d12 is not updated until `0x366D8`.

Expected catch:
- continues at `0x366DC`;
- retained config release can be bypassed;
- d12 remains zero fallback.

At the scale-read sub-site, scale capability has definitely passed.

## Unprotected config cleanup bridge
`0x366CC..0x366E4` is unprotected:
- commit d10 scale;
- release x22 config;
- copy d10 -> d12.

Exceptions here propagate.

## Semantic range — display bounds/frame fallback
Typed range `0x366E4..0x36734` covers:
- display bounds capability;
- optional bounds read and d9 width capture;
- optional frame capability;
- optional frame read.

Expected catch goes directly to `0x36758`, the geometry validity gate.

It skips scale derivation:
```
3673C..36754
```

Sub-site timing:
- bounds-read site => bounds capability definitely passed;
- frame-capability site => the preceding bounds probe has completed, but actual bounds read is not guaranteed because capability may have returned false;
- frame-read site => frame capability definitely passed, and frame dimensions remain uncommitted because d8/d11 capture begins at `0x36734`, outside the protected range.

The retained display x20 is not abandoned by this catch family; normal function continuation can later reach its cleanup.

## Geometry globals
After geometry validation/tolerance logic, unprotected code commits:
```
367F8/36800 -> xmmword_163AC0 width/height
36808       -> qword_163AD0 scale
```

These global writes happen before the next protected range.

They are not rolled back by later catches.

## Semantic site — resolution string formatting
Typed `0x36814..0x3682C` covers:
- `+[NSString stringWithFormat:@"%.0f × %.0f"]`;
- retain-autoreleased result.

Range ends before:
```
3682C mov x23,x0
```

At entry:
- retained display x20 committed;
- geometry/scale globals already committed.

Expected catch:
- force false;
- x20 normal release is bypassed;
- temporary resolution string construction/retain may have started;
- no committed x23 resolution string is asserted;
- geometry globals persist;
- x19 input cleanup still runs.

## Resolution/quality local commits
The unprotected bridge `0x3682C..0x3688C`:
- commits retained resolution string x23;
- computes result bit w22 from height;
- chooses static quality label;
- retains quality label into x24.

Exceptions in this bridge propagate.

## Semantic sites — resolution/quality dedup equality
Typed `0x3688C..0x368A8` covers:
- resolution string equality with `qword_163AD8`;
- when needed, quality equality with `qword_163AE0`.

At both equality calls:
- display x20 committed;
- resolution x23 committed;
- quality x24 committed;
- geometry globals committed.

Expected catch:
- force false;
- normal x24/x23/x20 releases are all bypassed;
- x19 input cleanup still runs.

The quality-equality site is reached only after the resolution equality returned matched/equal.

## Unprotected dedup-global stores
`0x368A8..0x368CC` is unprotected and contains:
- `objc_storeStrong(qword_163AD8, x23)`;
- `objc_storeStrong(qword_163AE0, selectedQuality)`.

Thus every protected publication sub-site begins only after both dedup globals were stored successfully.

Exceptions in these stores propagate and may partially mutate global state.

## Late publication typed range
Typed `0x368CC..0x36938` covers:
1. CFPreferencesSetAppValue headunit_resolution.
2. CFPreferencesSetAppValue headunit_video_quality.
3. CFPreferencesAppSynchronize.
4. CFNotificationCenterGetDarwinNotifyCenter.
5. NSString stringWithUTF8String notification-name creation.
6. CFNotificationCenterPostNotification.

At every sub-site:
- display x20 committed;
- resolution x23 committed;
- quality x24 committed;
- geometry globals committed;
- qword_163AD8 and qword_163AE0 already stored.

Expected catch:
- force false;
- bypass x24/x23/x20 releases;
- keep x19 input cleanup;
- do not rollback earlier globals/preferences/notification effects.

### Resolution preference SetValue
The preference write may already have partially applied before throw.

### Quality preference SetValue
Reached only after resolution preference SetValue returned.

So resolution preference is definitely set before this call; quality preference may apply before throw.

### Preferences synchronize
Reached after both SetValue calls returned.

Both preference values are definitely set before synchronize; synchronization may partially apply before throw.

### Darwin center acquisition
Reached only after synchronize completed.

Both preference values are set and synchronize completed.

### Notification-name construction
Reached after the Darwin center was acquired and committed to x21.

### Darwin post
Reached only after notification-name construction returned.

If post throws, notification delivery may already have partially occurred; no local rollback exists.

## Final unprotected cleanup
`0x36938..0x369E8` has no landing for normal cleanup:
- release x24 quality label;
- release x23 resolution string;
- release x20 display;
- release x19 input;
- return.

Exceptions in these unprotected releases propagate.

Catch landing/unwind code also resides in this tail.

## Promoted runtime contract
Added:
- `DDDisplayConfigurationPublishExceptionSite` with semantic sites for:
  - display acquisition;
  - FBS class lookup/construction;
  - pixelSize capability/read;
  - scale capability/read;
  - bounds capability/read;
  - frame capability/read;
  - resolution formatting;
  - resolution/quality dedup equality;
  - two preference writes;
  - synchronize;
  - Darwin center;
  - notification name;
  - notification post;
  - unprotected range.
- `DDDisplayConfigurationPublishExceptionOutcome`.
- `DDResolveDisplayConfigurationPublishExceptionOutcome(site)`.

Metadata captures:
- which of the three catch continuations applies;
- false-result forcing;
- pixel-width and zero-scale fallback behavior;
- skipped scale derivation before geometry-validity gate;
- input/display/config/resolution/quality ownership boundaries;
- release-bypass;
- geometry-global timing;
- dedup-global timing;
- ordered preferences/Darwin side-effect timing;
- unprotected propagation;
- nonmatching typed unwind.

## Explicit exclusions
R-152 does not:
- execute display/FBS queries;
- call pixelSize/scale/bounds/frame;
- mutate geometry/dedup globals;
- format or retain live strings;
- write/synchronize preferences;
- post Darwin notifications;
- mutate real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 365A8
Next earlier LSDA-bearing function:
- `365A8 -> LSDA 0x113FE8`.
- Role: wrapper invoking `sub_365D4(CFSTR("display.changed"), YES)`.

Exact table:
1. `0x365B0..0x365C0 -> 0x365C8`, action 1 catch-all.
2. `0x365C0..0x365D4` -> no landing.
Prefix `0x365A8..0x365B0` is unprotected.

Protected range prepares:
- static `display.changed` string;
- force flag 1;
- calls `sub_365D4`.

Landing `0x365C8`:
- unconditional `objc_begin_catch`;
- restore frame;
- tail `objc_end_catch`;
- immediate return.

There is no discriminator/nonmatching branch.

R-153 should promote wrapper-level catch-all swallow/immediate-return metadata only. Inner R-152 site behavior remains represented by the R-152 resolver and should not be duplicated.

## Scout after R-153 — 3640C
Next earlier LSDA-bearing function:
- `3640C -> LSDA 0x113FD0`.
- Role: `+[DDz1 carPlayConnected]`.

Exact table decodes:
1. `0x36418..0x3643C -> 0x3644C`, action 5.
2. `0x3643C..0x36474` -> no landing.
Prefix before `0x36418` is unprotected.

Protected range covers:
- `objc_getClass("AVExternalDevice")`;
- optional `currentCarPlayExternalDevice`;
- retain-autoreleased current device.

Expected typed catch at `0x3644C`:
- begin/end-catch;
- force false result via `0x3645C`.

Nonmatching type resumes unwind at `0x36470`.

The range ends before the returned device is tested/committed as the boolean result and before normal device release.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
