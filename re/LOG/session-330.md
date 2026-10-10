# Session-330 — Complete host-flow guard predicate verification

Continued on `chore/reconstruction-build-ci`, preserving uncommitted sessions 320–329.

## Change
In `scripts/verify_reconstruction.py`, replaced partial substring checks for `DDHostSwitchSlotCountsMatch` and `DDHostSwitchConsistencyAllows` with whitespace-tolerant structural regex checks that cover every term of their return conjunctions. Previously a middle condition could be deleted without triggering these checks. No compiled Objective-C code or runtime behavior changed.

## Verification
PASS: `python scripts/verify_reconstruction.py` (30 modules), `python -m py_compile scripts/verify_reconstruction.py`, and `git diff --check` (LF/CRLF warnings only). Arm64 Theos CI unconfirmed. No commit/push.
