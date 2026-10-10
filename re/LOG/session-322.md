# Session-322 — Pure in-place switch shell-bounds guard

Continued on `chore/reconstruction-build-ci` with uncommitted sessions 320–321 preserved.

## Evidence and boundary
`re/EVIDENCE/hosting_engine.md` §3, `208F4:238-242`: an early switch guard calls 22D64; a positive shell-bounds mismatch causes rejection (return 0). Only the supplied boolean decision is promoted, not 22D64, geometry acquisition, private selectors or switch wiring.

## Implementation
- `HostFlowAdapter.m`: `DDHostSwitchShellBoundsAllow(BOOL shellBoundsMismatch)` returns `!shellBoundsMismatch`.
- `DuoDashShared.h`: exported declaration.
- `scripts/verify_reconstruction.py`: structural regression guard.
- `re/STATE.md`: current status.

## Verification
PASS reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warnings only). Theos arm64 CI remains pending for sessions 320–322. No commit/push.
