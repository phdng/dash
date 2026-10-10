# Session-315 — Pure delayed host generation guard

Continued after session-314. Working tree started clean on `chore/reconstruction-build-ci` (ahead of origin by one commit); user did not provide a new arm64 CI result.

## Evidence
`re/EVIDENCE/hosting_engine.md` §4, `27AE4:11-13`: the delayed onHosted/reap continuation advances only when the captured generation equals the current host generation. Implemented only the equality decision; no timer, queue, block capture, IPC or reap/kill path.

## Changes
- `HostFlowAdapter.m`: `DDHostDelayedGenerationIsCurrent(uint64_t capturedGeneration, uint64_t currentGeneration)` returns equality.
- `DuoDashShared.h`: public declaration.
- `scripts/verify_reconstruction.py`: structural regression guard.
- `re/STATE.md`: current session/status.

## Verification
PASS: reconstruction verifier, Python py_compile and git diff --check (only LF/CRLF warnings). Arm64 Theos CI for new helper pending; no commit or push by assistant.
