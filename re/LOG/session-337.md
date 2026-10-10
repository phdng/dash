# Session-337 — Nil BID coalescing full-expression verifier

Continued on `chore/reconstruction-build-ci` preserving uncommitted Sessions 335–336.

## Change
`scripts/verify_reconstruction.py` now verifies the full `DDHostSplitBidOrEmpty(NSString * _Nullable bid)` declaration shape in compiled `HostFlowAdapter.m` and the exact `return bid ?: @""` coalescing semantics while tolerating formatting whitespace. Existing header nullability check remains. No Objective-C runtime changes.

## Verification
PASS reconstruction verifier (30 modules), Python py_compile and `git diff --check` (LF/CRLF warnings only). Theos arm64 CI unconfirmed; no commit or push.
