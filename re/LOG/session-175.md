# LOG/session-175.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-174; promote exact present + weak-overlay cleanup exception routing inside sub_3257C -> LSDA 0x113860, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 44dbad6.
- Working tree clean.
- User reported session-174 build GREEN.

## Exact protected site
LSDA entry:
- 0x32A54..0x32A68 -> 0x33C30, action 5.

Raw ARM64:
- 0x32A54: call present.
- 0x32A58..0x32A60: route/captured result-byte store.
- 0x32A64: call sub_702BC.
- 0x32A68: protected range ends.

Decompile confirms:
- v64 = present();
- captured result byte = v64;
- sub_702BC(v64);
- only after this range does code test the captured result and, on success, retain the host, obtain DDz4 shared, teardown, and buildInHost:.

## sub_702BC
Decompile of 0x702BC:
- objc_loadWeakRetained(&qword_164550);
- if nonnil, removeFromSuperview;
- objc_storeWeak(&qword_164550, nil);
- release retained weak target.

The helper has no local swallow in this evidence path, so an escaping exception is handled by the outer typed site above.

## Landing and continuation
Landing 0x33C30 stores exception/type and routes through 0x33CF0 -> 0x33D00.
For discriminator 1:
- begin catch;
- end catch;
- branch to 0x339B4 function epilogue;
- immediate return.

Nonmatching discriminator resumes unwind at 0x33D1C.

Therefore a matching exception from either present or sub_702BC skips all later successful-present logic, including DDz4 teardown and buildInHost:.

## Site-aware timing
Present-call subsite:
- presentation side effects may already have started before throw;
- captured present-result byte is definitely not committed;
- weak-overlay cleanup is not reached;
- later success branch/teardown/buildInHost are skipped.

Weak-overlay-cleanup subsite:
- captured present-result byte is definitely committed;
- presentation side effects may persist;
- weak overlay removal may already have occurred;
- weak-slot clear may have started/not completed depending on throw point;
- later success branch/teardown/buildInHost are skipped.

## Runtime contract
Added:
- DDPresentAndOverlayCleanupExceptionSite
- DDPresentAndOverlayCleanupExceptionOutcome
- DDResolvePresentAndOverlayCleanupExceptionOutcome(...)

Data-only resolver distinguishes the two timing subsites while preserving common typed swallow/direct-return and nonmatching unwind behavior.

## Explicit exclusions
No live present invocation, view removal, weak store, DDz4 teardown/buildInHost, begin/end-catch, or unwind execution.

## Next
After compiler green, continue site-scoped decoding inside 3257C -> LSDA 0x113860. Natural next candidate is the post-present-success DDz4 shared/teardown/buildInHost typed range 0x32A94..0x32AB4.
