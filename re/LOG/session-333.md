# Session-333 — Continuation-state and slot-size regression checks

Continued on `chore/reconstruction-build-ci`, preserving uncommitted sessions 320–332.

## Changes
- `scripts/verify_reconstruction.py`: replace brittle literal substring checks for `DDHostSwitchContinuationStateAllows` and `DDHostSwitchHostedSlotSizeValid` with whitespace-tolerant function-scoped expressions validating all continuation terms and the >= 1.0 slot-size threshold.
- No Objective-C code or private hook wiring changed.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `python -m py_compile scripts/verify_reconstruction.py`, and `git diff --check` (LF/CRLF warnings only). Arm64 Theos CI pending. No commit/push.
