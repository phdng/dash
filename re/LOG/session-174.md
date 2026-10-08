# LOG/session-174.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-173; promote exact reapplyMaximizeAfterHost recovery routing inside sub_3257C -> LSDA 0x113860, including nested recovery exception behavior, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD af2659b.
- Working tree clean and aligned with origin after user push.
- User reported session-173 build GREEN.

## Top-level protected site
Exact LSDA entry:
- 0x32A4C..0x32A50 -> 0x33A5C, action 5.

Raw ARM64 maps this range exactly to:
- call reapplyMaximizeAfterHost at 0x32A4C.
- continuation 0x32A50 begins the normal present path.

Expected typed catch at 0x33A5C:
- begins catch;
- clears/reset host/maximize state fields;
- advances generation/reset flags;
- clears pending retained state;
- retains the recovery collection at host ivar +0x148;
- enumerates collection items and sends setHidden:NO;
- clears collection with removeAllObjects;
- conditionally calls rebuildMatForEnvironment if the saved pre-reset flag requested it;
- releases caught exception, ends catch;
- branches to 0x32A50, so present still runs.

Nonmatching top-level type resumes unwind.

## Nested recovery LSDA
Within the catch recovery sequence:
- 0x33B1C..0x33B2C -> 0x33BE0, action 5: initial fast enumeration.
- 0x33B50..0x33B68 -> 0x33BF0, action 5: enumerationMutation/setHidden:NO.
- 0x33B74..0x33B88 -> 0x33BE4, action 5: subsequent fast enumeration.
- 0x33B90..0x33B98 -> 0x33D18, action 0: collection release cleanup.
- 0x33BA0..0x33BA4 -> 0x33BDC, action 5: removeAllObjects.
- 0x33BAC..0x33BB0 -> 0x33BC0, action 5: rebuildMatForEnvironment.
- 0x33BB0..0x33BB8 -> 0x33D18, action 0: caught-exception release/end-catch cleanup.

Initial/subsequent enumeration, mutation-or-setHidden, and removeAllObjects typed failures terminate the original recovery catch and resume unwind; present is not reached.

The rebuildMat nested landing is special:
- compares nested discriminator to the original catch discriminator;
- matching type is itself begin/end-caught;
- then execution continues through original catch cleanup and branches to 0x32A50 present;
- nonmatching type ends original catch and resumes unwind.

Action-0 cleanup ranges resume unwind.

## Runtime contract
Added:
- DDReapplyMaximizeRecoveryExceptionSite
- DDReapplyMaximizeRecoveryExceptionOutcome
- DDResolveReapplyMaximizeRecoveryExceptionOutcome(...)

The resolver records top-level reset/reveal/clear/optional-rebuild/present continuation and exact nested abort-vs-rebuild-swallow behavior.

## Explicit exclusions
Data-only only. No live private selector execution, UIKit/view mutation, host/global state mutation, begin/end-catch, or unwind execution.

## Next
After compiler green, continue site-scoped decoding inside 3257C -> LSDA 0x113860 with another exact protected operation or bounded recovery sequence.
