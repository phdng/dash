# LOG/session-152.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-151 commit `42153ac`; decode and promote exact data-only `369E8` layout-area publish exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `42153ac`.
- Working tree clean and synchronized with origin.
- User confirmed session-151 macOS CI/compiler GREEN.

## Target
- Function: `sub_369E8`.
- LSDA: `0x114058`.
- Role: classify layout-area label, build a status string, deduplicate it against global `qword_163AE8`, persist `headunit_layout_area`, synchronize preferences, and post the BLE-status Darwin notification.

## Exact LSDA call-site table
1. `0x36A20..0x36A24 -> 0x36DE0`, action 5.
2. `0x36C64..0x36C7C -> 0x36DDC`, action 5.
3. `0x36CC0..0x36CE0 -> 0x36DEC`, action 5.
4. `0x36CFC..0x36D1C -> 0x36DD8`, action 5.
5. `0x36D28..0x36D2C -> 0x36DEC`, action 5.
6. `0x36D30..0x36D40 -> 0x36DE8`, action 0.
7. `0x36D40..0x36D94 -> 0x36DEC`, action 5.
8. `0x36D94..0x36DA4 -> 0x36DE8`, action 0.
9. `0x36DA4..0x36E00` -> no landing.

Catch tail:
- `0x36DD8 -> 0x36DDC -> 0x36DEC`;
- `0x36DE0` routes nonzero discriminator to `0x36DEC`, zero to unwind;
- `0x36DEC` accepts expected type 1, begin/end-catches, then jumps to final stack cleanup `0x36DA4`;
- nonmatching type routes to `0x36DE8`;
- `0x36DE8` resumes unwind.

Thus expected typed exceptions return from the function after final stack cleanup, while action-0 and nonmatching exceptions propagate.

## Typed site 1 — initial CGRectIsEmpty
`0x36A20..0x36A24` covers only `CGRectIsEmpty`.

At this point:
- no Objective-C label/status local has been constructed;
- no global/prefs/notification side effect has started.

Expected typed catch:
- swallow;
- skip the entire function body;
- final stack cleanup/return.

No ownership cleanup claim is needed.

## Typed site 2 — optional +dock label append
`0x36C64..0x36C7C` covers:
- `stringByAppendingString:@"+dock"`;
- retain-autoreleased result.

The range ends before:
```
36C7C  mov x19,x0
```

Therefore:
- appended-label construction/retain may have started;
- no committed retained appended label in x19 is guaranteed;
- expected catch skips normal final label release;
- a temporary retained label result may be left without local cleanup.

R-151 records temporary label construction/release-bypass, not definite x19 ownership.

## Typed sites 3/4 — status string formatting
Two alternative protected branches:
- `0x36CC0..0x36CE0`;
- `0x36CFC..0x36D1C`.

Both execute:
- `+[NSString stringWithFormat:]`;
- retain-autoreleased result.

Both ranges end before:
```
36D1C  mov x20,x0
```

Therefore:
- status-string construction/retain may have started;
- committed retained status x20 is not guaranteed on caught path;
- x19 may already be a committed retained appended label when the +dock path was used, otherwise it is a static CFString;
- expected catch jumps past normal x20/x19 releases.

R-151 records possible committed retained-label lifetime and temporary status-string construction/release-bypass.

## Typed site 5 — status dedup equality
`0x36D28..0x36D2C` covers:
- `-[NSString isEqualToString:]` comparing committed status x20 with global `qword_163AE8`.

At entry:
- retained status x20 is definitely committed;
- x19 may be retained appended label or static label;
- no new global/prefs/notify side effect has occurred.

Expected catch:
- returns via final stack cleanup;
- bypasses normal x20 release;
- can also bypass retained appended-label release when that ownership exists;
- does not perform global store/prefs/notify work.

## Action-0 site — global status strong store
`0x36D30..0x36D40` covers:
```
objc_storeStrong((id *)&qword_163AE8, x20)
```

This is action 0:
- no local typed swallow;
- landing `0x36DE8` resumes unwind.

If the store itself faults after starting:
- global `qword_163AE8` may already have changed;
- x20 status is definitely committed;
- a retained appended label may also be live;
- normal x20/x19 releases are bypassed by unwind.

R-151 records possible global-store side effect plus propagation/release-bypass; it does not assert rollback.

## Typed late range — preferences and Darwin publication
`0x36D40..0x36D94` begins only after the global strong store returned successfully.

At every semantic sub-site in this range:
- global `qword_163AE8` definitely stores the new status;
- retained status x20 is definitely committed;
- x19 may be retained appended label;
- typed catch skips normal final x20/x19 releases.

### CFPreferences SetValue
At `CFPreferencesSetAppValue`:
- global status already committed;
- preferences write could already have partially applied before throw.

Expected catch does not rollback global state or preferences.

### CFPreferences synchronize
Reached only after SetValue returned.

Therefore:
- global status definitely stored;
- preferences value definitely set;
- synchronize may have partially persisted before throw.

### Darwin notification center acquisition
Reached only after synchronize returned.

Therefore:
- global status stored;
- preferences value set;
- synchronize call completed.

If center acquisition throws, all those earlier side effects persist.

### Notification-name construction
Reached after:
```
36D64 CFNotificationCenterGetDarwinNotifyCenter
36D68 mov x21,x0
```

Therefore the Darwin center is definitely acquired before protected notification-name construction.

### Darwin notification post
Reached only after notification-name construction returned.

If `CFNotificationCenterPostNotification` throws:
- global status store completed;
- preferences SetValue completed;
- synchronize completed;
- Darwin center acquired;
- notification name constructed;
- notification delivery itself may already have partially occurred.

Catch performs no rollback of any of those effects.

## Action-0 final local cleanup
`0x36D94..0x36DA4` contains:
```
36D94 mov x0,x20
36D98 objc_release
36D9C mov x0,x19
36DA0 objc_release
```

The range is action 0 and resumes unwind.

Semantic split:

### Status release cleanup
If x20 release throws:
- status release is not known complete;
- retained appended-label release later in the sequence can be skipped;
- unwind propagates.

### Label release cleanup
If x19 release throws:
- x20 release definitely completed first;
- label release may be incomplete;
- unwind propagates.

These are cleanup-unwind outcomes, not successful catches.

## Final unprotected tail
`0x36DA4..0x36E00` has no landing.

It contains stack-cookie validation, return, and the catch/unwind landing code itself.

Any exception outside protected ranges propagates according to the active runtime/unwind path.

## Promoted runtime contract
Added:
- `DDLayoutAreaPublishExceptionSite`:
  - initial rect-empty check;
  - dock-suffix label append;
  - status formatting;
  - status dedup equality;
  - global-status store unwind;
  - preferences SetValue;
  - preferences synchronize;
  - Darwin-center acquisition;
  - notification-name construction;
  - Darwin notification post;
  - final status cleanup unwind;
  - final label cleanup unwind;
  - unprotected range.
- `DDLayoutAreaPublishExceptionOutcome`.
- `DDResolveLayoutAreaPublishExceptionOutcome(site)`.

Metadata captures:
- expected typed swallow + immediate return;
- temporary-vs-committed retained label/status ownership;
- retained local release-bypass;
- global status store timing;
- preferences SetValue/synchronize timing;
- Darwin center/name/post ordering;
- possible notification side-effect persistence;
- action-0 resume-unwind semantics;
- final cleanup ordering;
- unprotected propagation;
- nonmatching typed unwind.

## Explicit exclusions
R-151 does not:
- execute CGRect/string formatting operations;
- mutate `qword_163AE8`;
- write/synchronize CFPreferences;
- obtain/post Darwin notifications;
- mutate real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 365D4
Next earlier LSDA-bearing function:
- `365D4 -> LSDA 0x113FFC`.
- Role: probe FBS display configuration / display bounds+frame, derive pixel dimensions and scale, commit headunit geometry globals, build resolution/quality labels, deduplicate/persist them, and post the same BLE-status Darwin notification.

Exact 14-entry table:
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

Landing families have different continuations:
- `0x3698C`: restore `d8=d9`, then join `0x369A4`;
- `0x369A4`: expected catch -> continue at `0x366DC`, i.e. fallback/continue display-configuration probing;
- `0x369B8`: expected catch -> continue at `0x36758`, i.e. later bounds/frame fallback path;
- `0x36994/0x36998/0x3699C/0x369A0`: aliases to `0x369CC`;
- `0x369CC`: expected catch -> set result false (`w22=0`) and jump cleanup `0x36958`;
- nonmatching type ultimately resumes unwind at `0x369E4`.

R-152 must not collapse these into one generic catch. It should separately map:
- display object acquisition;
- FBSDisplayConfiguration class/init;
- pixelSize capability/read;
- scale capability/read;
- display bounds/frame capability/read fallback;
- global geometry/scale commit timing;
- resolution-string and quality-label ownership;
- dedup global stores;
- preferences + Darwin publication;
- late release-bypass;
- false-result catch family vs geometry-continuation catch families.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
