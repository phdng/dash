# Session-390 — Dock edge finite-input guard and original boundary cases

Started on a clean `chore/reconstruction-build-ci` working tree; Sessions 385–389 already in HEAD.

## Changes
- `DDHostDockEdgeLabel` rejects nonfinite origins or dimensions before CoreGraphics intersection, returning `not-an-edge-strip`. This is a defensive caller-data safety addition, not an undocumented original check.
- Extended `hostflow_preflight_smoke.m` with original 26654 boundary cases: dock partially beyond usable area; left edge origin at +2pt tolerance; residual 40pt accepted and 39.9pt degenerate; NaN origin and infinite width rejected.
- No private selectors, host UI changes, or device operations.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 synthesis modules), PASS `python -m py_compile scripts/verify_reconstruction.py`, PASS `git diff --check`. Compiled macOS Objective-C smoke and arm64 Theos CI unverified. No commit/push.
