# LOG/session-162.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-161 commit `899e242`; decode and promote exact data-only `35328` `-[CNABLivePresenter restoreTargets]` typed/action-0 exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `899e242`.
- Working tree clean and synchronized with origin.
- User confirmed session-161 macOS CI/compiler GREEN.

## Target
- Function: `-[CNABLivePresenter restoreTargets]`.
- Address: `0x35328`.
- LSDA: `0x113E30`.
- Role: probe targets, start a no-animation CATransaction, obtain/enumerate target layers, restore eligible CALayer opacity to 1.0, then commit.

## Exact LSDA call-site table
1. `0x35360..0x3536C -> 0x35520`, action 5.
2. `0x3536C..0x35380` -> no landing.
3. `0x35380..0x35390 -> 0x35520`, action 5.
4. `0x3539C..0x353C0 -> 0x3551C`, action 5.
5. `0x353C0..0x353CC` -> no landing.
6. `0x353CC..0x353E0 -> 0x3551C`, action 5.
7. `0x3541C..0x35440 -> 0x35534`, action 5.
8. `0x35440..0x35450` -> no landing.
9. `0x35450..0x35480 -> 0x35530`, action 5.
10. `0x35488..0x3548C -> 0x3552C`, action 0.
11. `0x35490..0x3549C -> 0x35530`, action 5.
12. `0x3549C..0x354A4 -> 0x3552C`, action 0.
13. `0x354B0..0x354C4 -> 0x35528`, action 5.
14. `0x354CC..0x354D4 -> 0x3552C`, action 0.
15. `0x354D8..0x354DC -> 0x35520`, action 5.
16. `0x354DC..0x35548` -> no landing.

Action 5 chain:
- typed filter 1;
- cleanup action 0.

## Typed landing topology
Aliases:
- `0x3551C`;
- `0x35520`;
- `0x35528`;
- `0x35530`;
- `0x35534`.

They converge at:
```
35534 cmp w1,#1
35538 b.ne 3552C
3553C objc_begin_catch
35540 objc_end_catch
35544 b 354DC
```

Expected type:
- is swallowed;
- jumps to epilogue `0x354DC`;
- does **not** resume the normal cleanup/commit sequence from the failing site.

Nonmatching type:
- resumes unwind at `0x3552C`.

## Action-0 landing
`0x3552C` directly resumes unwind.

Therefore release failures in action-0 ranges are not swallowed.

## Semantic site — initial targets probe
Typed `0x35360..0x3536C`:
- `-[CNABLivePresenter targets]`;
- retain-autoreleased result.

The range ends before:
```
3536C mov x20,x0
35370 objc_release(x20)
35374 cbz x20,354DC
```

Expected catch:
- returns via epilogue;
- CATransaction has not started;
- temporary targets acquisition/retain may already have started;
- temporary release can be bypassed.

## Unprotected initial probe bridge
`0x3536C..0x35380`:
- commits probe result to x20;
- releases it;
- tests whether targets exist.

If no targets:
- function jumps directly to epilogue;
- no transaction begins.

## Semantic sites — CATransaction begin / disable actions
Typed `0x35380..0x35390`:
```
35380 CATransaction begin
3538C setDisableActions:YES
```

### begin
If begin throws:
- begin may already have changed transaction state;
- expected catch jumps to epilogue;
- normal final commit is skipped.

### disable actions
Reached only after begin completed.

If disable-actions throws:
- transaction begin definitely completed;
- disable-actions may already have applied;
- expected catch jumps to epilogue;
- final commit is skipped.

No compensating commit/rollback exists.

## Semantic sites — enumeration source / collection acquisition
Typed `0x3539C..0x353C0`.

Sequence:
```
353A0 targets
353A8 retain-autoreleased
353AC mov x20,x0              ; enumeration source/provider committed
353B0 load callable
353B4 invoke callable
353BC retain-autoreleased result
```

The range ends before:
```
353C0 mov x19,x0              ; returned collection committed
```

### enumeration source acquisition
If targets getter/retain throws before x20 commit:
- temporary source acquisition may have started;
- transaction begin+disable have completed;
- expected catch skips final commit.

### returned collection acquisition
At callable invocation:
- retained enumeration source x20 is committed.

If callable/result retain throws:
- source release at `0x353C8` can be bypassed;
- returned collection acquisition may have started;
- x19 collection is not yet committed;
- expected catch skips final commit.

## Unprotected collection commit bridge
`0x353C0..0x353CC`:
- commits returned collection to x19;
- releases source/provider x20.

Release exceptions here are unprotected and propagate.

## Semantic site — initial enumeration read
Typed `0x353CC..0x353E0`:
- `countByEnumeratingWithState:objects:count:`.

At entry:
- CATransaction begin completed;
- disable-actions completed;
- collection x19 committed.

Expected catch:
- returns via epilogue;
- collection release at `0x354D0` is bypassed;
- final CATransaction commit is skipped.

## Enumeration loop state
After initial enumeration returns nonzero:
- enumeration mutation marker is saved;
- layer class reference and opacity constants are prepared.

## Semantic site — enumeration mutation / type filter
Typed `0x3541C..0x35440` covers:
- conditional `objc_enumerationMutation`;
- CALayer class lookup;
- `objc_opt_isKindOfClass`.

At entry:
- collection x19 committed;
- enumeration has started;
- transaction is active.

Expected catch:
- skips remaining iteration;
- bypasses collection release;
- skips final commit.

No retained per-layer object exists yet.

## Unprotected per-layer retain bridge
`0x35440..0x35450`:
- branches around non-CALayer items;
- retains matching item;
- commits retained layer to x22.

Retain failure here is unprotected and propagates.

## Semantic group — retained-layer opacity / animation probe
Typed `0x35450..0x35480`.

At entry:
- collection x19 committed;
- retained layer x22 committed;
- enumeration active.

Protected sequence:
```
35450 opacity
35454 compare > 0.9
35460 opacity
35464 compare < 1.0
35474 animationForKey:@"opacity"
3547C retain-autoreleased
```

### first opacity read
Expected catch:
- bypasses x22 layer release and x19 collection release;
- skips final commit.

### second opacity read
Reached only after first opacity > 0.9.

Expected catch:
- first opacity read definitely completed;
- same release/commit bypass applies.

### opacity animation lookup
Reached only after:
- first opacity > 0.9;
- second opacity < 1.0.

The retained animation result is still temporary because the range ends before null-test/result handling.

Expected catch:
- temporary animation acquisition/release may be bypassed;
- retained layer/collection releases are bypassed;
- final commit skipped.

## Action-0 — animation-result release
`0x35488..0x3548C` is action 0:
- releases the retained animation lookup result.

If this release throws:
- exception resumes unwind;
- retained layer x22 release can be bypassed;
- collection x19 release can be bypassed;
- final transaction commit is skipped.

This path is not swallowed.

## Semantic site — layer opacity mutation
Typed `0x35490..0x3549C`:
- `setOpacity:1.0`.

Reached only when opacity animation lookup result was nil.

If it throws:
- opacity mutation may already have applied;
- expected catch returns via epilogue;
- retained layer/collection releases are bypassed;
- final commit is skipped.

No rollback of opacity exists.

## Action-0 — retained-layer release
`0x3549C..0x354A4`:
- normal release of x22.

If release throws:
- resume unwind;
- remaining collection release can be bypassed;
- final transaction commit is skipped.

## Semantic site — enumeration advance
Typed `0x354B0..0x354C4`:
- next `countByEnumeratingWithState:objects:count:`.

At entry:
- collection x19 remains committed;
- per-layer local has already been released on normal path.

Expected catch:
- bypasses final collection release;
- skips final transaction commit.

## Action-0 — collection release
`0x354CC..0x354D4`:
- normal release of x19.

If it throws:
- resume unwind;
- final CATransaction commit at `0x354D8` is skipped.

## Semantic site — final CATransaction commit
Typed `0x354D8..0x354DC`:
- `+[CATransaction commit]`.

Reached after collection release completed normally.

If commit throws:
- commit may already have partially applied;
- expected catch swallows;
- jumps to epilogue;
- no retry or compensating transaction action occurs.

## Final epilogue
`0x354DC..`:
- stack-canary validation;
- register/frame restore;
- return.

Expected typed catches jump here directly.

## Promoted runtime contract
Added:
- `DDRestoreTargetsExceptionSite`;
- `DDRestoreTargetsExceptionOutcome`;
- `DDResolveRestoreTargetsExceptionOutcome(site)`.

Semantic sites expose:
- initial targets probe;
- transaction begin;
- disable actions;
- enumeration source acquisition;
- returned collection acquisition;
- initial enumeration read;
- mutation/type filtering;
- first/second opacity reads;
- opacity animation lookup;
- opacity mutation;
- enumeration advance;
- final transaction commit;
- three action-0 release stages;
- generic unprotected range.

Metadata records:
- expected typed swallow/epilogue routing;
- transaction begin/disable timing;
- skipped final commit;
- temporary-vs-committed source/collection/layer/animation ownership;
- layer/collection release bypass;
- opacity mutation persistence;
- action-0 resume unwind;
- nonmatching typed unwind;
- propagation.

## Explicit exclusions
R-161 does not:
- query live targets;
- enumerate real collections;
- mutate live CALayers;
- start/commit real CATransactions;
- retain/release real objects;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 34F28
Next earlier LSDA-bearing function:
- `34F28 -> LSDA 0x113D8C`.
- Method: `-[CNABLivePresenter tick:]`.

Exact LSDA call-site table has 26 entries.

Protected typed ranges use action 5:
- typed filter 1;
- cleanup action 0.

Action-0 ranges are also interleaved for local release/cleanup failures.

Landing aliases:
- `0x352F4`;
- `0x352F8`;
- `0x352FC`;
- `0x35300`;
- `0x35304`;
- `0x35308`;
- `0x35310`;
- `0x35314`.

They converge at:
```
35314 cmp w1,#1
35318 b.ne 3530C
3531C objc_begin_catch
35320 objc_end_catch
35324 b 352A8
```

Expected typed catch:
- is swallowed;
- jumps to final retained-input cleanup at `0x352A8`;
- does not simply return from landing.

Action-0/nonmatching:
- resume unwind at `0x3530C`.

The method is a large state machine covering:
- retained timer/input;
- window/layer admission;
- hidden/noop/opacity-animation gates;
- targets-vs-alt fallback collection selection;
- phase toggle and target opacity selection;
- CATransaction begin/disable;
- fast enumeration;
- per-layer animation/opacity/group-opacity checks;
- `setAllowsGroupOpacity:` and `setOpacity:` mutations;
- collection/layer/local cleanup;
- final CATransaction commit;
- tick increment;
- retained window/input cleanup.

R-162 should decode all 26 ranges site-by-site, preserving which retained locals still receive final cleanup at `0x352A8` versus which intermediate releases are bypassed.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
