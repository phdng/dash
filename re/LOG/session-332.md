# Session-332 — Whitespace-tolerant complete mode-flags verifier

Continued on `chore/reconstruction-build-ci`, preserving uncommitted sessions 320–331.

## Change
`scripts/verify_reconstruction.py`: replaced brittle literal substring validation for `DDHostSwitchModeFlagsAllow` with whitespace-tolerant structural regex anchored to the function and its complete 208F4:170-206 predicate: `hostMode == 0x0100`, `hostPhase == 2`, and `(stateFlags & 0x101) == 0`. No compiled Objective-C code changed.

## Verification
PASS reconstruction verifier (30 modules), Python py_compile and git diff --check (LF/CRLF warnings only). Theos arm64 CI pending. No commit or push.
