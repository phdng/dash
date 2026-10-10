# Session-350 — CI executes Objective-C preflight smoke tests

Continued from uncommitted Sessions 346–349 on `chore/reconstruction-build-ci`.

## Functional verification wiring
- Added `scripts/hostflow_preflight_smoke.m` as a standalone macOS Foundation executable entrypoint that calls the compiled `DDHostSwitchPreflightSelfTest()`; unrelated recovery dependency functions are aborting link-only stubs.
- Updated `.github/workflows/build.yml` to compile/link `HostFlowAdapter.m` and the test entrypoint using `xcrun clang` and run the executable BEFORE installing Theos/building the tweak.
- Updated workflow push/PR path filters so smoke test edits trigger CI.
- Test executable is NOT part of the tweak Makefile and cannot be invoked at startup.

## Verification
Local PASS: `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check` (line ending warnings only). No local macOS Objective-C compiler; macOS executable and Theos arm64 CI NOT YET EXECUTED/CONFIRMED. No commit/push.
