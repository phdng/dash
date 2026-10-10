# Session-346 — Two-pane host input array (Objective-C)

Started with a clean tree on `chore/reconstruction-build-ci` (branch ahead of origin by one commit).

## Compiled source changes
- `DuoDashShared.h`: declare `NSArray<NSString *> *DDHostSplitBids(NSString * _Nullable leftBid, NSString * _Nullable rightBid)`.
- `HostFlowAdapter.m`: return an ordered two-element array of `DDHostSplitBidOrEmpty(leftBid)` and `DDHostSplitBidOrEmpty(rightBid)`, matching static 217EC:26-37.
- No private `hostSlots:skipEvict:onHosted:` call, no live CarPlay pane mutation. This only prepares input.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `git diff --check` (line-ending warnings only). Arm64 Theos CI not confirmed. No commit/push.
