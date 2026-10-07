# LOG/session-165.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-164 commit `e28c5a6`; decode and promote exact data-only `34524` reset/teardown catch-all behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `e28c5a6`.
- Working tree clean and synchronized with origin.
- User confirmed session-164 macOS CI/compiler GREEN.

## Target
- Function: `sub_34524`.
- LSDA: `0x113CB8`.
- Role: conditional presenter/window reset followed by collection clear and teardown.

## Exact LSDA
1. `0x34524..0x34598` -> no landing.
2. `0x34598..0x345A4 -> 0x345B0`, action 1 catch-all.
3. `0x345A4..0x345C0` -> no landing.

Landing:
```
345B0 objc_begin_catch
345B4 restore frame
345BC tail objc_end_catch
```

There is no type discriminator and no retry/alternate continuation.

## Reset-path prefix
The reset path is entered only when byte `+0xA9 == 1`.

Before the protected range it performs, in order:
- clear reset flag `+0xA9`;
- write sentinel `-1` to `+0xB0`;
- write `CGRectNull` origin+size at `+0xC0`;
- clear bytes `+0x130` and `+0x131`;
- clear qword/counter `+0x138`;
- load old strong value from `+0x140`;
- clear strong slot `+0x140`;
- release the old strong value at `0x3458C`.

The release is unprotected.

Therefore if that release throws:
- every reset store above is already committed;
- the strong slot is already nil;
- collection clear has not started;
- teardown has not started;
- the exception propagates.

R-164 exposes this as a dedicated unprotected site rather than merging it into generic propagation.

## Protected site — removeAllObjects after reset
Protected call at `0x34598`:
- sends `removeAllObjects` to object at `+0x148`.

Reaching this call proves:
- all reset stores completed;
- the old `+0x140` release returned normally.

If `removeAllObjects` throws:
- collection mutation may already have partially applied;
- teardown has not started;
- action-1 catch swallows the exception;
- function returns immediately.

No collection rollback is attempted.

## Protected site — teardownWindow after reset
After `removeAllObjects` returns:
```
3459C load owner
345A0 teardownWindow
```

Thus a teardown exception on reset path proves:
- all reset stores completed;
- old strong-slot release completed;
- collection clear completed.

If teardown throws:
- teardown side effects may already have applied;
- catch swallows;
- function returns.

No compensating rebuild/restore exists.

## Protected site — teardownWindow without reset
If `+0xA9 != 1`, control branches directly from `0x34540` to `0x345A0`.

Thus:
- none of the reset stores are attributable to this path;
- collection clear was not attempted;
- only teardown may have side effects before the caught exception.

Catch semantics remain identical:
- swallow any exception;
- immediate return.

## Promoted runtime contract
Added:
- `DDResetTeardownExceptionSite`:
  - `StrongSlotReleaseUnprotected`;
  - `RemoveAllObjectsAfterReset`;
  - `TeardownWindowAfterReset`;
  - `TeardownWindowWithoutReset`;
  - `UnprotectedRange`.
- `DDResetTeardownExceptionOutcome`.
- `DDResolveResetTeardownExceptionOutcome(site)`.

Metadata records:
- action-1 swallow + immediate return;
- exact reset/sentinel/CGRect/state/counter/strong-slot milestones;
- unprotected old-slot release propagation;
- old-slot release completion before protected reset-path calls;
- partial collection-clear possibility;
- collection-clear completion before reset-path teardown;
- explicit no-clear/no-reset semantics on direct teardown;
- explicit teardown-not-started timing for earlier failures.

## Explicit exclusions
R-164 does not:
- mutate live presenter state;
- clear live collections;
- call live teardownWindow;
- retain/release live objects;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 34250
Next earlier LSDA-bearing function:
- `34250 -> LSDA 0x113C60`.
- Role: resolve CarPlay CADisplay using AVExternalDevice screen ID.

Exact 13-entry table:
1. `0x34250..0x342B8` unprotected.
2. `0x342B8..0x342E8 -> 0x34520`, action 0.
3. `0x342E8..0x34308` unprotected.
4. `0x34308..0x34338 -> 0x34520`, action 0.
5. `0x34338..0x3434C` unprotected.
6. `0x3434C..0x34404 -> 0x34520`, action 0.
7. `0x34404..0x34440` unprotected.
8. `0x34440..0x34448 -> 0x3448C`, action 5.
9. `0x3444C..0x34458 -> 0x34488`, action 5.
10. `0x3446C..0x34474 -> 0x34520`, action 0.
11. `0x34474..0x344A0` unprotected.
12. `0x344A0..0x344E0 -> 0x34520`, action 0.
13. `0x344E0..0x34524` unprotected.

Typed landing topology:
- bounds-send landing `0x34488 -> 0x34490`;
- capability landing `0x3448C` checks action/type then converges at `0x34490`;
- expected type begin/end-catches;
- candidate display x24 is released;
- x24 is forced nil;
- final screenIDs/displays/external-device cleanup continues;
- return value is nil.

Action-0 cleanup and nonmatching typed exceptions resume unwind at `0x34520`.

R-165 should map:
- CADisplay and AVExternalDevice class admission;
- currentCarPlayExternalDevice acquisition;
- screenIDs ownership/type check;
- firstObject screen ID;
- displays collection double-retain/enumeration;
- uniqueId ownership/type/equality;
- matched candidate retain;
- bounds capability check and bounds send;
- >=20x20 validation;
- candidate retain/nil fallback;
- every cleanup action-0 boundary.

## Scout after R-165 — 34020
Next earlier LSDA-bearing function:
- `34020 -> LSDA 0x113C1C`.
- Role: build/install/present the Phase-4a display-OK UI.

Exact table has 9 entries:
- action-7 `0x34038..0x3403C -> 0x341B8` around `buildShellIfNeeded`;
- action-5 UI ranges covering UIView/UILabel/style/install/present;
- unprotected retained-style releases/bridges.

All typed landing aliases converge at `0x341C0`:
- expected type begin/end-catches and returns;
- nonmatching resumes unwind at `0x341DC`.

R-166 should split shell-build gate, content/background, label styling/text, hierarchy/installContent, and present-result capture.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
