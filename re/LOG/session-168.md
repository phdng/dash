# LOG/session-168.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-167; commit R-166 locally, then promote exact data-only 33F5C showWithHostView block catch-all behavior as R-167 without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- R-166 committed locally as 364732a after user confirmed GREEN.
- Working tree clean after commit.
- Continued from session-167 scout of 33F5C -> LSDA 0x113C08.

## Exact LSDA table
1. 0x33F70..0x33F88 -> 0x33FA0, action 1 catch-all.
2. Tail after 0x33F88 is unprotected.

## Protected sequence
- buildShellIfNeeded.
- If buildShellIfNeeded returns true, installContent:hostView.
- present.

The captured present-result byte store at 0x33F90 is outside the protected range.

## Catch behavior
Landing 0x33FA0 has no type discriminator. It unconditionally begin/end-catches and returns immediately. Therefore every caught protected exception skips the captured present-result byte store. There is no local rollback of side effects already applied by buildShellIfNeeded, installContent:, or present.

## Semantic sites
- Build-shell exception: buildShell side effects may already have started; install/present have not been reached.
- Install-content exception: buildShell definitely returned true; installContent may already have applied side effects; present has not been reached.
- Present exception: buildShell definitely returned true and installContent definitely completed; present may already have applied side effects; present result is still uncommitted because the byte store is later and unprotected.
- Unprotected tail exceptions propagate.

## Runtime contract
Added DDShowWithHostViewBlockExceptionSite, DDShowWithHostViewBlockExceptionOutcome, and DDResolveShowWithHostViewBlockExceptionOutcome(site). The resolver is data-only and records catch-all swallow/return behavior, captured-result-store skip, prior-success ordering, possible side-effect persistence, and unprotected propagation.

## Explicit exclusions
No live DDz1/UI invocation, host-view mutation, captured-state mutation, exception runtime, or unwind execution.

## Next target
R-168: 33DB4 -> LSDA 0x113BE8. Existing project evidence identifies 33DB4 as a duodash_ab_content_inset value-read site, but exact LSDA/raw-ARM64 behavior still needs decoding before promotion.
