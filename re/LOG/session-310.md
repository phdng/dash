# Session-310 — Green CI follow-up and pane corner radius

User confirmed Theos arm64 build green after session-309 linker collision repair. Workspace branch `chore/reconstruction-build-ci` started clean.

## Scope / evidence
`re/EVIDENCE/hosting_engine.md` documents 218D8:416-420: `/var/tmp/duodash_ab_nopaneround` marker selects pane corner radius 0.0 when present and 13.0 otherwise. Promote only this pure decision; no file acquisition, UI mutation or globals. Leave `paneratio` fallback unresolved.

## Changes
- `DuoDashShared.h`: export `DDPaneCornerRadiusForNoRoundMarker(BOOL markerPresent)`.
- `ToggleValueHelpers.m`: implement 0.0 / 13.0 mapping.
- `scripts/verify_reconstruction.py`: assert source contracts.
- `re/STATE.md`: update status from old session-303 repair to user-confirmed green CI and session-310 scope.

## Verification
PASS: `python scripts/verify_reconstruction.py`, `python -m py_compile scripts/verify_reconstruction.py`, `git diff --check` (only LF/CRLF warnings). Exact arm64 CI for session-310 change remains pending; no push.
