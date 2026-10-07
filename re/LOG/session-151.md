# LOG/session-151.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-150 commit `43a6ef8`; decode and promote exact data-only `36E00` display-bounds zero-fallback exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `43a6ef8`.
- Working tree clean and synchronized with origin.
- User confirmed session-150 macOS CI/compiler GREEN.

## Target
- Function: `sub_36E00`.
- LSDA: `0x11409C`.
- Role: read `UIScreen.mainScreen.bounds`, derive a dimension-based scalar, and return zero for expected protected exceptions.

## Exact LSDA
1. `0x36E18..0x36E2C -> 0x36E80`, action 5.
2. `0x36E2C..0x36E98` -> no landing.

The protected range covers:
- `+[UIScreen mainScreen]`;
- retain-autoreleased UIScreen;
- x19 commit;
- `bounds`.

All dimension capture and scalar calculation is outside protection.

## Raw ARM64 ordering
```
36E18  +[UIScreen mainScreen]
36E20  retain-autoreleased
36E24  mov x19,x0
36E28  bounds

36E2C  fmov d8,d2
36E30  fmov d9,d3
36E34  mov x0,x19
36E38  objc_release
...
36E60  fmov d0,xzr
...
36E80  cmp w1,#1
36E84  b.ne 36E94
36E88  objc_begin_catch
36E8C  objc_end_catch
36E90  b 36E60
36E94  resume unwind
```

## Expected catch behavior
Expected action-5 exception:
- begin catch;
- end catch;
- jump directly to `0x36E60`;
- set return register `d0 = 0.0`;
- return zero.

The catch skips:
- d8/d9 bounds-dimension capture;
- normal UIScreen release;
- min-dimension selection;
- numeric range gate;
- half-dimension multiplication.

Nonmatching type resumes unwind at `0x36E94`.

## Semantic site 1 — main-screen acquisition
Protected operations before `mov x19,x0`:
- `+[UIScreen mainScreen]`;
- retain-autoreleased result.

If expected exception occurs:
- catch returns 0.0;
- x19 is not guaranteed committed;
- UIScreen acquisition/retain may already have started;
- temporary UIScreen cleanup may be bypassed;
- no bounds dimensions are committed.

## Semantic site 2 — bounds read
At `bounds`:
- retained UIScreen x19 is definitely committed.

If expected exception occurs:
- catch returns 0.0;
- normal x19 release at `0x36E34..0x36E38` is bypassed;
- d8/d9 are still unmodified by this function because their assignment begins at `0x36E2C`, outside the protected range;
- no partial bounds dimension is consumed by fallback.

## Promoted runtime contract
Added:
- `DDDisplayBoundsFallbackExceptionSite`:
  - `MainScreenAcquisition`;
  - `BoundsRead`;
  - `UnprotectedRange`.
- `DDDisplayBoundsFallbackExceptionOutcome`.
- `DDResolveDisplayBoundsFallbackExceptionOutcome(site)`.

Both typed sites record:
- expected exception swallowed;
- forced zero return;
- bounds result ignored;
- bounds dimensions definitely uncommitted before catch routing;
- nonmatching type resumes unwind.

Acquisition site:
- temporary UIScreen acquisition may have started;
- temporary cleanup can be bypassed.

Bounds site:
- retained UIScreen definitely committed;
- retained-screen release can be bypassed.

Unprotected:
- propagates.

## Explicit exclusions
R-150 does not:
- call `+[UIScreen mainScreen]`;
- query live bounds;
- reproduce screen-dimension calculations;
- mutate real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 369E8
Next earlier LSDA-bearing function:
- `369E8 -> LSDA 0x114058`.
- Role: classify layout area, build a status string, deduplicate against global `qword_163AE8`, persist `headunit_layout_area`, synchronize preferences, and post a Darwin notification.

Exact 9-entry table:
1. `0x36A20..0x36A24 -> 0x36DE0`, action 5.
2. `0x36C64..0x36C7C -> 0x36DDC`, action 5.
3. `0x36CC0..0x36CE0 -> 0x36DEC`, action 5.
4. `0x36CFC..0x36D1C -> 0x36DD8`, action 5.
5. `0x36D28..0x36D2C -> 0x36DEC`, action 5.
6. `0x36D30..0x36D40 -> 0x36DE8`, action 0.
7. `0x36D40..0x36D94 -> 0x36DEC`, action 5.
8. `0x36D94..0x36DA4 -> 0x36DE8`, action 0.
9. `0x36DA4..0x36E00` -> no landing.

Observed catch tail:
- `0x36DD8 -> 0x36DDC -> 0x36DEC`;
- `0x36DEC` checks expected type, begin/end-catches, then jumps final function cleanup at `0x36DA4`;
- nonmatching paths route through action-0/unwind handling;
- `0x36DE0` has an extra discriminator-zero branch before the common unwind path.

R-151 must map each protected site independently:
- initial `CGRectIsEmpty`;
- optional label `stringByAppendingString:` retain;
- both `NSString stringWithFormat:` formatting branches + retained status-string commit;
- status-string equality check;
- global strong-store / CFPreferences write/synchronize / Darwin notification creation+post;
- action-0 cleanup ranges for retained status/label releases.

Do not infer rollback of global/preferences/notification side effects once a later protected call has begun.

## Scout after R-151
Next earlier LSDA-bearing function:
- `365D4 -> LSDA 0x113FFC`.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
