# Session-380 — macOS arm64 Objective-C link check

Continued uncommitted Session 379 on `chore/reconstruction-build-ci`.

## Changes
- In `.github/workflows/build.yml`, after the two existing macOS arm64 Objective-C `-c` compile commands, link them with `xcrun clang -arch arm64 -fobjc-arc -fblocks -Wall -Wextra -Werror -framework Foundation -framework CoreFoundation` into `$RUNNER_TEMP/hostflow_preflight_smoke_arm64`.
- Validate the resulting architecture with `xcrun lipo -verify_arch arm64`.
- Native host smoke execution, Theos build and device setup unchanged. This is a macOS arm64 link check, not an iOS runtime verification.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. External macOS CI not executed. No commit/push.
