# Session-336 — Complete shell-bounds and delayed-continuation guards

Continued on `chore/reconstruction-build-ci`, retaining uncommitted Session-335 edits; HEAD remains 750902c unless externally updated.

## Changes
- `scripts/verify_reconstruction.py` now checks function-scoped, whitespace-tolerant complete predicates for `DDHostSwitchShellBoundsAllow` (`!shellBoundsMismatch`, 208F4:238-242) and `DDHostSwitchNeedsDelayedContinuation` (`pendingBidCount != 0`, 208F4:574-584).
- No compiled Objective-C runtime logic or private hooks changed.

## Verification
PASS reconstruction verifier (30 synthesis modules), Python py_compile and `git diff --check` (LF/CRLF warnings only). Arm64 Theos CI unconfirmed. No commit/push.
