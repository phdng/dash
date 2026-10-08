# LOG/session-176.md
_Date: 2026-10-08. Objective: shift from runtime-contract accumulation to executable subsystem integration after the user questioned why only ReconstructionRuntime was changing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD d066f50.
- Working tree clean.
- Existing Makefile compiled only Tweak.x + ReconstructionRuntime.m.
- Existing synthesis modules (SpikeHosting, PresentCommitAck, CNABConn, etc.) remained outside the executable target.

## Architectural change
Added new compile-safe module:
- re/RECONSTRUCTION/RecoveryRouting.m

The module imports ReconstructionRuntime.h and consumes the exact evidence-safe resolver families already promoted in R-169..R-174:
- initial layout-confirm enumeration recovery;
- subsequent enumeration recovery;
- setRoot recovery;
- post-commit root-attach/tick recovery;
- reapplyMaximize recovery;
- present + weak-overlay cleanup recovery.

It derives a one-time capability mask with dispatch_once. No private selector, UIKit, recovered global mutation, begin/end-catch, or unwind behavior is executed.

## Build integration
Makefile now compiles:
- Tweak.x
- ReconstructionRuntime.m
- RecoveryRouting.m

DuoDashShared.h exports:
- DDRecoveryRoutingStart(void)
- DDRecoveryRoutingCapabilities(void)

Tweak.x now calls DDRecoveryRoutingStart() immediately after DDReconstructionStart().

This is intentionally the first executable consumer outside ReconstructionRuntime. It establishes a stable seam so the next promoted subsystem can depend on RecoveryRouting rather than directly coupling to every low-level resolver.

## Verification changes
scripts/verify_reconstruction.py now:
- requires RecoveryRouting.m to exist;
- requires Makefile to include it;
- checks that RecoveryRouting consumes the key resolver families;
- checks Tweak.x bootstraps DDRecoveryRoutingStart().

## Explicit exclusions
No existing approximation-heavy synthesis module was force-added to the target. PresentCommitAck.m, SpikeHosting.m, CNABConn.m, etc. still contain unresolved/private contracts and placeholders, so adding them wholesale would create misleading compiler-green behavior.

## Next
After compiler green, promote one concrete compile-safe subsystem adapter that consumes RecoveryRouting. Keep new executable behavior outside ReconstructionRuntime unless it is truly a low-level evidence resolver.
