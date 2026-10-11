# Session-363 — Decompiled 3DD4C lookup-free BID normalization

Continued uncommitted Sessions 361–362 on `chore/reconstruction-build-ci`.

## Direct export evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/3DD4C.c`: a3=0 bypasses SBApplicationController. Loop fills each slot: missing/non-NSString -> empty, repeated nonempty BID -> empty, preserves the first BID, always outputs one entry per slot. a3=1 may additionally invalidate nonexistent SBApplications outside CarPlay UI; intentionally not synthesized.

## Compiled changes
- `DDHostNormalizeBidsWithoutLookup` exported in shared header and compiled in HostFlowAdapter.m; constrained to supported 0..3 slots, caller-supplied arrays only, no private selector or globals.
- Explicit Objective-C self-test assertions cover dedupe, NSNull, nil input, truncation.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. Objective-C executable and Theos arm64 CI unconfirmed. No commit/push.
