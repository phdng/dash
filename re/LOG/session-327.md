# Session-327 — Host-flow one-to-one export/definition verifier

Continued on `chore/reconstruction-build-ci`, preserving uncommitted sessions 320–326.

## Change
Updated `scripts/verify_reconstruction.py` so each of 13 evidence-backed host-flow helpers from sessions 313–325 must have exactly one `FOUNDATION_EXPORT` declaration in `DuoDashShared.h` and exactly one function definition in compiled `HostFlowAdapter.m`. Handles both `BOOL` and `NSString *` return spellings. This is structural regression hardening only, with no change to compiled Objective-C code or runtime behavior.

## Verification
The initial stricter regex rejected the valid unspaced `NSString *Function` spelling; fixed and reran all checks. Final PASS: reconstruction verifier (30 modules), Python py_compile, git diff --check (LF/CRLF warnings only). Arm64 CI not run; no commit/push.
