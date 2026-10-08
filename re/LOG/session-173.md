# LOG/session-173.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-172; resolve the adjacent post-setRoot exception ranges inside sub_3257C -> LSDA 0x113860, promote only data-only routing, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD b3afad5.
- Working tree clean and aligned with origin after user push.
- User reported session-172 build GREEN.

## Exact LSDA entries
Focused decode of LSDA 0x113860 around the layout-confirm post-setRoot region:

- entry 127: 0x338B4..0x338C0 -> 0x33A1C, action 5 (R-171 setRoot:)
- entry 128: 0x338C0..0x338D0 -> 0x33D18, action 0
- entry 129: 0x338D0..0x338E8 -> 0x33A1C, action 5
- entry 130: 0x338E8..0x339B4 -> 0x33D18, action 0

Raw ARM64 maps entry 128 exactly to:
- address formation for qword_164510;
- load of the new CNABLayoutConfirm controller;
- objc_storeStrong(&qword_164510, controller).

Landing 0x33D18 is cleanup-only and immediately resumes unwind. This range is not a typed swallow.

Raw ARM64 maps entry 129 exactly to:
- host/root loads;
- addSubview: at 0x338D8;
- controller load;
- tick:15 at 0x338E4.

Landing stub 0x33A1C branches to shared typed cleanup 0x33C64.

## Site semantics
Global storeStrong cleanup-only site:
- setRoot: definitely completed before entry;
- global commit may have begun/applied before an exception;
- addSubview:/tick: are not reached;
- exception resumes unwind, with no typed swallow.

Root-attach typed subsite:
- setRoot: and qword_164510 global commit definitely completed;
- addSubview: may have applied before throwing;
- tick: is definitely not reached;
- expected typed cleanup attempts to remove the committed root, clears/releases qword_164510, and outer-returns;
- nonmatching type resumes unwind.

Countdown-tick typed subsite:
- setRoot:, global commit, and root attachment definitely completed;
- tick:15 may have applied before throwing;
- expected typed cleanup removes the committed root when present, clears/releases qword_164510, and outer-returns;
- nonmatching type resumes unwind.

## Runtime contract
Added:
- DDLayoutConfirmPostCommitExceptionSite
- DDLayoutConfirmPostCommitExceptionOutcome
- DDResolveLayoutConfirmPostCommitExceptionOutcome(...)

The resolver separates cleanup-only storeStrong unwind from typed root-attach and tick recovery.

## Explicit exclusions
Data-only only. No live objc_storeStrong, UIKit attachment/removal, tick call, global mutation, begin/end-catch, or unwind execution.

## Next
After compiler green, continue site-scoped decoding inside 3257C -> LSDA 0x113860 after the post-commit layout-confirm region, again preferring an exact protected operation or tightly bounded sequence.
