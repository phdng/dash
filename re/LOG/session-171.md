# LOG/session-171.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-170; promote the next closed site-scoped exception outcome inside sub_3257C -> LSDA 0x113860, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 909dfec.
- Working tree clean.
- User reported session-170 build GREEN.

## Target site
Exact call-site entry from the already decoded 3257C LSDA:
- 0x33890..0x338A4 -> 0x33A30, action 5.

Raw ARM64 maps the protected range to the later fast-enumeration fetch:
- prepare state/object buffer;
- load the retained layout-confirm row array from sp+0x48;
- call countByEnumeratingWithState:objects:count:;
- returned count would be committed to x27 at 0x338A4, immediately outside the protected range.

This fetch occurs after the first enumeration batch and its row-building loop. Therefore one or more prior items may already have applied view mutations before this exception.

## Landing and continuation
0x33A30 is a branch stub to shared typed cleanup 0x33C64.

For expected discriminator 1, shared cleanup:
- begins catch;
- clears splash in-flight byte;
- clears/releases qword_164500;
- conditionally obtains qword_164510.root, removes it from superview, releases root, clears/releases qword_164510;
- releases retained caught exception;
- ends catch;
- branches to outer cleanup 0x339A4 and normal function return.

Nonmatching type resumes unwind via 0x33CF0 -> 0x33D00 -> 0x33D1C.

## Timing / side effects
- Subsequent enumeration result is uncommitted if the protected call throws.
- Prior enumeration items may already have mutated row backgrounds/layers/labels and attached subviews; this catch does not roll those local mutations back.
- The new layout-confirm global storeStrong occurs later at 0x338C0, so it definitely has not committed before this catch.
- Shared cleanup may clear an older qword_164510 controller if present.

## Runtime contract
Added:
- DDLayoutConfirmSubsequentEnumerationExceptionOutcome
- DDResolveLayoutConfirmSubsequentEnumerationExceptionOutcome(void)

Recorded:
- expected typed swallow;
- shared splash/layout-confirm cleanup intent;
- outer-cleanup-and-return continuation;
- nonmatching unwind;
- uncommitted subsequent count;
- possible persistence of prior view-hierarchy mutations;
- definite pre-storeStrong timing for the new layout-confirm global.

## Explicit exclusions
Data-only only. No live enumeration, UIKit/view mutation, global mutation, begin/end-catch, or unwind execution.

## Next
After compiler green, continue site-scoped decoding inside 3257C -> LSDA 0x113860 and select another closed landing alias rather than grouping broad ranges.
