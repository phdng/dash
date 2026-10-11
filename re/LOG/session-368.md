# Session-368 — Guarded live SBApplicationController normalization

Continued Sessions 361–367 uncommitted on chore/reconstruction-build-ci.

## Decompiled source
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/3DD4C.c`: a3=1 optionally gets `SBApplicationController.sharedInstance`; calls `applicationWithBundleIdentifier:` only if selector exists and BID is nonempty and CarPlay UI flag false. Absent controller bypasses the lookup.

## Compiled implementation
- Exported `DDHostNormalizeBidsUsingSpringBoard` in DuoDashShared.h.
- In HostFlowAdapter.m use NSClassFromString, NSSelectorFromString, respondsToSelector, typed objc_msgSend; mirrors ordered BID dedupe, type filtering, per-slot CarPlay flag and application existence checks.
- No automatic startup invocation or private UI mutation. Existing caller-fed normalization remains for unit tests.

## Verification
PASS python scripts/verify_reconstruction.py (30 modules); PASS git diff --check. GH CLI unavailable in workspace; macOS Objective-C compiler test and arm64 CI not run. No commit/push.
