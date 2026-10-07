# LOG/session-150.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-149 commit `c072275`; decode and promote exact data-only `370F8` DDz1 nudge-present gate exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `c072275`.
- Working tree clean.
- User confirmed session-149 macOS CI/compiler GREEN.
- Local tracking ref still reported ahead 1 at session start; assistant did not fetch/push.

## Target
- Function: `sub_370F8`.
- LSDA: `0x1140B4`.
- Role: gate a DDz1 `nudgePresent:@"tick"` call on DDz1 visibility/live-present state and a file marker.

## Exact LSDA call-site table
1. `0x37110..0x37158 -> 0x3718C`, action 5.
2. `0x37158..0x37168` -> no landing.
3. `0x37168..0x37178 -> 0x3718C`, action 5.
4. `0x37178..0x371AC` -> no landing.

Both protected ranges converge on common typed catch `0x3718C`.

Expected type:
- compare discriminator with 1;
- begin catch;
- restore frame/callee-saved registers;
- end catch;
- return immediately.

Nonmatching type:
- resume unwind at `0x371A8`.

The expected catch performs no local `objc_release` for any retained DDz1/NSFileManager object that was live when the exception occurred.

## Raw ARM64 ordering

```
37110  +[DDz1 shared]
37118  retain-autoreleased
3711C  mov x19,x0                 ; DDz1 commit

37120  visible
37124  if false -> 37178

3712C  livePresentRunning
37130  if true -> 37178

3713C  +[NSFileManager defaultManager]
37144  retain-autoreleased
37148  mov x20,x0                 ; manager commit
37154  fileExistsAtPath:

37158  mov x21,x0                 ; marker result commit, UNPROTECTED
3715C  mov x0,x20
37160  objc_release               ; manager release, UNPROTECTED
37164  if marker true -> 37178

37168  load "tick"
37170  mov x0,x19
37174  nudgePresent:

37178  mov x0,x19
37188  tail objc_release          ; final DDz1 release, UNPROTECTED

3718C  cmp w1,#1
37190  b.ne 371A8
37194  objc_begin_catch
...
371A4  tail objc_end_catch
371A8  resume unwind
```

## Semantic site 1 — shared DDz1 acquisition
Protected operations:
- `+[DDz1 shared]`;
- retain-autoreleased result.

The range can throw before `mov x19,x0`.

Expected catch:
- swallows the expected typed exception;
- returns immediately;
- no committed retained controller x19 is asserted;
- DDz1 acquisition/retain may already have started;
- temporary DDz1 cleanup can be bypassed.

## Semantic site 2 — visible check
At `visible`:
- retained DDz1 x19 is definitely committed.

Expected catch:
- returns immediately;
- bypasses final normal DDz1 release at `0x37178..0x37188`.

No visibility result is known before the protected call itself.

## Semantic site 3 — livePresentRunning check
This site is reached only if:
- retained DDz1 x19 is committed;
- `visible` returned true.

If `livePresentRunning` throws:
- expected catch returns immediately;
- DDz1 release can be bypassed;
- no file-manager work has begun.

R-149 records `visibleCheckDefinitelyPassedBeforeProtectedCall`.

## Semantic site 4 — NSFileManager acquisition
This site is reached only if:
- x19 retained DDz1 committed;
- `visible` returned true;
- `livePresentRunning` returned false.

Protected operations:
- `+[NSFileManager defaultManager]`;
- retain-autoreleased result.

The exception may occur before `mov x20,x0`, so no committed manager x20 is asserted for the whole site.

Expected catch may bypass:
- retained DDz1 release;
- temporary manager cleanup if manager acquisition/retain already produced a temporary object.

## Semantic site 5 — marker-file check
At `fileExistsAtPath:`:
- DDz1 x19 is retained and committed;
- visible=true is already established;
- livePresentRunning=false is already established;
- NSFileManager x20 is retained and committed.

The protected range ends immediately after the send, before `mov x21,x0`.

If it throws:
- expected catch returns immediately;
- both retained DDz1 and retained manager releases can be bypassed;
- no committed marker result is asserted.

## Unprotected marker bridge
`0x37158..0x37168` is outside local exception protection.

It:
- commits file-exists result to w21;
- releases retained manager x20;
- branches away when the marker exists.

Therefore any control flow reaching the second protected range has already established:
- visible=true;
- livePresentRunning=false;
- marker check completed;
- marker absent=false result means no marker file exists;
- NSFileManager release completed;
- retained DDz1 x19 remains live.

Exceptions in this bridge propagate normally.

## Semantic site 6 — nudgePresent send
Protected range `0x37168..0x37178` covers the `nudgePresent:@"tick"` call.

At entry:
- retained DDz1 x19 definitely committed;
- visible check definitely passed;
- livePresentRunning definitely returned false;
- marker check definitely completed;
- marker is definitely absent;
- file manager has definitely been released.

If `nudgePresent:` throws:
- expected typed catch returns immediately;
- final DDz1 release at `0x37178..0x37188` is bypassed;
- any nudge side effects already applied before the exception are not rolled back locally.

## Promoted runtime contract
Added:
- `DDNudgePresentGateExceptionSite`:
  - `SharedControllerAcquisition`;
  - `VisibleCheck`;
  - `LivePresentRunningCheck`;
  - `FileManagerAcquisition`;
  - `MarkerFileCheck`;
  - `NudgePresentSend`;
  - `UnprotectedRange`.
- `DDNudgePresentGateExceptionOutcome`.
- `DDResolveNudgePresentGateExceptionOutcome(site)`.

Recorded evidence-safe metadata includes:
- typed swallow + immediate return;
- temporary-vs-committed DDz1 ownership;
- visible=true admission into later sites;
- livePresentRunning=false admission into file-marker/nudge sites;
- temporary-vs-committed NSFileManager ownership;
- marker-check/result availability boundary;
- manager-release completion before nudge;
- marker-absent admission into nudge;
- possible nudge-side-effect persistence;
- retained-DDz1/manager release bypass;
- unprotected propagation;
- nonmatching-type resume unwind.

## Explicit exclusions
R-149 does not:
- call DDz1;
- evaluate live DDz1 guards;
- acquire NSFileManager;
- probe the marker file;
- invoke `nudgePresent:`;
- mutate DDz1 state;
- mutate real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 36E00
Next earlier LSDA-bearing function:
- `36E00 -> LSDA 0x11409C`.
- Role: obtain `UIScreen.mainScreen.bounds`, choose a dimension-derived value, and return zero when the protected display query throws.

Exact table:
1. `0x36E18..0x36E2C -> 0x36E80`, action 5.
2. `0x36E2C..0x36E98` -> no landing.

Protected raw order:
- `+[UIScreen mainScreen]`;
- retain-autoreleased UIScreen;
- `mov x19,x0` at `0x36E24`;
- `bounds` at `0x36E28`.

The protected range ends before:
- `fmov d8,d2`;
- `fmov d9,d3`;
- normal UIScreen release.

Expected typed catch:
- begin/end-catch;
- branch to `0x36E60`;
- force `d0 = 0.0`;
- return zero.

Nonmatching type resumes unwind at `0x36E94`.

R-150 should split:
- main-screen acquisition before x19 commit;
- bounds send after x19 commit, where catch can bypass the normal UIScreen release.

No width/height result is committed before the protected range ends.

## Scout after R-150 — 369E8
Next earlier LSDA-bearing function:
- `369E8 -> LSDA 0x114058`.
- Role: classify layout area, build a status string, deduplicate/persist `headunit_layout_area`, and post a Darwin notification.

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

This function mixes typed catches, action-0 cleanup unwind, retained strings, global dedup state, preferences writes, and Darwin notification. It must be decoded as a separate multi-site batch rather than inferred from the simpler wrappers.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
