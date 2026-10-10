# Session-334 — No-display and degenerate geometry predicate checks

Continued on `chore/reconstruction-build-ci`, preserving uncommitted Sessions 320–333.

## Changes
- `scripts/verify_reconstruction.py`: replace brittle exact-string checks for `DDHostShouldRefuseNoDisplay` and `DDHostHasDegenerateContent` with whitespace-tolerant function-scoped regex checks for their full boolean expressions from 218D8:315-327 and 218D8:338-352.
- No Objective-C source/runtime behavior changed.

## Verification
PASS reconstruction verifier (30 synthesis modules), Python py_compile and `git diff --check` (LF/CRLF warnings only). Theos arm64 CI pending. No commit/push.
