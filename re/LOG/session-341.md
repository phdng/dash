# Session-341 — Host guard body termination

Continued on `chore/reconstruction-build-ci`, retaining uncommitted Sessions 335–340.

## Changes
- `scripts/verify_reconstruction.py`: require closing braces immediately after returns for `DDHostRequiresFullHost`, `DDHostShouldRefuseNoDisplay`, `DDHostHasDegenerateContent` and `DDHostSwitchModeFlagsAllow`. This rejects extra post-return statements while preserving whitespace-tolerant matching.
- No Objective-C runtime/private-hook changes.

## Verification
PASS reconstruction verifier (30 synthesis modules), Python py_compile and `git diff --check` (LF/CRLF warnings only). Arm64 Theos CI unconfirmed. No commit/push.
