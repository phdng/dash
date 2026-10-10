# Session-331 — Complete full-host and interaction predicate verification

Continued on `chore/reconstruction-build-ci` preserving uncommitted sessions 320–330.

## Change
` scripts/verify_reconstruction.py` now checks all return-expression terms, in order, for `DDHostRequiresFullHost` (seven OR terms, 218D8:307-313) and `DDHostSwitchInteractionStateAllows` (six AND terms, 208F4:170-206). Previous partial substring guards could miss removal of intermediate terms. No compiled Objective-C code changed.

## Verification
PASS reconstruction verifier (30 modules), Python py_compile and git diff --check (LF/CRLF warnings only). Arm64 Theos CI unconfirmed. No commit/push.
