# Session-325 — Pure hosted slot size guard

Continued `chore/reconstruction-build-ci` with uncommitted sessions 320–324 preserved.

## Evidence
`re/EVIDENCE/hosting_engine.md` §3, `208F4:207-237`: the in-place CarPlay UI switch compares hosted BID values only in a context with hosted slot size at least 1.0. Extracted only the numeric threshold, not the private size source or BID comparison.

## Change
- `HostFlowAdapter.m`: pure `DDHostSwitchHostedSlotSizeValid(double hostedSlotSize)` returning `hostedSlotSize >= 1.0`.
- `DuoDashShared.h`: exported declaration.
- `scripts/verify_reconstruction.py`: structural regression check.
- `re/STATE.md`: updated current status.

## Verification
PASS reconstruction verifier, Python py_compile and git diff --check (LF/CRLF warnings only). Arm64 Theos CI pending. No automatic commit/push.
