# LOG/session-172.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-171; promote the next closed site-scoped exception outcome inside sub_3257C -> LSDA 0x113860, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 5832090.
- Working tree clean.
- User reported session-171 build GREEN.

## Target site
Exact call-site entry:
- 0x338B4..0x338C0 -> 0x33A1C, action 5.

Raw ARM64:
- 0x338B4 mov x0, x19
- 0x338B8 load root argument
- 0x338BC call -[CNABLayoutConfirm setRoot:]
- protected range ends at 0x338C0.

This occurs after fast enumeration has fully completed and the retained enumeration array has been released.

## Landing and continuation
0x33A1C is a branch stub to shared typed cleanup 0x33C64.

Expected discriminator 1:
- begins catch;
- clears splash in-flight byte;
- clears/releases qword_164500;
- conditionally obtains/removes qword_164510.root and clears/releases qword_164510;
- releases retained caught exception;
- ends catch;
- branches to outer cleanup 0x339A4 and returns.

Nonmatching type resumes unwind via 0x33CF0 -> 0x33D00 -> 0x33D1C.

## Timing / side effects
- Fast enumeration definitely completed before setRoot:.
- setRoot: itself may have changed the CNABLayoutConfirm controller root before throwing; no rollback is visible.
- New qword_164510 global commit via objc_storeStrong at 0x338CC is definitely not reached.
- Host addSubview: at 0x338D8 is definitely not reached.
- tick:15 at 0x338E4 is definitely not reached.
- Shared cleanup can still clear an older qword_164510 controller if one was present.

## Runtime contract
Added:
- DDLayoutConfirmSetRootExceptionOutcome
- DDResolveLayoutConfirmSetRootExceptionOutcome(void)

Recorded:
- expected typed swallow;
- shared splash/layout-confirm cleanup intent;
- outer cleanup continuation;
- nonmatching unwind;
- completed enumeration milestone;
- possible controller-root mutation;
- definite pre-global-store, pre-host-attach, and pre-tick timing.

## Explicit exclusions
Data-only only. No live controller mutation, UIKit/view attachment, global mutation, begin/end-catch, or unwind execution.

## Next
After compiler green, continue site-scoped decoding inside 3257C -> LSDA 0x113860 with another exact protected operation or tightly bounded sequence.
