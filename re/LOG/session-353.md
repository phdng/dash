# Session-353 — Fail-closed malformed switch input handling

Clean worktree at start on `chore/reconstruction-build-ci`.

## Compiled Objective-C changes
- `HostFlowAdapter.m`: `DDHostSwitchBidsMatch` now checks both requested and hosted inputs are actual NSArrays before `.count` and indexed access. This prevents exceptions/unrecognized selectors for a malformed non-array caller input while retaining per-index NSString equality and 1..3 count limit.
- Added explicit self-test assertions for wrong-type requested/hosted arrays, an NSNull BID element and NSNull slot-size element. Tests are in compiled code but not auto-run at tweak startup.
- No private API, host switch or UI mutation added.

## Checks
PASS `python scripts/verify_reconstruction.py` (30 modules), `git diff --check`. Objective-C macOS smoke test and Theos arm64 CI not run here. No commit/push.
