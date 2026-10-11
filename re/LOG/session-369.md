# Session-369 — Compiled runtime mock coverage for private 3DD4C lookup

Continued uncommitted sessions 361–368 on `chore/reconstruction-build-ci`.

## Objective-C test harness
- Extended `scripts/hostflow_preflight_smoke.m` with a local test-only `SBApplicationController` mock exposing `sharedInstance` and `applicationWithBundleIdentifier:` matching selectors recovered from decoded `3DD4C.c`.
- Smoke main calls compiled `DDHostNormalizeBidsUsingSpringBoard` with four slots and asserts that unknown app becomes empty, a CarPlay UI exempt repeated unknown BID remains, installed mock app is accepted, and a later duplicate is cleared.
- Mock is compiled only in macOS test executable and not in Theos tweak target; no production private host call is auto-invoked.
- Existing `.github/workflows/build.yml` already builds and executes the smoke executable with `-Wall -Wextra -Werror` before Theos build.

## Checks
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. macOS runner not available locally, Objective-C test not executed, arm64 CI status unconfirmed. No commit/push.
