# Session-323 — Pure delayed-continuation routing decision

Continued on `chore/reconstruction-build-ci` while preserving uncommitted sessions 320–322.

## Evidence
`re/EVIDENCE/hosting_engine.md` §3, `208F4:574-584`: after composing the pending BID list, a nonzero count selects the delayed continuation/scheduling path, otherwise the continuation is invoked directly. Timer duration and callback execution are intentionally not reconstructed here.

## Implementation
- `HostFlowAdapter.m`: pure `DDHostSwitchNeedsDelayedContinuation(NSUInteger pendingBidCount)` returns `pendingBidCount != 0`.
- `DuoDashShared.h`: exported declaration.
- `scripts/verify_reconstruction.py`: structural regression assertion.
- `re/STATE.md`: session status.

## Verification
PASS reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warnings only). No arm64 Theos build executed; changes not committed or pushed.
