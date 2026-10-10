# Session-347 — Objective-C slot-ordered hosted BID comparison

Continued on `chore/reconstruction-build-ci` preserving uncommitted Session-346 changes.

## Compiled-source changes
- `DuoDashShared.h`: exported `DDHostSwitchBidsMatch` for caller-supplied requested and hosted BID arrays and expected slot count.
- `HostFlowAdapter.m`: validate count 1..3, both arrays have exactly that count, each corresponding element is NSString and direct `isEqualToString:` compares equal.
- This models only the evidenced per-index equality gate (208F4:207-237); private 3DD4C normalization, geometric size reading, shell check, switch mutations and hook integration remain excluded.

## Verification
PASS reconstruction verifier (30 modules) and `git diff --check` (line-ending warnings only). Theos arm64 CI unconfirmed. No commit/push.
