# LOG/session-147.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-146 commit `41c0195`; decode and promote exact data-only `37284` DDz1 `dropSplashIfOverdue` catch-all exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `41c0195`.
- Working tree clean.
- User confirmed session-146 macOS CI/compiler GREEN.
- Local tracking ref still reported ahead 2 at session start; assistant did not fetch/push.

## Target
- Function: `sub_37284`.
- LSDA: `0x114100`.
- Role: obtain shared DDz1 and send `dropSplashIfOverdue`.

## Exact LSDA
Raw bytes at `0x114100`:
```
FF 9B 11 01 08
14 14 38 01
28 20 00 00
...
```

Decoded call-site table:
1. `0x37298..0x372AC -> 0x372BC`, action 1.
2. `0x372AC..0x372CC` -> no landing.

The function prefix `0x37284..0x37298` is also outside the protected range.

Action 1 is catch-all.

## Raw ARM64
Relevant flow:
```
37298  bl  +[DDz1 shared]
372A0  bl  objc_retainAutoreleasedReturnValue
372A4  mov x19,x0
372A8  bl  dropSplashIfOverdue

372AC  mov x0,x19
372B0  restore frame
372B8  b   objc_release

372BC  bl  objc_begin_catch
372C0  restore frame
372C8  b   objc_end_catch
```

There is no discriminator test and no nonmatching-type branch.

Any exception covered by `0x37298..0x372AC`:
- is swallowed;
- skips the normal retained-DDz1 release tail;
- returns immediately after `objc_end_catch`.

## Semantic site 1 — shared DDz1 acquisition
Protected operations before `mov x19,x0`:
- `+[DDz1 shared]`;
- retain-autoreleased result.

If an exception occurs here:
- catch-all swallows it;
- function returns immediately;
- x19 is not guaranteed committed;
- DDz1 acquisition/retain work may already have started;
- temporary DDz1 cleanup may be bypassed.

No committed-controller release-bypass claim is made.

## Semantic site 2 — dropSplashIfOverdue send
At `0x372A4`, retained DDz1 is committed to x19.

The selector send at `0x372A8` is therefore entered with retained DDz1 definitely committed.

If it throws:
- catch-all swallows it;
- normal release tail `0x372AC..0x372B8` is skipped;
- any selector side effect already applied before exception is not rolled back;
- function returns immediately.

No retry, alternate selector, or compensating action exists locally.

## Unprotected paths
No landing covers:
- prologue/prefix before `0x37298`;
- normal release tail after `0x372AC`;
- catch body itself.

Exceptions there propagate normally.

## Promoted runtime contract
Added:
- `DDDropSplashIfOverdueExceptionSite`:
  - `SharedControllerAcquisition`;
  - `DropSelectorSend`;
  - `UnprotectedRange`.
- `DDDropSplashIfOverdueExceptionOutcome`.
- `DDResolveDropSplashIfOverdueExceptionOutcome(site)`.

Shared acquisition:
- swallow any covered exception;
- return immediately;
- temporary controller acquisition may have started;
- temporary controller cleanup may be bypassed.

Selector send:
- swallow any covered exception;
- return immediately;
- retained controller definitely committed;
- retained-controller release may be bypassed;
- selector side effects may already have applied.

Unprotected:
- propagates.

There is intentionally no nonmatching-type field because action 1 has no type discriminator.

## Explicit exclusions
R-146 does not:
- call `+[DDz1 shared]`;
- invoke `dropSplashIfOverdue`;
- mutate DDz1 state;
- alter real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 371F4
Next earlier LSDA-bearing function:
- `371F4 -> LSDA 0x1140EC`.
- Role: DDz1 `dropServerNoticeNow` wrapper.

Raw LSDA has the same action-1 layout.

Exact table:
1. `0x37208..0x3721C -> 0x3722C`, action 1 catch-all.
2. `0x3721C..0x3723C` -> no landing.

Protected raw order:
- `+[DDz1 shared]`;
- retain-autoreleased result;
- x19 commit at `0x37214`;
- `dropServerNoticeNow` send at `0x37218`.

Landing `0x3722C` unconditionally begin/end-catches and returns.

R-147 should mirror the exact pre/post-x19 split from R-146, but keep selector-specific metadata separate:
- acquisition exception before x19 commit;
- selector-send exception with retained x19 committed;
- catch skips normal release tail;
- any selector side effect before throw can persist.

## Scout after R-147
R-148:
- `371AC -> LSDA 0x1140D8`;
- same action-1 catch-all shape around `dropOverdueNotice`;
- protected `0x371C0..0x371D4 -> 0x371E4`;
- x19 commit at `0x371CC`;
- selector send at `0x371D0`.

After that:
- `370F8 -> LSDA 0x1140B4`;
- more complex DDz1 visible/livePresent/file-marker/nudge wrapper;
- must be decoded separately rather than treated as the same simple catch-all.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
