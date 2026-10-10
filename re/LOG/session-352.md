# Session-352 — Per-slot staged switch preflight

Working tree clean at session start on chore/reconstruction-build-ci.

## Code changes
- Exported `DDHostSwitchPreflightForSlots` in `DuoDashShared.h`.
- Implemented staged checks in compiled `HostFlowAdapter.m`: early snapshot gates, ordered BID equality, size validation of all caller-supplied slots, and observed shell bounds. Preserves separate error flags and refuses to proceed on any failure. Legacy scalar preflight remains available.
- Added explicit self-test cases for valid two-pane slot sizes, too-small second slot, and combined slot-size and shell-bound rejection.
- No new private selector access, UI mutation, or startup self-test invocation.

## Verification
PASS reconstruction verifier (30 modules) and git diff --check. macOS Foundation self-test and Theos arm64 CI not executed here; no commit/push.
