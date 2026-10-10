# Session-340 — Delayed generation and slot count body termination

Continued on `chore/reconstruction-build-ci`, retaining uncommitted Sessions 335–339.

## Changes
- `scripts/verify_reconstruction.py`: require closing brace immediately after the verified return expression in `DDHostDelayedGenerationIsCurrent` and `DDHostSwitchSlotCountIsValid`, permitting whitespace but disallowing extra statements after return.
- No Objective-C runtime or private-hook changes.

## Verification
PASS reconstruction verifier (30 synthesis modules), Python py_compile and `git diff --check` (LF/CRLF warnings only). Theos arm64 CI unconfirmed. No commit/push.
