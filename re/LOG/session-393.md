# Session-393 — Direct dock trim boundary smoke

Continued Sessions 390–392 on `chore/reconstruction-build-ci`.

## Change
Expanded `scripts/hostflow_preflight_smoke.m` with 26654 direct clipping assertions for overhanging dock beyond left usable boundary, dock starting at exactly 2pt from edge, residual width exactly 40pt accepted, residual width 39.9pt rejected with unchanged output. These test `DDHostTrimUsableBoundsForDock`, complementing preceding classifier and packed-state smoke. No new private calls or UI mutation.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. macOS compiled Objective-C smoke, Theos arm64 CI and real CarPlay remain unverified. No commit/push.
