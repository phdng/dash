# Session-339 — Shell-bounds and continuation body termination

On `chore/reconstruction-build-ci`, retained uncommitted Sessions 335–338.

## Change
`scripts/verify_reconstruction.py` now requires the function closing brace directly after the return statement in `DDHostSwitchShellBoundsAllow` and `DDHostSwitchNeedsDelayedContinuation`. It permits whitespace but catches accidental trailing statements in these pure route predicates. No Objective-C changes.

## Checks
PASS: reconstruction verifier (30 synthesis modules), Python py_compile and `git diff --check` (LF/CRLF warnings only). Arm64 Theos CI not verified. No commit/push.
