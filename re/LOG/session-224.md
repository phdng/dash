# LOG/session-224.md
_Date: 2026-10-08. Objective: switch away from saturated NavProvider helpers and promote exact pure camera-relay source-token mapper 84258 without relay I/O or global state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD c9f01c0.
- Working tree clean; branch ahead 39.

## Candidate selection
- `87CA0` AC-power probe was skipped because it would require adding IOKit linkage solely for one helper.
- `84258` is a pure Foundation string mapper shared by camera relay callers and adds no framework dependency.

## Exact 84258 semantics
- source equal to `waze` => 2.
- else source equal to `google_maps` => 1.
- else source equal to `provider` => 3.
- else => 0.
- Nil naturally falls through all Objective-C equality messages to 0.

## Executable promotion
Added standalone compiled `CameraRelayHelpers.m` with `DDCameraRelaySourceCode(NSString *source)`; exported in DuoDashShared.h and added to Makefile/verifier.

## Boundary
No source-file lookup, app-container scanning, relay plist writes, Darwin notifications, DataRouter submission, UIKit/private APIs, or global state are activated.

## Next
After compiler green, inspect another pure camera-relay helper only if independent from file scanning/relay writes/DataRouter/private state; otherwise switch subsystem again.