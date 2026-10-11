# Session-367 — 3DD4C conditional application validation and duplicate order

Continued uncommitted Sessions 361–366 on `chore/reconstruction-build-ci`.

## Evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/3DD4C.c:62–94` checks whether a nonempty BID has appeared in the **already-normalized output**, optionally resolves application existence, then appends the resulting BID. Thus if first occurrence is rejected as unavailable, a later identical BID can survive when CarPlay UI exempts it from lookup.

## Compiled regression tests
- First occurrence rejected as unavailable, second identical BID accepted as CarPlay UI -> `[@"", @"a"]`.
- First occurrence accepted as CarPlay UI, second identical BID -> `[@"a", @""]`.
- Both occurrences unavailable and non-CarPlay UI -> both empty.
- Existing implementation already matches this ordering; no speculative private hooks or UI mutation were introduced.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `git diff --check`. Objective-C executable test and arm64 Theos CI remain unconfirmed. No commit/push.
