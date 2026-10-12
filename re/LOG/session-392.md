# Session-392 — Packed dock state/direct rectangle parity

Continued Sessions 390–391 on `chore/reconstruction-build-ci`.

## Implementation
Extended `scripts/hostflow_preflight_smoke.m` with regression assertions for packed right, top and bottom dock states, comparing `DDHostTrimUsableBoundsForDockState` output to `DDHostTrimUsableBoundsForDock` using the exact decoded dock CGRect. Added rejection test for a centered vertical dock ensuring caller output remains unchanged. Uses C CGRect arrays rather than platform-specific NSValue rectangle methods to keep macOS Foundation-only smoke portable. No production code changed, private notification reads or UI hosting operations added.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python -m py_compile scripts/verify_reconstruction.py`, PASS `git diff --check`. Native compiled Objective-C, arm64 Theos and CarPlay device remain unverified. No commit/push.
