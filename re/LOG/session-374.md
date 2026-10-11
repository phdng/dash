# Session-374 — Missing private selector fallback smoke

Continued Sessions 361–373 uncommitted on `chore/reconstruction-build-ci`.

## Direct decoded contract
`DuoDash.dylib_export_for_ai/decompile/3DD4C.c`: if shared SBApplicationController does not respond to `applicationWithBundleIdentifier:`, treat controller as nil and skip application lookup while retaining normalization and deduplication.

## Changes
- Test-only `scripts/hostflow_preflight_smoke.m` mock supports a nonnil shared instance without the application selector, via plain NSObject.
- Tests verify no private lookup is performed, duplicate BID handling remains correct, and guarded prepared-request composition proceeds with the selector-unavailable fallback.
- Production Objective-C private adapter and startup behavior unchanged.

## Verification
PASS reconstruction verifier (30 modules), git diff --check. Windows workspace lacks clang, xcrun, make; macOS compiled Objective-C and Theos arm64 CI not verified. No commit/push.
