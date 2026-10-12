# Session-412 — Packed dock update and recovery regression matrix

Continued Session-411 on `chore/reconstruction-build-ci`; user prefers completing related flows per iteration rather than one selector at a time.

## Changes
Extended `scripts/hostflow_preflight_smoke.m` end-to-end 83FC->23D94->26654->269FC packed-state coverage to exercise a right dock, top dock, bottom dock, loss of dock state (restore full usable CarPlay bounds), then left dock restoration (trim again). Tests compare source-derived reason, initial and resolved rectangles through repeated updates. Prior tests already cover initial left dock, malformed state and invalid usable bounds.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 methods), PASS `git diff --check`. Objective-C smoke compiled execution, Theos arm64 and device testing remain unverified here. No commit/push.
