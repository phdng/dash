# Session-314 — Pure degenerate-content geometry predicate

Continued bounded reconstruction from session-313. Branch `chore/reconstruction-build-ci` started clean; no new CI confirmation was provided in this turn.

## Evidence and implementation
`re/EVIDENCE/hosting_engine.md`, `218D8:338-352` records refusal when computed content width or height is below 1.0. Added `DDHostHasDegenerateContent(double width, double height)` in already compiled `HostFlowAdapter.m`, returning `width < 1.0 || height < 1.0`. Exported via `DuoDashShared.h`, with structural verifier guard.

No geometry acquisition, DDz selectors, notification, mutation or new host routing is performed. `paneratio` remains blocked by unresolved fallback metadata.

## Verification
PASS: `python scripts/verify_reconstruction.py`, `python -m py_compile scripts/verify_reconstruction.py`, `git diff --check` (only LF/CRLF warnings). Theos arm64 CI for new code remains pending; no commit/push.
