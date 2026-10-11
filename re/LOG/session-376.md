# Session-376 — Pure-data vs private-selector normalization parity

Continued on chore/reconstruction-build-ci with uncommitted Session 375.

## Changes
Added macOS Objective-C smoke assertions in `scripts/hostflow_preflight_smoke.m` to compare output of guarded `DDHostNormalizeBidsUsingSpringBoard` to `DDHostNormalizeBidsWithAvailability` with precisely the mock's available BID set and flags. For nil-controller fallback, assert parity with caller-fed nil availability. For absent application selector, assert parity with lookup-free `DDHostNormalizeBidsWithoutLookup`. All changes are to test-only code; no new production hooks or UI mutations.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. No native Objective-C compiler available in Windows workspace, so macOS smoke execution and Theos arm64 build remain unverified. No commit/push.
