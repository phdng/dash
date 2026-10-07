# LOG/session-159.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-158 commit `93c1aea`; decode and promote exact data-only `358F0` splash presentation/preferences/image/dispatch exception routing, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `93c1aea`.
- Working tree clean and synchronized with origin.
- User confirmed session-158 macOS CI/compiler GREEN.

## Target
- Function: `sub_358F0`.
- LSDA: `0x113EDC`.
- Role: no-splash gate, host/content-view selection, splash preference parsing, image-path selection/loading, splash view/image hierarchy construction, duration parsing, global splash state, weak captures and delayed splash-fade/watchdog dispatch.

## LSDA structure
The call-site table has 29 entries.

Protected landing aliases:
- `0x35F60`
- `0x35F64`
- `0x35F68`
- `0x35F6C`
- `0x35F70`
- `0x35F74`
- `0x35F78`
- `0x35F7C`
- `0x35F80`

All alias to common discriminator `0x35F84`.

Expected type:
- begin catch;
- restore frame;
- end catch;
- return immediately.

Nonmatching type:
- resume unwind at `0x35FB8`.

## Action-chain distinction
Action table:
- action index 7 -> filter 1 only;
- action index 5 -> filter 1 followed by cleanup action 0.

Therefore:
- initial no-splash marker probe is typed-catch-only;
- later protected ranges are typed catch plus cleanup chain;
- expected type returns in both cases;
- nonmatching exceptions propagate;
- action-5 ranges can route through the local cleanup landing before resume unwind.

R-158 records this distinction explicitly instead of treating all protected ranges as identical.

## Exact call-site table
1. `0x35924..0x35940 -> 0x35F84`, action 7.
2. `0x35940..0x3595C` unprotected.
3. `0x3595C..0x35984 -> 0x35F70`, action 5.
4. `0x35984..0x359B4` unprotected.
5. `0x359B4..0x359BC -> 0x35F60`, action 5.
6. `0x359F4..0x35A3C -> 0x35F7C`, action 5.
7. `0x35A3C..0x35A50` unprotected.
8. `0x35A50..0x35AF4 -> 0x35F7C`, action 5.
9. `0x35AF4..0x35B10` unprotected.
10. `0x35B10..0x35B18 -> 0x35F7C`, action 5.
11. `0x35B1C..0x35B5C -> 0x35F78`, action 5.
12. `0x35B5C..0x35B80` unprotected.
13. `0x35B80..0x35BB0 -> 0x35F78`, action 5.
14. `0x35BB0..0x35BC8` unprotected.
15. `0x35BC8..0x35BCC -> 0x35F78`, action 5.
16. `0x35BD4..0x35C14 -> 0x35F80`, action 5.
17. `0x35C14..0x35C1C` unprotected.
18. `0x35C1C..0x35C5C -> 0x35F80`, action 5.
19. `0x35C64..0x35C8C -> 0x35F6C`, action 5.
20. `0x35C98..0x35D04 -> 0x35F74`, action 5.
21. `0x35D04..0x35D0C` unprotected.
22. `0x35D0C..0x35D18 -> 0x35F6C`, action 5.
23. `0x35D18..0x35D2C` unprotected.
24. `0x35D2C..0x35D78 -> 0x35F68`, action 5.
25. `0x35D78..0x35D8C` unprotected.
26. `0x35D8C..0x35DB0 -> 0x35F64`, action 5.
27. `0x35DB0..0x35F2C` unprotected.
28. `0x35F2C..0x35F30 -> 0x35F7C`, action 5.
29. `0x35F30..0x35FBC` unprotected.

## Semantic site — no-splash marker probe
Protected `0x35924..0x35940`:
- `+[NSFileManager defaultManager]`;
- retain-autoreleased manager;
- manager commit x19;
- `fileExistsAtPath:/var/tmp/duodash_ab_nosplash`.

Expected catch:
- returns immediately;
- manager acquisition/retain may have started;
- normal manager release at `0x35948` is bypassed.

This is the only action-index-7 protected range.

The marker result commit and manager release are outside protection.

## Semantic site — content-view selection
Protected `0x3595C..0x35984` can:
- query a contentView;
- retain it into x21;
- when non-null, query/retain the contentView again for the selected view candidate.

The range ends before final selected-view commit/branch normalization.

Expected catch:
- returns immediately;
- retained/intermediate content-view ownership may exist;
- normal local releases can be bypassed.

Fallback retain of the alternate view and some commit/release logic are unprotected.

## Semantic site — selected-view bounds
Protected `0x359B4..0x359BC`:
- selected view x19 is already committed;
- sends `bounds`.

Expected catch:
- returns immediately;
- selected-view release at final `0x35F30..0x35F34` is bypassed.

Bounds validity checks are unprotected.

## Semantic group — splash preference load/parse
Protected ranges:
- `0x359F4..0x35A3C`;
- `0x35A50..0x35AF4`;
- `0x35B10..0x35B18`.

Covered work includes:
- CFPreferencesSynchronize;
- CFPreferencesCopyValue("splash_selected");
- type probing;
- string values "0"/"1"/"2"/"3";
- integer-number fallback;
- CFRelease of copied preference value.

Expected catches:
- selected view is already committed;
- selected-view release may be bypassed;
- synchronize may already have affected preferences before a throw;
- copied preference object may already be committed;
- its normal release may be bypassed.

Selection normalization itself is partly unprotected.

## Semantic group — image-path selection/probe
Protected ranges:
- `0x35B1C..0x35B5C`;
- `0x35B80..0x35BB0`.

Covered work:
- custom/default splash path canonicalization;
- path length;
- NSFileManager defaultManager;
- file-existence probe;
- formatted fallback image path;
- canonicalization of fallback path.

Expected catches:
- selected view remains committed;
- manager/path acquisition may be in progress or committed;
- normal local releases can be bypassed.

The manager-result commit/release bridge and some path commits/releases are unprotected.

## Semantic site — pre-build removeSplash
Protected `0x35BC8..0x35BCC`:
- calls `removeSplash`.

Expected catch:
- returns immediately;
- selected view/image path locals may remain unreleased;
- removeSplash may have already applied partial side effects.

No rollback exists.

## Semantic group — splash UIView/image hierarchy construction
Protected ranges:
- `0x35BD4..0x35C14`;
- `0x35C1C..0x35C5C`;
- `0x35C64..0x35C8C`;
- `0x35C98..0x35D04`;
- `0x35D0C..0x35D18`.

Covered work includes:
- splash UIView allocation/init;
- black background color acquisition and application;
- user-interaction/tag/autoresizing/clips/opaque properties;
- UIImage loading/type check;
- UIImageView allocation/properties/image assignment;
- image-view attach to splash view;
- splash-view attach to selected view.

Expected catches:
- return immediately;
- committed selected view/image path/splash intermediates can have normal releases bypassed;
- splash view properties and hierarchy mutation may have partially applied before throw.

The global strong store of the splash view occurs later, outside these ranges.

## Global splash strong store
Unprotected:
```
35D18 load owner
35D1C owner+0x20
35D20 splash view
35D24 objc_storeStrong
```

Therefore every protected duration-file range begins after the global splash view strong store has completed.

Later catches do not rollback that store.

## Semantic group — duration-file read/parse
Protected ranges:
- `0x35D2C..0x35D78`;
- `0x35D8C..0x35DB0`.

Covered work:
- stringWithContentsOfFile for `/var/tmp/duodash_ab_splash_secs`;
- whitespace/newline character set;
- trimmed duration string;
- length/doubleValue;
- CACurrentMediaTime.

Expected catches:
- global splash store is already committed;
- selected view/image path/splash locals may remain unreleased;
- duration string/intermediate ownership may exist;
- `qword_163C30` is definitely not committed yet.

The deadline calculation/store begins after the protected range.

## Unprotected deadline / weak / dispatch pipeline
`0x35DB0..0x35F2C` is unprotected.

It includes:
- duration clamp to [0.5,15] else 3.0;
- `qword_163C30 = CACurrentMediaTime + duration + 0.3 + 0.75`;
- weak owner initialization;
- first dispatch_time;
- first block strong splash capture;
- first copied weak capture;
- first `dispatch_after`;
- second dispatch_time;
- second copied weak capture;
- second strong splash capture;
- second `dispatch_after`;
- queue/capture/weak cleanup;
- duration/image/path local cleanup.

Any exception here propagates.

Depending on where it occurs:
- deadline may already be committed;
- weak capture may already be initialized;
- first dispatch may already be scheduled;
- second dispatch may already be scheduled.

No typed catch handles those failures.

## Semantic site — disabled-selection removeSplash
Protected `0x35F2C..0x35F30`:
- calls `removeSplash` on the selection-zero path.

Expected catch:
- returns immediately;
- selected-view final release at `0x35F30..0x35F34` is skipped;
- removeSplash side effects may already have applied.

## Promoted runtime contract
Added:
- `DDSplashPresentationExceptionSite` semantic groups for marker probe, content view, bounds, preference parsing, image path, remove-before-build, splash hierarchy, duration parsing, disabled-selection remove, post-duration unprotected dispatch pipeline, and generic unprotected range.
- `DDSplashPresentationExceptionOutcome`.
- `DDResolveSplashPresentationExceptionOutcome(site)`.

Metadata captures:
- expected typed swallow + immediate return;
- action-7 vs action-5 nonmatching cleanup distinction;
- file-manager lifetime;
- selected-view lifetime;
- preference synchronization/value lifetime;
- image-path lifetime;
- removeSplash side-effect persistence;
- splash view/property/hierarchy partial effects;
- global splash-store timing;
- duration/deadline timing;
- unprotected weak/dispatch side-effect milestones;
- propagation.

## Explicit exclusions
R-158 does not:
- query live preferences/files;
- create/load live images/views;
- mutate UI hierarchy/global splash state;
- schedule live dispatch blocks;
- mutate real ownership;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 35880
Next earlier LSDA-bearing function:
- `35880 -> LSDA 0x113EC8`.

Exact table:
1. `0x35894..0x358D4 -> 0x358E0`, action 1 catch-all.
2. `0x358D4..0x358F0` unprotected.

Protected work:
- layer opacity getter;
- compare against 0.99;
- when equal: CATransaction begin;
- setDisableActions:YES;
- setOpacity:1.0;
- CATransaction commit.

Landing `0x358E0`:
- unconditional begin/end-catch;
- immediate return;
- no discriminator.

R-159 should split:
- opacity getter;
- transaction begin;
- disable-actions;
- opacity mutation;
- commit;
and record prior transaction/mutation side effects without rollback.

## Scout after R-159 — 356A0
Next earlier LSDA-bearing function:
- `356A0 -> LSDA 0x113E98`.

Exact call-site table:
1. `0x356A0..0x356DC` unprotected.
2. `0x356DC..0x356F8 -> 0x35858`, action 5.
3. `0x356FC..0x3573C -> 0x35854`, action 5.
4. `0x3573C..0x35750` unprotected.
5. `0x35750..0x35778 -> 0x35854`, action 5.
6. `0x35778..0x35880` unprotected.

This helper mixes:
- weak owner;
- retained target view;
- hidden/live-present gates;
- layer acquisition/opacity;
- opacity animation probe;
- CATransaction mutation;
- counter decrement;
- retained layer capture;
- delayed dispatch to `sub_35880`.

R-160 should decode all three typed ranges and their continuation/cleanup behavior separately.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
