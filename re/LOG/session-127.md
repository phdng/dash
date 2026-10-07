# LOG/session-127.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-126 commit `d99b720`; decode and promote exact data-only `3C1F0` degrade-slot exception behavior from Mach-O LSDA/raw ARM64, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD at session start: `d99b720`.
- Working tree: clean.
- Branch synchronized with origin.
- User confirmed the session-126 macOS CI/compiler build was green.

## Target selection

Persisted unwind enumeration from session-125/session-126 showed the next earlier LSDA-bearing function:
- `3C1F0 -> LSDA 0x1145B8`.

Decompiler identity:
- `-[DDz2 degradeSlot:bid:native:why:]`.

Reviewed:
- `decompile/3C1F0.c`;
- raw ARM64 `0x3C1F0..0x3C368`;
- Mach-O LSDA bytes at `0x1145B8`;
- existing hosting/degrade synthesis and prior exception-outcome conventions.

The first arm64 FAT slice begins at file offset `0x4000`.

## Exact LSDA call-site table

LSDA header:
- LPStart encoding: omitted;
- type-table encoding: `0x9B`;
- call-site encoding: ULEB128;
- call-site table length: `0x0F` bytes.

Decoded entries:

1. `0x3C1F0..0x3C26C` -> no landing pad.
2. `0x3C26C..0x3C2C8` -> landing `0x3C350`, action 5.
3. `0x3C2C8..0x3C368` -> no landing pad.

Therefore `3C1F0` has exactly one local typed protected range.

## Protected private-controller teardown

Raw ARM64 `0x3C26C..0x3C2C8` covers:

- `respondsToSelector:viewIfLoaded`;
- optional `viewIfLoaded` send;
- retain-autoreleased handling for the returned view;
- `removeFromSuperview`;
- `respondsToSelector:invalidate`;
- optional `invalidate`.

The normal retained-view release is at `0x3C2C8`, immediately after the protected range.

Landing `0x3C350`:
- compare catch discriminator with expected value 1;
- nonmatching -> `0x3C364` resume unwind;
- expected type -> begin catch, end catch, branch `0x3C360 -> 0x3C2D0`.

No reason-probe, retry, or alternate private teardown is performed by the catch.

## Exact continuation at 0x3C2D0

At catch rejoin:
- the selected hosted-controller ivar has **not** yet been cleared;
- `0x3C2D0` loads the selected ivar;
- `0x3C2D4` stores nil to that ivar;
- `0x3C2D8` releases the old ivar value;
- `0x3C2DC..0x3C2F8` replace `qword_163D30[slot]` with the empty-string constant and release the old hosted bid;
- `0x3C2FC..0x3C314` call `sub_36E98(slot,width,height)`, retain-autoreleased result, and store it as the return placeholder;
- later normal cleanup releases the retained controller/reason/bid arguments and returns the placeholder.

Therefore an expected exception from the protected private teardown:
- is swallowed locally;
- skips the remaining private teardown portion;
- does **not** skip the pending hosted-controller ivar clear/release;
- does **not** skip hosted-bid replacement with empty string;
- does **not** skip degraded placeholder creation.

If a view had already been retained before the throw, the direct branch to `0x3C2D0` bypasses the normal view release at `0x3C2C8`. This is modeled as a possible retained-view-release bypass, not a guaranteed lifetime change.

## Unprotected behavior

Both surrounding ranges have no local landing pad:
- pre-teardown `0x3C1F0..0x3C26C`;
- post-teardown `0x3C2C8..0x3C368`.

Thus exceptions from:
- selected controller retain setup before the protected region;
- controller-ivar release after the catch rejoin;
- hosted-bid release/reset;
- `36E98` placeholder creation;
- final cleanup/autorelease return;

propagate rather than using the local typed catch.

## Promoted runtime contract

Added:
- `DDDegradeSlotExceptionSite`:
  - `PrivateControllerTeardown`;
  - `UnprotectedRange`;
- `DDDegradeSlotExceptionOutcome`;
- `DDResolveDegradeSlotExceptionOutcome(site)`.

For `PrivateControllerTeardown`:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingPrivateTeardown = YES`;
- `controllerIvarClearStillPendingAtCatch = YES`;
- `shouldContinueControllerIvarClear = YES`;
- `shouldContinueHostedBundleReset = YES`;
- `shouldContinuePlaceholderCreation = YES`;
- `retainedViewReleaseCouldBeBypassed = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

For `UnprotectedRange`:
- `exceptionWouldPropagate = YES`.

Unknown/None returns all false.

The resolver is descriptive data-only metadata. It does not invoke any private selector, mutate hosted state, or create placeholders.

## Explicit exclusions

R-126 does not:
- call `viewIfLoaded`, `removeFromSuperview`, or `invalidate`;
- mutate real hosted-controller ivars;
- write live `qword_163D30` hosted-bid state;
- call `36E98`;
- retain/release live private objects through the resolver;
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch/resume-unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final verifier, CatDesk verification status, and `git diff --check` are run immediately before commit.

## Scout for next batch — 3BBF0

Direct unwind enumeration shows the next earlier LSDA-bearing function:
- `3BBF0 -> LSDA 0x114538`.

Decompiler identity:
- `-[DDz2 spikeCreateSlot:index:native:]`.

Decoded LSDA call-site table has 19 entries:

1. `0x3BBF0..0x3BD48` -> no landing.
2. `0x3BD48..0x3BD58` -> `0x3C150`, action 5.
3. `0x3BD64..0x3BD74` -> `0x3C154`, action 5.
4. `0x3BDD8..0x3BDE8` -> `0x3C158`, action 5.
5. `0x3BDF8..0x3BE14` -> `0x3C14C`, action 5.
6. `0x3BE14..0x3BE20` -> no landing.
7. `0x3BE20..0x3BE34` -> `0x3C15C`, action 5.
8. `0x3BE34..0x3BE6C` -> no landing.
9. `0x3BE6C..0x3BEB4` -> `0x3C15C`, action 5.
10. `0x3BEC0..0x3BF00` -> `0x3C148`, action 5.
11. `0x3BF00..0x3BF48` -> `0x3C12C`, action 5.
12. `0x3BF48..0x3C018` -> no landing.
13. `0x3C018..0x3C030` -> `0x3C154`, action 5.
14. `0x3C038..0x3C060` -> `0x3C158`, action 5.
15. `0x3C068..0x3C090` -> `0x3C15C`, action 5.
16. `0x3C098..0x3C0C0` -> `0x3C148`, action 5.
17. `0x3C0C0..0x3C184` -> no landing.
18. `0x3C184..0x3C1C4` -> `0x3C1E0`, action 0.
19. `0x3C1C4..0x3C1F0` -> no landing.

Raw tail:
- `0x3C12C` expected typed catch begin/end-catches then rejoins `0x3BF50`;
- landing stubs `0x3C148..0x3C158` converge at common typed catch `0x3C15C`;
- expected common catch captures the exception description, formats a degrade reason, invokes the slot degrade path, ends catch, then rejoins normal cleanup at `0x3C0F8`;
- nonmatching type resumes unwind at `0x3C1E8`;
- `0x3C184..0x3C1C4` is action-0 cleanup for work performed inside the catch and leads through `0x3C1E0` end-catch + resume-unwind.

R-127 should map the individual protected ranges to exact pre-/post-state-commit points before promotion. In particular, it must distinguish the special `0x3C12C -> 0x3BF50` continuation from the common degrade-on-exception path.

## Next

After the user pushes session-127 and confirms compiler green:
- R-127: decode/promote exact `3BBF0 -> LSDA 0x114538` per-site exception outcomes;
- preserve any already-committed hosted bid/native-size/controller state exactly by range;
- keep SpringBoard private controller/entity/view construction and live degrade execution excluded.

Known unresolved items remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device runtime smoke testing.
