# Session-318 — Pure in-place switch slot count consistency

Continued on `chore/reconstruction-build-ci` with uncommitted session-317 changes preserved; branch ahead of origin 3 commits.

## Evidence
`re/EVIDENCE/hosting_engine.md` §3, 208F4:170–206: hostedSlotCount must be 1..3, equal global runtime count `1639C0`, equal layout-derived `BA7C8` count and no greater than prepared capacity `1639C8`. This is only a subset of many in-place switch conditions.

## Implementation
Added `DDHostSwitchSlotCountsMatch(hostedSlotCount, runtimeSlotCount, layoutSlotCount, preparedSlotCapacity)` to compiled `HostFlowAdapter.m`; exported through `DuoDashShared.h`; verifier regression guard added. All counts are supplied inputs; no private selectors, global reads/writes or switch execution.

## Verification
PASS `python scripts/verify_reconstruction.py`, `python -m py_compile scripts/verify_reconstruction.py`, `git diff --check` (only LF/CRLF warnings). Arm64 Theos CI unconfirmed; no commit/push.
