# LOG/session-163.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-162 commit `783c8ae`; decode and promote exact data-only `34F28` `-[CNABLivePresenter tick:]` typed/action-0 exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `783c8ae`.
- Working tree clean.
- User confirmed session-162 macOS CI/compiler GREEN.
- Local tracking still reported ahead 1; assistant did not fetch/push.

## Target
- Method: `-[CNABLivePresenter tick:]`.
- Address: `0x34F28`.
- LSDA: `0x113D8C`.
- Role: retain timer/input, acquire live-presenter window/layer, run noop/hidden/animation/targets admission, derive target collection and phase opacity, mutate eligible layers in a CATransaction, increment ticks, then release retained locals.

## Exact LSDA call-site table
1. `0x34F28..0x34F70` unprotected.
2. `0x34F70..0x34FBC -> 0x35308`, action 5.
3. `0x34FBC..0x34FC8` unprotected.
4. `0x34FC8..0x35000 -> 0x35304`, action 5.
5. `0x35000..0x3500C` unprotected.
6. `0x3500C..0x3501C -> 0x352FC`, action 5.
7. `0x3501C..0x35028` unprotected.
8. `0x35028..0x3504C -> 0x352FC`, action 5.
9. `0x3504C..0x3505C` unprotected.
10. `0x3505C..0x350D4 -> 0x352FC`, action 5.
11. `0x350D4..0x35108 -> 0x352F8`, action 5.
12. `0x35108..0x35120` unprotected.
13. `0x35120..0x35130 -> 0x352F4`, action 5.
14. `0x35168..0x3518C -> 0x35314`, action 5.
15. `0x3518C..0x3519C` unprotected.
16. `0x3519C..0x351AC -> 0x35310`, action 5.
17. `0x351B0..0x351B4 -> 0x3530C`, action 0.
18. `0x351B8..0x35204 -> 0x35310`, action 5.
19. `0x35204..0x35210 -> 0x3530C`, action 0.
20. `0x35218..0x35238 -> 0x35310`, action 5.
21. `0x35238..0x35240 -> 0x3530C`, action 0.
22. `0x3524C..0x35260 -> 0x35300`, action 5.
23. `0x35268..0x35270 -> 0x3530C`, action 0.
24. `0x35278..0x35290 -> 0x352F8`, action 5.
25. `0x35290..0x352B0 -> 0x3530C`, action 0.
26. `0x352B0..0x35328` unprotected.

Action 5 chain:
- expected typed filter 1;
- cleanup action 0 for nonmatching unwind.

## Typed landing topology
Aliases `0x352F4/2F8/2FC/300/304/308/310/314` converge at:
```
35314 cmp w1,#1
35318 b.ne 3530C
3531C objc_begin_catch
35320 objc_end_catch
35324 b 352A8
```

Expected type:
- is swallowed;
- jumps to `0x352A8`;
- attempts only the retained timer/input release;
- then runs stack-canary/frame epilogue.

Nonmatching type:
- resumes unwind at `0x3530C`.

This is the key R-162 cleanup asymmetry.

## Unprotected prefix — retained timer/input
```
34F64 mov x0,x2
34F68 objc_retain
34F6C str x0,[sp,#8]
```

The timer/input is retained and committed before every typed range.

Therefore every expected typed catch can still reach its final release at `0x352AC`.

## Typed range 1 — window/noop/timer-maintenance admission
`0x34F70..0x34FBC` covers:
- `win` getter + retain;
- null-window branch;
- `noop`;
- noop-path `ticks` getter + `setTicks:`;
- missing-window timer `invalidate`.

Semantic split:
- window acquisition: temporary retained window may exist before stack commit;
- missing-window invalidate: invalidate side effect may already have happened;
- noop check: committed window can have normal release bypassed;
- noop tick maintenance: tick mutation may already have happened before throw.

Expected catch always skips normal window cleanup and reaches timer cleanup only.

## Unprotected bridge after range 1
`0x34FBC..0x34FC8` performs a direct window release and jumps to timer cleanup for normal noop/missing-window exits.

Failures here propagate.

## Typed range 2 — window layer / hidden / opacity-animation gate
`0x34FC8..0x35000` covers:
- window `layer` getter + retain;
- committed layer store at `sp+0`;
- window `isHidden`;
- layer `animationForKey:@"opacity"` + retain.

Semantic split:
- layer acquisition can fail before stack commit;
- hidden check begins after layer commit;
- animation lookup has only a temporary retained animation result because x22 commit is outside the range.

Expected catch:
- skips layer/window normal cleanup;
- reaches timer cleanup.

## Unprotected animation-result bridge
`0x35000..0x3500C`:
- commits temporary animation result to x22;
- releases it;
- exits if animation exists.

Failures here propagate.

## Typed targets presence probe
`0x3500C..0x3501C`:
- `targets` getter + retain.

The range ends before x22 commit/release/test.

Caught probe exceptions:
- can leave temporary targets ownership;
- skip layer/window cleanup;
- still reach timer cleanup.

## Typed targets provider / collection acquisition
`0x35028..0x3504C`:
- second `targets` getter + retain;
- retained provider commit x24;
- provider callable invocation;
- retained returned collection acquisition.

The range ends before x23 selected-collection commit.

Semantic split:
- provider acquisition may fail before x24 commit;
- collection acquisition begins with retained provider committed;
- provider normal release can be bypassed;
- returned collection remains temporary if protected call throws.

## Fallback target path
When the presence probe says no targets, typed `0x3505C..0x350D4` performs:
- window-layer opacity;
- presenter `alt`;
- fallback threshold check;
- single-object array construction + retain;
- selected-collection count;
- `phase` read;
- `setPhase:` toggle.

R-162 splits:
- fallback opacity/alt gate;
- fallback collection acquisition;
- selected collection count;
- phase read/mutation.

A phase mutation may already have applied before throw.

Once selected collection is committed, expected catch skips its normal release.

## Typed phase opacity + transaction setup
`0x350D4..0x35108`:
- phase getter;
- optional alt getter for target opacity;
- CATransaction begin;
- CATransaction setDisableActions:YES.

At this point the earlier phase toggle already completed.

Semantic split:
- phase/alt target-opacity preparation;
- transaction begin;
- disable actions.

Begin/disable side effects may already have applied before throw.
Expected catch skips selected collection, layer and window cleanup and reaches timer cleanup.

## Unprotected enumeration-retain bridge
`0x35108..0x35120`:
- retains selected collection for enumeration;
- commits that retained enumeration ownership.

Failures propagate.

## Typed initial enumeration read
`0x35120..0x35130`:
- `countByEnumeratingWithState:objects:count:`.

At entry:
- phase toggle completed;
- transaction begin completed;
- disable-actions completed;
- selected collection committed;
- extra enumeration retain committed.

Caught exception:
- bypasses both enumeration and selected-collection releases;
- skips later commit/ticks;
- bypasses layer/window cleanup;
- still reaches timer cleanup.

## Typed mutation / CALayer type filter
`0x35168..0x3518C`:
- conditional `objc_enumerationMutation`;
- CALayer class lookup;
- type check.

No per-layer retain exists yet.

Caught expected exception aborts remaining iteration and routes to timer cleanup only.

## Per-layer retained layer bridge
`0x3518C..0x3519C`:
- retains matching CALayer;
- commits x26.

This bridge is unprotected.

## Typed per-layer opacity-animation lookup
`0x3519C..0x351AC`:
- `animationForKey:@"opacity"`;
- retain-autoreleased result.

The result remains temporary at the protected endpoint.

Caught exception:
- bypasses retained layer x26 release;
- bypasses enumeration/selected collection releases;
- bypasses window-layer/window releases;
- reaches timer cleanup.

## Action-0 animation-result release
`0x351B0..0x351B4` releases a nonnil opacity-animation result.

If this release throws:
- resume unwind;
- retained layer release can be bypassed;
- enumeration + selected collection releases can be bypassed;
- window-layer/window/timer releases can be bypassed.

This path is not swallowed.

## Typed per-layer opacity / alt / group-target probe
`0x351B8..0x35204` begins only when opacity animation is absent.

It covers:
- layer opacity;
- presenter alt;
- threshold admission;
- presenter targets getter + retain;
- allowsGroupOpacity getter;
- presenter group getter.

Semantic split:
- per-layer opacity/alt gate;
- group-targets acquisition;
- group-opacity comparison.

If retained group-targets exists, its x27 release is still pending.

## Action-0 group-targets release
`0x35204..0x35210` releases x27.

A release exception:
- resumes unwind;
- bypasses layer/enumeration/selected-collection/window-layer/window/timer cleanup.

## Typed group-opacity + opacity mutations
`0x35218..0x35238` covers:
- presenter group getter;
- conditional `setAllowsGroupOpacity:`;
- layer `setOpacity:`.

Semantic split:
- group-opacity mutation may already apply before throw;
- opacity mutation may already apply before throw;
- setOpacity can run whether or not group-opacity mutation was necessary.

No rollback is performed by the catch.

## Action-0 retained-layer release
`0x35238..0x35240` releases x26.

If it throws:
- resume unwind;
- enumeration + selected collection + window-layer + window + timer cleanup can be bypassed.

## Typed enumeration advance
`0x3524C..0x35260`:
- next `countByEnumeratingWithState:objects:count:`.

Caught exception:
- bypasses enumeration retain release;
- bypasses selected collection/window-layer/window releases;
- skips transaction commit/tick update;
- reaches timer cleanup.

## Action-0 enumeration-collection release
`0x35268..0x35270` releases the extra enumeration ownership.

If it throws:
- resume unwind;
- selected collection/window-layer/window/timer cleanup can be bypassed;
- transaction commit and ticks are skipped.

## Typed commit + post-commit tick update
`0x35278..0x35290` covers:
- CATransaction commit;
- ticks getter;
- setTicks:.

Semantic split:
- commit may partially apply before throw;
- ticks read occurs only after commit returned;
- tick mutation occurs only after commit + ticks getter returned and may itself partially apply.

Expected catch:
- skips final selected collection/window-layer/window releases;
- still reaches timer cleanup.

## Shared final action-0 release range
`0x35290..0x352B0` contains four releases:
1. selected collection `0x35294`;
2. window layer `0x3529C`;
3. window `0x352A4`;
4. timer/input `0x352AC`.

All four map to action-0 resume unwind.

Important:
- this range is shared by normal post-commit cleanup and earlier pre-transaction exit paths;
- therefore a release exception here does **not** prove CATransaction commit occurred.

R-162 models four semantic release sites separately:
- selected collection release failure can bypass layer/window/timer cleanup;
- layer release failure can bypass window/timer;
- window release failure can bypass timer;
- timer release failure resumes unwind with no later object cleanup.

## Promoted runtime contract
Added:
- `DDTickPresenterExceptionSite`;
- `DDTickPresenterExceptionOutcome`;
- `DDResolveTickPresenterExceptionOutcome(site)`.

Typed semantic sites cover:
- window acquisition;
- missing-window invalidate;
- noop check/tick maintenance;
- layer acquisition/hidden/opacity-animation gate;
- targets probe/provider/collection;
- fallback opacity/alt/collection;
- count/phase toggle;
- phase target-opacity preparation;
- transaction begin/disable;
- initial enumeration;
- mutation/type filter;
- per-layer animation lookup;
- per-layer opacity/alt;
- group targets/comparison/mutation;
- layer opacity mutation;
- enumeration advance;
- transaction commit;
- post-commit tick read/mutation.

Action-0 sites cover:
- animation-result release;
- group-targets release;
- retained-layer release;
- enumeration-collection release;
- final selected-collection release;
- final window-layer release;
- final window release;
- final timer release.

Metadata records:
- expected typed swallow;
- timer-only catch cleanup continuation;
- nonmatching/action-0 unwind;
- temporary-vs-committed ownership;
- release bypass;
- phase/group-opacity/opacity/ticks/invalidate side-effect timing;
- transaction begin/disable/commit milestones;
- generic unprotected propagation.

## Explicit exclusions
R-162 does not:
- invalidate a real timer;
- query/mutate a real presenter/window/layer/collection;
- mutate live phase/group-opacity/opacity/ticks;
- start/commit real CATransactions;
- retain/release live objects;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 345E4
Next earlier LSDA-bearing function:
- `345E4 -> LSDA 0x113CD4`.
- Role: server-notice UI construction/presentation pipeline.

Exact table:
- 29 call-site entries;
- initial marker/text gate ranges use action index 7 = typed catch only;
- later protected UI-build ranges use action index 5 = typed catch + cleanup.

Landing aliases:
- `0x34B8C`;
- `0x34B90`;
- `0x34B94`;
- `0x34B98`;
- `0x34B9C`;
- `0x34BA0`;
- `0x34BA4`;
- `0x34BA8`.

They converge at `0x34BA8`.

Expected type:
- begin catch;
- load captured/byref result-reason slot;
- replace the slot with a static failure reason;
- release previous slot value;
- restore frame;
- end catch / return.

Nonmatching type:
- resumes unwind at `0x34BFC`.

R-163 should map:
- no-notice marker file probe;
- notice text type/length gate;
- contentView acquisition/bounds;
- `removeServerNotice`;
- UILabel/container allocation and styling;
- layer corner/border/color styling;
- hierarchy mutation;
- global/current server-notice strong store;
- present/live-state gate;
- deadline;
- userInteractionEnabled mutation;
- weak capture + 6s dispatch_after;
- failed-present removeFromSuperview/current-slot clear/failure reason;
- retained local cleanup;
- action-7 versus action-5 nonmatching cleanup distinction.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
