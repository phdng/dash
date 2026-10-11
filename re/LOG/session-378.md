# Session-378 — macOS arm64 Objective-C syntax guard in CI

Branch `chore/reconstruction-build-ci`, clean baseline at `80d3904` before edits.

## Change
- Added a separate `.github/workflows/build.yml` step invoking `xcrun clang -arch arm64 -fsyntax-only -fobjc-arc -fblocks -Wall -Wextra -Werror` on `HostFlowAdapter.m` and test-only `hostflow_preflight_smoke.m`.
- Kept existing native-host compiled-and-executed smoke step and later Theos build unchanged. This extra check is macOS arm64 syntax only, not an iOS arm64 binary or device verification.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. GitHub Actions not executed here. No commit/push.
