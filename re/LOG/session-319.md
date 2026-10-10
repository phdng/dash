# Session-319 — Pure in-place switch interaction-state guard

Continued `chore/reconstruction-build-ci`, preserving the uncommitted session-318 changes.

## Evidence
`re/EVIDENCE/hosting_engine.md` §3, `208F4:170-206` lists early rejections when host is inactive, not split-hosting, not visible, swap in flight, maximizedPosition < 0 or maximize in flight. These checks are individually necessary but not sufficient for in-place switch.

## Implementation
- `HostFlowAdapter.m`: added pure `DDHostSwitchInteractionStateAllows(active,splitHosting,visible,swapInFlight,maximizedPosition,maximizeInFlight)` with corresponding conjunction.
- `DuoDashShared.h`: exported declaration.
- `scripts/verify_reconstruction.py`: structural guard.
- `re/STATE.md`: updated session status.

No private selectors, global reads/writes, scheduling, notifications or live hook installation.

## Verification
PASS: reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warnings only). Arm64 Theos CI pending. No automatic commit/push.
