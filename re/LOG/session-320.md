# Session-320 — Pure switch generation/geometry/layout consistency guard

Workspace `chore/reconstruction-build-ci` started clean, tracking origin with no ahead commits.

## Evidence
`re/EVIDENCE/hosting_engine.md` §3, `208F4:170-206`: in-place switch rejects pending generation `163978 != 0`, geometry mismatch `1639B8 != 1639BC`, and layout mismatch `162E90 != 73E8()`. This session extracts only equality predicates from those observed gates. Exact private acquisition and switch execution remain excluded.

## Implementation
- `HostFlowAdapter.m`: pure `DDHostSwitchConsistencyAllows(pendingGeneration, requestedGeometryVersion, appliedGeometryVersion, activeLayout, preferredLayout)`.
- `DuoDashShared.h`: exported declaration.
- `scripts/verify_reconstruction.py`: regression guard.
- `re/STATE.md`: session/status update.

## Verification
PASS reconstruction verifier, Python py_compile and git diff --check (LF/CRLF warnings only). Theos arm64 CI for session-320 pending. No commit or push.
