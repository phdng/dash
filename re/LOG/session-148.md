# LOG/session-148.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-147 commit `bd54b46`; decode and promote exact data-only `371F4` DDz1 `dropServerNoticeNow` catch-all exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `bd54b46`.
- Working tree clean.
- User confirmed session-147 macOS CI/compiler GREEN.
- Local tracking ref still reported ahead 3 at session start; assistant did not fetch/push.

## Target
- Function: `sub_371F4`.
- LSDA: `0x1140EC`.
- Role: obtain shared DDz1 and send `dropServerNoticeNow`.

## Exact LSDA
Decoded table:
1. `0x37208..0x3721C -> 0x3722C`, action 1 catch-all.
2. `0x3721C..0x3723C` -> no landing.

The function prefix before `0x37208` is unprotected.

## Raw ARM64
```
37208  bl  +[DDz1 shared]
37210  bl  objc_retainAutoreleasedReturnValue
37214  mov x19,x0
37218  bl  dropServerNoticeNow

3721C  mov x0,x19
37220  restore frame
37228  b   objc_release

3722C  bl  objc_begin_catch
37230  restore frame
37238  b   objc_end_catch
```

There is no catch discriminator and no nonmatching-type path.

Any exception covered by `0x37208..0x3721C`:
- is swallowed;
- skips normal retained-DDz1 release tail;
- returns immediately after `objc_end_catch`.

## Semantic site 1 — shared DDz1 acquisition
Before `mov x19,x0`:
- `+[DDz1 shared]`;
- retain-autoreleased result.

Expected catch-all behavior:
- immediate return;
- x19 not guaranteed committed;
- DDz1 acquisition/retain may already have started;
- temporary DDz1 cleanup can be bypassed.

No committed-controller release-bypass claim is made.

## Semantic site 2 — dropServerNoticeNow selector send
At `0x37214`, retained DDz1 is committed to x19.

The selector send at `0x37218` therefore begins with committed retained DDz1.

If it throws:
- catch-all swallows it;
- normal x19 release `0x3721C..0x37228` is skipped;
- any selector side effect that occurred before throw is not rolled back locally;
- function returns immediately.

No retry or alternate selector exists locally.

## Unprotected paths
Exceptions outside `0x37208..0x3721C` propagate:
- function prefix;
- normal release tail;
- catch body.

## Promoted runtime contract
Added:
- `DDDropServerNoticeNowExceptionSite`:
  - `SharedControllerAcquisition`;
  - `DropSelectorSend`;
  - `UnprotectedRange`.
- `DDDropServerNoticeNowExceptionOutcome`.
- `DDResolveDropServerNoticeNowExceptionOutcome(site)`.

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
R-147 does not:
- call `+[DDz1 shared]`;
- invoke `dropServerNoticeNow`;
- mutate DDz1 state;
- change real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 371AC
Next earlier LSDA-bearing function:
- `371AC -> LSDA 0x1140D8`.
- Role: DDz1 `dropOverdueNotice` wrapper.

Exact table:
1. `0x371C0..0x371D4 -> 0x371E4`, action 1 catch-all.
2. `0x371D4..0x371F4` -> no landing.

Raw ordering:
- `+[DDz1 shared]`;
- retain-autoreleased DDz1;
- x19 commit at `0x371CC`;
- `dropOverdueNotice` send at `0x371D0`;
- normal release tail `0x371D4..0x371E0`;
- catch-all landing `0x371E4`.

R-148 should mirror the pre/post-x19 split from R-146/R-147, while keeping selector-specific metadata.

## Scout after R-148 — 370F8
Next earlier LSDA-bearing function:
- `370F8 -> LSDA 0x1140B4`.
- Role: DDz1 visible/live-present guard + file marker + `nudgePresent:`.

Exact table:
1. `0x37110..0x37158 -> 0x3718C`, action 5.
2. `0x37158..0x37168` -> no landing.
3. `0x37168..0x37178 -> 0x3718C`, action 5.
4. `0x37178..0x371AC` -> no landing.

Common catch:
- typed discriminator at `0x3718C`;
- expected type begin/end-catches and returns;
- nonmatching type resumes unwind at `0x371A8`.

The first protected range spans:
- DDz1 shared + retain + x19 commit;
- `visible`;
- `livePresentRunning`;
- NSFileManager `defaultManager` + retain + x20 commit;
- `fileExistsAtPath:`.

The second protected range covers:
- `nudgePresent:`.

R-149 must map sub-sites separately for:
- pre/post x19 DDz1 ownership;
- pre/post x20 file-manager ownership;
- which guards completed;
- marker result availability;
- nudge side effects before throw;
- cleanup bypass on common typed catch.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
