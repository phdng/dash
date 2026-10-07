# LOG/session-149.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-148 commit `8ce0957`; decode and promote exact data-only `371AC` DDz1 `dropOverdueNotice` catch-all exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `8ce0957`.
- Working tree clean.
- User confirmed session-148 macOS CI/compiler GREEN.
- Local tracking ref still reported ahead 4 at session start; assistant did not fetch/push.

## Target
- Function: `sub_371AC`.
- LSDA: `0x1140D8`.
- Role: obtain shared DDz1 and send `dropOverdueNotice`.

## Exact LSDA
Decoded table:
1. `0x371C0..0x371D4 -> 0x371E4`, action 1 catch-all.
2. `0x371D4..0x371F4` -> no landing.

The function prefix before `0x371C0` is unprotected.

## Raw ARM64
```
371C0  bl  +[DDz1 shared]
371C8  bl  objc_retainAutoreleasedReturnValue
371CC  mov x19,x0
371D0  bl  dropOverdueNotice

371D4  mov x0,x19
371D8  restore frame
371E0  b   objc_release

371E4  bl  objc_begin_catch
371E8  restore frame
371F0  b   objc_end_catch
```

There is no catch discriminator and no nonmatching-type path.

Any exception covered by `0x371C0..0x371D4`:
- is swallowed;
- skips normal retained-DDz1 release tail;
- returns immediately after `objc_end_catch`.

## Semantic site 1 — shared DDz1 acquisition
Before `mov x19,x0`:
- `+[DDz1 shared]`;
- retain-autoreleased result.

Catch-all behavior:
- immediate return;
- x19 not guaranteed committed;
- DDz1 acquisition/retain may already have started;
- temporary DDz1 cleanup can be bypassed.

No committed-controller release-bypass claim is made.

## Semantic site 2 — dropOverdueNotice selector send
At `0x371CC`, retained DDz1 is committed to x19.

The selector send at `0x371D0` therefore starts with committed retained DDz1.

If it throws:
- catch-all swallows it;
- normal release tail `0x371D4..0x371E0` is skipped;
- any selector side effect that happened before the throw is not rolled back locally;
- function returns immediately.

No retry or alternate selector exists locally.

## Unprotected paths
Exceptions outside `0x371C0..0x371D4` propagate:
- function prefix;
- normal release tail;
- catch body.

## Promoted runtime contract
Added:
- `DDDropOverdueNoticeExceptionSite`:
  - `SharedControllerAcquisition`;
  - `DropSelectorSend`;
  - `UnprotectedRange`.
- `DDDropOverdueNoticeExceptionOutcome`.
- `DDResolveDropOverdueNoticeExceptionOutcome(site)`.

Shared acquisition:
- swallow any covered exception;
- return immediately;
- temporary controller acquisition may have started;
- temporary controller cleanup may be bypassed.

Selector send:
- catch-all swallow + immediate return;
- retained controller definitely committed;
- retained-controller release may be bypassed;
- selector side effects may already have applied.

Unprotected:
- propagates.

There is intentionally no nonmatching-type field because LSDA action 1 is catch-all.

## Explicit exclusions
R-148 does not:
- call `+[DDz1 shared]`;
- invoke `dropOverdueNotice`;
- mutate DDz1 state;
- change real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 370F8
Next earlier LSDA-bearing function:
- `370F8 -> LSDA 0x1140B4`.
- Role: DDz1 visibility/live-present/file-marker gate before `nudgePresent:@"tick"`.

Exact table:
1. `0x37110..0x37158 -> 0x3718C`, action 5.
2. `0x37158..0x37168` -> no landing.
3. `0x37168..0x37178 -> 0x3718C`, action 5.
4. `0x37178..0x371AC` -> no landing.

Common catch at `0x3718C`:
- compare discriminator to expected type;
- expected: begin/end-catch and return;
- nonmatching: resume unwind at `0x371A8`.

### First protected range timing
Raw order:
- `0x37110`: `+[DDz1 shared]`;
- `0x37118`: retain-autoreleased DDz1;
- `0x3711C`: commit retained DDz1 to x19;
- `0x37120`: `visible`;
- `0x3712C`: `livePresentRunning`;
- `0x3713C`: `+[NSFileManager defaultManager]`;
- `0x37144`: retain-autoreleased manager;
- `0x37148`: commit manager to x20;
- `0x37154`: `fileExistsAtPath:`.

The range ends at `0x37158`, before `mov x21,x0` commits the file-exists result.

R-149 should split at least:
- DDz1 acquisition before x19 commit;
- `visible` and `livePresentRunning` after x19 commit;
- file-manager acquisition before x20 commit;
- file-exists send after x20 commit.

Expected catch from late sub-sites can bypass DDz1 release, and the file-exists subsite can additionally bypass manager release.

### Between ranges
`0x37158..0x37168` is unprotected:
- commit file-exists result to w21;
- release x20 manager;
- branch if marker exists.

Thus the second protected range has no live retained manager.

### Second protected range
`0x37168..0x37178` covers:
- load static `"tick"`;
- send `nudgePresent:` on retained DDz1 x19.

Expected exception:
- swallow and return;
- retained DDz1 release at `0x37178` is bypassed;
- any nudge side effect already applied before throw is not rolled back.

R-149 should encode precise guard-completion/result-availability and ownership timing without executing live DDz1/NSFileManager behavior.

## Scout after R-149 — 36E00
Next earlier LSDA-bearing function:
- `36E00 -> LSDA 0x11409C`.
- Role: read `UIScreen.mainScreen.bounds`, choose the smaller of bounds dimensions, then return half that dimension only when it lies within the observed numeric gate; otherwise return 0.

Exact table:
1. `0x36E18..0x36E2C -> 0x36E80`, action 5.
2. `0x36E2C..0x36E98` -> no landing.

Protected range covers:
- `+[UIScreen mainScreen]`;
- retain-autoreleased UIScreen;
- `bounds`.

Expected catch at `0x36E80`:
- typed begin/end-catch;
- branch to `0x36E60`;
- return 0.0.

Nonmatching type resumes unwind at `0x36E94`.

Important boundary:
- `fmov d8,d2` / `fmov d9,d3` happen at/after `0x36E2C`, outside protection;
- expected catch therefore does not rely on committed bounds dimensions and forces zero directly.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
