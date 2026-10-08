# LOG/session-195.md
_Date: 2026-10-08. Objective: determine whether repair and republish have an exact evidence-safe integration point in 27E20, promote only that bounded ordering, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 39985b3.
- Working tree clean; branch ahead 10.

## Direct 27E20 tail evidence
At the end of the repair/status-record block:
- config_repair.record bookkeeping completes;
- autorelease pool is popped;
- `sub_74C8()` is called unconditionally;
- `sub_7B29C("springboard.bringup")` follows immediately afterward.

This ordering is outside the knob/clean/repaired branch structure: republish happens regardless of whether repair was skipped, no-op, repaired, or its final synchronize returned failure.

## Executable integration seam
Added `DDRepairAndRepublishAppBridge()`.
It intentionally:
- invokes `DDRepairAppBridgeConfigIfNeeded()` first and ignores its BOOL for control flow;
- always invokes `DDRepublishAppBridgeResolvedSnapshot()` second;
- returns republish plist-write success only as reconstruction observability.

## Explicit exclusion
The subsequent private `sub_7B29C("springboard.bringup")` behavior is not reconstructed or called.
The combined seam remains explicit/manual and is not wired into startup.

## Next
After compiler green, continue another bounded executable subsystem. Do not auto-wire repair+republish into startup because the proven call site belongs to a broader SpringBoard bringup flow with private behavior after it.