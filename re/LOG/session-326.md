# Session-326 — Host-flow public export regression checks

Continued on `chore/reconstruction-build-ci` with uncommitted Sessions 320–325 preserved.

## Changes
`scripts/verify_reconstruction.py` now checks that all 13 promoted host-flow helpers from sessions 313–325 still have matching `FOUNDATION_EXPORT` declarations in `DuoDashShared.h`. Earlier verifier guards already check their implementations; this covers inadvertent header drift. No compiled Objective-C code changed in Session 326.

## Verification
Initial new regex incorrectly double-escaped its character classes and failed in Python; corrected immediately before concluding. PASS on rerun: `python scripts/verify_reconstruction.py` (30 modules), `python -m py_compile scripts/verify_reconstruction.py`, and `git diff --check` (only LF/CRLF warnings). Arm64 Theos CI for outstanding sessions remains pending. No commit/push.
