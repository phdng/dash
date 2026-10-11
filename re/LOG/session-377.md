# Session-377 — CarPlay UI-only private lookup bypass smoke

Continued on `chore/reconstruction-build-ci` with uncommitted Sessions 375–376.

## Changes
- Extended `scripts/hostflow_preflight_smoke.m` with a CarPlay UI-only mock case: nonempty CarPlay UI BID accepted; its duplicate and empty slot normalized to empty; zero calls to `SBApplicationController.applicationWithBundleIdentifier:` despite live mock controller.
- Cross-checked output against `DDHostNormalizeBidsWithAvailability` with a nonnil empty available BID set. This asserts 3DD4C per-slot CarPlay bypass and deduplication precedence without adding production hooks.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. macOS compiled Objective-C smoke and Theos arm64 CI not executed locally. No commit/push.
