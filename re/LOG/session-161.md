# LOG/session-161.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-160 commit `07e9ad4`; decode and promote exact data-only `356A0` splash-nudge preparation typed exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `07e9ad4`.
- Working tree clean.
- User confirmed session-160 macOS CI/compiler GREEN.
- Local tracking still reported ahead 1; assistant did not fetch/push.

## Target
- Function: `sub_356A0`.
- LSDA: `0x113E98`.
- Role: weak-owner/target admission, layer opacity + opacity-animation probing, optional CATransaction mutation to opacity 0.99, counter decrement, then a 50ms delayed call into `sub_35880`.

## Exact LSDA call-site table
1. `0x356A0..0x356DC` -> no landing.
2. `0x356DC..0x356F8 -> 0x35858`, action 5.
3. `0x356FC..0x3573C -> 0x35854`, action 5.
4. `0x3573C..0x35750` -> no landing.
5. `0x35750..0x35778 -> 0x35854`, action 5.
6. `0x35778..0x35880` -> no landing.

`0x35854` aliases common typed landing `0x35858`.

Expected type:
- begin catch;
- restore frame;
- end catch;
- return immediately.

Nonmatching type:
- resumes unwind at `0x3587C`.

Action 5 includes typed filter plus cleanup semantics for nonmatching unwind.

## Unprotected prefix ownership
```
356BC objc_loadWeakRetained(owner weak)
356C4 mov x19,x0
356C8 cbz x0,35828

356CC load owner->target
356D0 objc_retain
356D4 mov x20,x0
356D8 cbz x0,3582C
```

Therefore every protected range begins with:
- weak-retained owner x19 committed;
- retained target x20 committed.

Expected catches return before normal releases:
```
3582C objc_release(x20)
35834 objc_release(x19)
```

So both normal releases can be bypassed.

## Typed range 1 — admission
`0x356DC..0x356F8`.

Protected call sites:
- target `isHidden`;
- owner `livePresentRunning`.

Between them:
- owner byte at offset `0x58` must be set.

### Hidden check
At `isHidden`:
- owner x19 committed;
- target x20 committed.

Expected catch:
- return immediately;
- x20/x19 normal releases bypassed.

### livePresentRunning
Reached only after:
- hidden returned false;
- owner presentation byte was enabled.

If `livePresentRunning` throws:
- expected catch returns immediately;
- owner/target releases are bypassed.

No layer acquisition has begun yet.

## Typed range 2 — layer / opacity / opacity-animation probe
`0x356FC..0x3573C`.

Admission already passed:
- hidden=false;
- presentation byte enabled;
- livePresentRunning=false.

Protected sequence:
```
356FC layer
35708 retain-autoreleased
3570C mov x21,x0          ; retained layer committed

35710 opacity
3571C compare with threshold
35720 branch if opacity < threshold

35730 animationForKey:@"opacity"
35738 retain-autoreleased
```

The range ends exactly before:
```
3573C mov x23,x0
```

### Layer acquisition
A throw during `layer` or its retain can occur before x21 commit.

Metadata therefore records:
- temporary layer acquisition may have started;
- temporary layer cleanup can be bypassed;
- owner/target are definitely committed.

### Layer opacity
At `opacity`:
- retained layer x21 is definitely committed.

Expected catch:
- return immediately;
- normal x21 release at `0x35820` is bypassed;
- owner/target releases are also bypassed.

### opacity animation lookup
`animationForKey:@"opacity"` is reached only when opacity is at least the threshold (~0.999).

Its retained result is still temporary when the protected range ends, because x23 commit is outside protection.

Thus a caught animation lookup/retain exception records:
- threshold already passed;
- x21 layer committed;
- temporary animation acquisition may have started;
- temporary animation release may be bypassed;
- no committed x23 animation local is asserted.

## Unprotected animation-result bridge
`0x3573C..0x35750`:
```
3573C mov x23,x0
35740 objc_release(x23)
35744 cbnz x23,3581C
```

This bridge:
- commits x23;
- performs its normal release;
- skips CATransaction work if animation exists.

It is unprotected.

Only a nil animation result reaches range 3.

## Typed range 3 — CATransaction opacity mutation
`0x35750..0x35778`.

Admission:
- hidden=false;
- owner presentation gate enabled;
- livePresentRunning=false;
- retained layer x21 committed;
- opacity threshold passed;
- opacity animation absent.

Protected sequence:
```
35750 CATransaction begin
3575C setDisableActions:YES
3576C layer setOpacity:0.99
35774 CATransaction commit
```

### begin
If begin throws:
- transaction begin may already have applied;
- expected catch returns;
- x21/x20/x19 releases are bypassed.

### disable actions
Reached only after begin completed.

If disable throws:
- begin definitely completed;
- disable-actions may already have applied;
- expected catch returns without setOpacity/commit.

### opacity mutation
Reached only after begin + disable completed.

If setOpacity:0.99 throws:
- transaction configuration is already established;
- opacity mutation may already have partially/fully applied;
- expected catch returns without local commit/rollback.

### commit
Reached only after opacity mutation returned successfully.

If commit throws:
- opacity mutation definitely completed;
- commit may already have partially applied;
- expected catch returns.

No compensating transaction action is executed locally.

## Unprotected counter / deferred-dispatch tail
`0x35778..0x35880` is unprotected.

It performs:
- reason-string selection of one of two counters;
- decrement when selected counter is positive;
- `dispatch_time(..., 50ms)`;
- block construction targeting `sub_35880`;
- retain layer x21 into block capture;
- `dispatch_after` on main queue;
- captured-layer release;
- layer x21 release;
- target x20 release;
- owner x19 release.

This tail is reachable only after CATransaction commit completed normally.

If an exception propagates from this unprotected tail:
- transaction commit is already complete;
- counter may already have decremented;
- retained layer block capture may already exist;
- delayed dispatch may already have been scheduled.

R-160 records these as possible side-effect milestones, not local catch behavior.

## Promoted runtime contract
Added:
- `DDSplashNudgePreparationExceptionSite` with sites for:
  - target hidden check;
  - livePresentRunning check;
  - layer acquisition;
  - layer opacity read;
  - opacity animation lookup;
  - CATransaction begin;
  - disable actions;
  - opacity mutation;
  - transaction commit;
  - unprotected post-transaction counter/dispatch tail;
  - generic unprotected range.
- `DDSplashNudgePreparationExceptionOutcome`.
- `DDResolveSplashNudgePreparationExceptionOutcome(site)`.

Metadata records:
- expected typed swallow + immediate return;
- owner/target commit and release-bypass;
- hidden/presentation/live-present admission;
- temporary-vs-committed layer ownership;
- threshold admission;
- temporary animation-result ownership;
- nil-animation admission;
- ordered CATransaction side effects;
- completed transaction before unprotected tail;
- possible counter/capture/dispatch milestones;
- nonmatching unwind;
- unprotected propagation.

## Explicit exclusions
R-160 does not:
- load/mutate a real weak owner;
- query/mutate a real layer;
- invoke CATransaction;
- mutate counters;
- schedule dispatch;
- retain/release live objects;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 35328
Next earlier LSDA-bearing function:
- `35328 -> LSDA 0x113E30`.
- Method: `-[CNABLivePresenter restoreTargets]`.

Exact LSDA call-site table has 16 entries:
1. `0x35360..0x3536C -> 0x35520`, action 5.
2. `0x3536C..0x35380` no landing.
3. `0x35380..0x35390 -> 0x35520`, action 5.
4. `0x3539C..0x353C0 -> 0x3551C`, action 5.
5. `0x353C0..0x353CC` no landing.
6. `0x353CC..0x353E0 -> 0x3551C`, action 5.
7. `0x3541C..0x35440 -> 0x35534`, action 5.
8. `0x35440..0x35450` no landing.
9. `0x35450..0x35480 -> 0x35530`, action 5.
10. `0x35488..0x3548C -> 0x3552C`, action 0.
11. `0x35490..0x3549C -> 0x35530`, action 5.
12. `0x3549C..0x354A4 -> 0x3552C`, action 0.
13. `0x354B0..0x354C4 -> 0x35528`, action 5.
14. `0x354CC..0x354D4 -> 0x3552C`, action 0.
15. `0x354D8..0x354DC -> 0x35520`, action 5.
16. `0x354DC..0x35548` no landing.

Landing topology:
- aliases `0x3551C/20/28/30/34` converge on common typed discriminator at `0x35534`;
- expected type begin/end-catches then branches to epilogue `0x354DC`;
- nonmatching and action-0 cleanup paths resume unwind through `0x3552C`.

Important continuation:
- normal path calls `+[CATransaction commit]` at `0x354D4..0x354D8`;
- expected typed catch branches to `0x354DC`, **skipping that final commit**.

R-161 should map:
- initial `targets` lookup;
- CATransaction begin + disable-actions;
- retained target collection / enumeration setup;
- fast-enumeration mutation handling;
- CALayer type filtering;
- retained per-layer lifetime;
- first/second opacity reads;
- opacity-animation lookup;
- possible `setOpacity:1.0` side effects;
- enumeration continuation;
- local releases;
- typed catches that leave transaction begun but skip final commit;
- action-0/nonmatching unwind cleanup.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
