# Session-354 — Preflight stage-order regression tests

Started with clean worktree on `chore/reconstruction-build-ci`.

## Compiled Objective-C changes
- Expanded `DDHostSwitchPreflightSelfTest` in `HostFlowAdapter.m` to ensure a non-array hosted size argument is refused with the size failure bit.
- Added an early `swapInFlight` refusal case to ensure preflight stops before BID matching and late slot-size/shell evaluations.
- Kept public ABI unchanged and self-test excluded from tweak startup.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. The macOS Objective-C executable smoke test and arm64 Theos CI were not run. No commit/push.
