# Session-370 — Nil private controller fallback mock

Continued uncommitted Sessions 361–369 on chore/reconstruction-build-ci.

## Evidence and test
Decoded `DuoDash.dylib_export_for_ai/decompile/3DD4C.c` skips the optional applicationWithBundleIdentifier lookup when controller is unavailable, but retains per-slot BID normalization and deduplication. Extended test-only SBApplicationController mock in `scripts/hostflow_preflight_smoke.m` with a toggle returning nil from sharedInstance. Added runtime assertion for two repeated unknown BIDs plus NSNull, expecting first unknown to survive and duplicate/NSNull to become empty. The existing macOS Actions smoke command compiles this harness before Theos build.

## Verification
PASS local `python scripts/verify_reconstruction.py` (30 modules), PASS git diff --check. Objective-C macOS runner and arm64 CI not executed locally. No commit or push.
