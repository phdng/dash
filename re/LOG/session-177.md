# LOG/session-177.md
_Date: 2026-10-08. Objective: continue executable subsystem promotion after user-confirmed GREEN for session-176; add a concrete post-present host-flow adapter outside ReconstructionRuntime, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD ba94dce.
- Working tree clean and aligned with origin after user push.
- User reported session-176 build GREEN.

## Exact source site
sub_3257C -> LSDA 0x113860:
- 0x32A94..0x32AB4 -> 0x33A3C, action 5.

Raw ARM64:
- 0x32A94: +[DDz4 shared]
- 0x32A9C: objc_retainAutoreleasedReturnValue
- 0x32AA0: retain shared controller in x22
- 0x32AA4: -[DDz4 teardown]
- 0x32AAC/0x32AB0: -[DDz4 buildInHost:] using retained host x21
- 0x32AB4: normal-path release of retained DDz4 controller
- 0x32ABC: continuation release of retained host input

Landing 0x33A3C:
- validates expected discriminator 1;
- matching type begin/end-catches;
- branches to 0x32ABC;
- nonmatching type routes to 0x33CF0 -> 0x33D00 -> 0x33D1C and resumes unwind.

## Executable integration
Added re/RECONSTRUCTION/HostFlowAdapter.m to the tweak target.

The adapter:
- is bootstrapped from Tweak.x with DDHostFlowAdapterStart();
- consumes DDRecoveryRoutingCapabilities();
- only enables when the reapply-maximize and present-overlay recovery capabilities are available;
- exposes DDPostPresentHostFlowDecisionForSite(...).

Three site-aware decisions are modeled:
1. Shared acquisition:
   - teardown/buildInHost not reached;
   - catch skips remaining host block;
   - normal DDz4 release at 0x32AB4 is bypassed if acquisition got far enough to retain;
   - retained host input is still released at 0x32ABC.
2. Teardown:
   - shared DDz4 controller definitely acquired;
   - teardown may have applied side effects before throwing;
   - buildInHost not reached;
   - normal DDz4 release skipped;
   - retained host released at continuation.
3. BuildInHost:
   - shared controller acquired;
   - teardown definitely completed;
   - buildInHost may have partially applied before throw;
   - normal DDz4 release skipped;
   - retained host released at continuation.

## RecoveryRouting public surface
Moved recovery capability bit definitions to DuoDashShared.h so executable adapters can consume them without importing ReconstructionRuntime internals.

## Verification
Verifier now requires:
- HostFlowAdapter.m exists and is present in Makefile;
- Tweak.x bootstraps DDHostFlowAdapterStart();
- adapter consumes RecoveryRouting capability bits;
- exact shared/teardown/buildInHost sites and continuation/lifetime decisions are present.

## Explicit exclusions
No live DDz4 shared, teardown, buildInHost, UIKit/private-selector execution, recovered global mutation, begin/end-catch, or unwind execution.

## Next
After compiler green, continue executable promotion with another bounded host-flow adapter/decision outside ReconstructionRuntime.
