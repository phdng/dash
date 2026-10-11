# Session-375 — Pre-private API validation smoke checks

Continued Sessions 361–374 uncommitted on chore/reconstruction-build-ci.

## Changes
- Extended test-only `scripts/hostflow_preflight_smoke.m` to assert `DDHostPreparedRequestReadyUsingSpringBoard` refuses malformed requested BID type, malformed CarPlay UI flags type and invalid zero active slot count, without calling the mock private application lookup.
- Kept the existing runtime adapter, CI workflow and all prior mock success/fallback tests unchanged.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `python -m py_compile scripts/verify_reconstruction.py` and `git diff --check`. Windows environment lacks native macOS Objective-C and arm64 build tools; CI execution remains unconfirmed. No commit/push.
