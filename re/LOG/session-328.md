# Session-328 — Host-flow export and nullability verifier hardening

Continued on `chore/reconstruction-build-ci`, preserving uncommitted sessions 320–327.

## Changes
- `scripts/verify_reconstruction.py`: extend one-to-one `FOUNDATION_EXPORT`/compiled definition counts from 13 to 14 host-flow helpers by including `DDHostRequiresFullHost`.
- Enforce exact nullable input and nonnull output declaration for `DDHostSplitBidOrEmpty(NSString * _Nullable bid)` to catch future nullability regressions.
- No Objective-C changes this session, no private selectors or hook wiring.

## Verification
PASS: `python scripts/verify_reconstruction.py` (30 synthesis modules), `python -m py_compile scripts/verify_reconstruction.py`, and `git diff --check` (LF/CRLF warnings only). Arm64 Theos CI not run. No commit/push.
