# Session-381 — Structural guards for macOS arm64 compile/link CI

Continued uncommitted Sessions 379–380 on `chore/reconstruction-build-ci`.

## Change
Extended `scripts/verify_reconstruction.py` to assert `.github/workflows/build.yml` still compiles both HostFlowAdapter and test-only smoke harness into macOS arm64 object files, links them with Foundation/CoreFoundation, checks architecture with `lipo -verify_arch arm64`, and invokes Theos `make clean all`. Requires exactly two arm64 `-c` commands, guarding against silent reduction to `-fsyntax-only`.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. This is structural CI configuration verification, not macOS runtime/link execution. No commit/push.
