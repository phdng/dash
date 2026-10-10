# Session-338 — Pure helper body termination checks

Continued on `chore/reconstruction-build-ci`, preserving uncommitted Sessions 335–337.

## Changes
- `scripts/verify_reconstruction.py`: require closing `}` immediately after `return bid ?: @"";` in `DDHostSplitBidOrEmpty`, and after `return hostedSlotSize >= 1.0;` in `DDHostSwitchHostedSlotSizeValid`. Allows whitespace but rejects extra post-return source statements in these two pure helpers.
- No Objective-C runtime or private hook changes.

## Verification
PASS reconstruction verifier (30 modules), Python py_compile and git diff --check (LF/CRLF warnings only). Arm64 Theos CI pending. No commit or push.
