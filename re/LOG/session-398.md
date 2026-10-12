# Session-398 — 269FC covered geometry tolerance regression

Continued uncommitted Sessions 390–397 on `chore/reconstruction-build-ci`.

## Change
Expanded `scripts/hostflow_preflight_smoke.m` with boundary cases for the 269FC covered dock path: accepted adjacent dock at exactly 2pt; rejection at 2.1pt; accepted covered geometry at the 1pt expanded usable-bounds edge and unchanged caller output on rejection. No production code or private UI operations changed.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `git diff --check`. Native macOS Objective-C smoke, Theos arm64 and physical CarPlay remain unverified. No commit/push.
