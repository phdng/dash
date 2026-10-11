# Session-379 — arm64 Objective-C object compilation CI

Started with clean `chore/reconstruction-build-ci` working tree; Session 378 already present in current HEAD.

## Change
In `.github/workflows/build.yml`, replace macOS `xcrun clang -arch arm64 -fsyntax-only` check with separate `-arch arm64 -c -fobjc-arc -fblocks -Wall -Wextra -Werror` compilations generating `$RUNNER_TEMP/HostFlowAdapter_arm64.o` and `$RUNNER_TEMP/hostflow_preflight_smoke_arm64.o`. Keeps native compiled-and-executed smoke and later Theos arm64 build. Object generation extends coverage beyond syntax-only but does not link or execute arm64 host binary and is not an iOS device validation.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`; external macOS CI and arm64 Theos results unconfirmed. No commit/push.
