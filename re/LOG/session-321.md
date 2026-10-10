# Session-321 — Pure post-switch continuation state guard

Continued with uncommitted session-320 changes preserved on `chore/reconstruction-build-ci`.

## Evidence and boundary
`re/EVIDENCE/hosting_engine.md` §3, `26FE4:81-260` records the post-switch continuation requires active, split-hosting, visible and CarPlay-connected states. Extracted only these four boolean gates. Other 7764C check, controller access, pane mutation, evict, geometry push and IPC remain excluded.

## Implementation
- `HostFlowAdapter.m`: pure `DDHostSwitchContinuationStateAllows(active, splitHosting, visible, carPlayConnected)`.
- `DuoDashShared.h`: exported declaration.
- `scripts/verify_reconstruction.py`: structural guard.
- `re/STATE.md`: session/status update.

## Verification
PASS reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warnings only). Theos arm64 CI pending. No commit/push.
