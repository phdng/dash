# Session-329 — Host-flow return-type verification

Continued on `chore/reconstruction-build-ci`, preserving uncommitted Sessions 320–328.

## Changes
- `scripts/verify_reconstruction.py`: require exact return type for every one of the 14 promoted host-flow helpers in both `DuoDashShared.h` declarations and `HostFlowAdapter.m` definitions. `DDHostSplitBidOrEmpty` uses NSString * (nonnull header), the remaining 13 use BOOL.
- Existing count=1 checks and BID input/output nullability check remain intact.
- No Objective-C source or runtime behavior changed this session.

## Verification
PASS reconstruction verifier (30 modules), Python py_compile and git diff --check (LF/CRLF warnings only). Arm64 Theos CI remains unconfirmed. No commit/push.
