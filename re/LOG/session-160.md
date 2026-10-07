# LOG/session-160.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-159 commit `65a413d`; decode and promote exact data-only `35880` splash-opacity CATransaction catch-all behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `65a413d`.
- Working tree clean and synchronized with origin.
- User confirmed session-159 macOS CI/compiler GREEN.

## Target
- Function: `sub_35880`.
- LSDA: `0x113EC8`.
- Role: read captured layer opacity and, when it equals 0.99, run a no-animation CATransaction that forces opacity to 1.0.

## Exact LSDA
1. `0x35894..0x358D4 -> 0x358E0`, action 1 catch-all.
2. `0x358D4..0x358F0` -> no landing.

Prefix `0x35880..0x35894` is unprotected.

## Raw ARM64
```
35890  load captured layer
35894  opacity
35898  load 0.99 constant
358A0  compare opacity
358A4  branch if not equal -> 358D4

358B0  CATransaction begin
358BC  CATransaction setDisableActions:YES
358C8  layer setOpacity:1.0
358D0  CATransaction commit

358D4  epilogue/return

358E0  objc_begin_catch
358E4  restore frame
358EC  tail objc_end_catch
```

Landing has no discriminator and no alternate continuation.

## Catch behavior
Any exception escaping the protected path:
- is swallowed;
- returns immediately;
- does not retry;
- does not restore the prior opacity;
- does not issue a compensating CATransaction commit or rollback.

The catch therefore preserves any transaction/layer side effects that completed before the throw.

## Semantic site 1 — opacity read
At `opacity`:
- no CATransaction call has started.

If the getter throws:
- catch swallows and returns;
- no transaction side effect is asserted.

The comparison against 0.99 is not itself a throwing call.

## Semantic site 2 — transaction begin
This site is reached only after opacity read returned and matched 0.99.

If `+[CATransaction begin]` throws:
- opacity match definitely passed;
- transaction begin may already have started/applied before the exception;
- catch returns;
- no later local disable-actions, opacity mutation or commit runs.

R-159 records possible begin side effect, not guaranteed open transaction state.

## Semantic site 3 — disable actions
Reached only after `begin` returned normally.

If `setDisableActions:YES` throws:
- transaction begin definitely completed;
- disable-actions may already have applied;
- local opacity mutation and commit are skipped by catch.

No local compensation occurs.

## Semantic site 4 — opacity mutation
Reached only after:
- begin completed;
- disable-actions completed.

If `setOpacity:1.0` throws:
- transaction setup is already complete;
- opacity mutation may already have partially/fully applied;
- local commit is skipped.

Catch performs no opacity restore.

## Semantic site 5 — transaction commit
Reached only after:
- begin completed;
- disable-actions completed;
- opacity mutation returned successfully.

If `commit` throws:
- opacity mutation definitely completed first;
- commit itself may already have partially applied;
- catch returns immediately.

No second commit/rollback is attempted.

## Unprotected tail
`0x358D4..0x358F0` contains epilogue plus catch landing code outside local protected call-site coverage.

Any exception outside the action-1 range propagates according to normal runtime behavior.

## Promoted runtime contract
Added:
- `DDSplashOpacityTransactionExceptionSite`:
  - `OpacityRead`;
  - `TransactionBegin`;
  - `DisableActions`;
  - `OpacityMutation`;
  - `TransactionCommit`;
  - `UnprotectedRange`.
- `DDSplashOpacityTransactionExceptionOutcome`.
- `DDResolveSplashOpacityTransactionExceptionOutcome(site)`.

Metadata captures:
- catch-all swallow + immediate return;
- opacity admission completion;
- transaction begin possible/definite timing;
- disable-actions possible/definite timing;
- opacity mutation possible/definite timing;
- commit possible timing;
- skipped local transaction completion after catch;
- unprotected propagation.

## Explicit exclusions
R-159 does not:
- call live CALayer opacity APIs;
- invoke CATransaction;
- mutate real opacity/transaction state;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 356A0
Next earlier LSDA-bearing function:
- `356A0 -> LSDA 0x113E98`.
- Role: weak-owner/target/layer admission, opacity + opacity-animation probe, CATransaction opacity adjustment, counter decrement, retained layer capture and delayed call into `sub_35880`.

Exact 6-entry table:
1. `0x356A0..0x356DC` -> no landing.
2. `0x356DC..0x356F8 -> 0x35858`, action 5.
3. `0x356FC..0x3573C -> 0x35854`, action 5.
4. `0x3573C..0x35750` -> no landing.
5. `0x35750..0x35778 -> 0x35854`, action 5.
6. `0x35778..0x35880` -> no landing.

Action 5 chain:
- expected typed filter 1;
- cleanup action 0 for nonmatching unwind.

Landing topology:
- `0x35854 -> 0x35858`;
- `0x35858` checks type 1;
- expected type begin/end-catches and returns immediately;
- nonmatching type resumes unwind at `0x3587C`.

R-160 must map the three protected ranges separately:

### Range 1 — target admission
`0x356DC..0x356F8` covers:
- retained target hidden check;
- owner livePresentRunning check.

Weak owner and retained target were acquired in the unprotected prefix.

A caught exception returns immediately and bypasses later target/owner cleanup.

### Range 2 — layer/opacity/animation probe
`0x356FC..0x3573C` covers:
- layer acquisition + retain;
- layer opacity read;
- animationForKey:@"opacity" acquisition/retain.

Catch occurs before the unprotected release/branch bridge at `0x3573C..0x35750`.

Map pre/post layer commit and temporary animation-object release bypass exactly.

### Range 3 — CATransaction mutation
`0x35750..0x35778` covers:
- CATransaction begin;
- setDisableActions:YES;
- layer setOpacity to 0.99;
- CATransaction commit.

Expected catch returns immediately, so later counter decrement and delayed dispatch are skipped.

The counter/deferred-dispatch tail `0x35778..0x35880` is unprotected:
- reason string selects counter;
- counter decrements when positive;
- dispatch_time(50ms);
- layer retained into block;
- dispatch_after to `sub_35880`;
- capture/layer/target/owner releases.

Exceptions there propagate and may preserve prior counter/dispatch side effects.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
