# Session-316 — In-place switch slot-count guard

Workspace `chore/reconstruction-build-ci` started with uncommitted session-315 changes; preserve them. Last explicitly user-confirmed Theos CI green through session-312.

## Evidence and scope
`re/EVIDENCE/hosting_engine.md` §3 (208F4:170-206) lists `hostedSlotCount(1..3)` among mandatory early guards for `switchCarPlayUIInPlace:gen:`. Promote only this numeric validity condition as an independent pure decision: `DDHostSwitchSlotCountIsValid(NSInteger)` returns YES for 1,2,3 and NO outside. This is NOT a sufficient condition for authorizing switch; other state/slot/global guards remain untouched and unimplemented.

## Changes
- `HostFlowAdapter.m`: add exported pure guard.
- `DuoDashShared.h`: declare guard.
- `scripts/verify_reconstruction.py`: structural regression assertion.
- `re/STATE.md`: update status and retain note about session-315 uncommitted changes.

## Verification
PASS reconstruction verifier, Python py_compile, git diff --check (only LF/CRLF warnings). Arm64 Theos CI pending. No commit/push.
