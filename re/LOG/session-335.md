# Session-335 — Generation equality and slot count regression checks

At session start Git was clean on branch `chore/reconstruction-build-ci`, HEAD `750902c` (`uppp`); previous sessions 320–334 were already committed externally. No arm64 Theos CI result was verified.

## Change
`scripts/verify_reconstruction.py` now checks complete, whitespace-tolerant function-scoped expressions for `DDHostDelayedGenerationIsCurrent` (`capturedGeneration == currentGeneration`) and `DDHostSwitchSlotCountIsValid` (`hostedSlotCount >= 1 && hostedSlotCount <= 3`). No Objective-C runtime code changed.

## Verification
PASS reconstruction verifier (30 modules), Python py_compile, git diff --check (LF/CRLF warning only). Theos arm64 CI unconfirmed. No commit/push from assistant.
