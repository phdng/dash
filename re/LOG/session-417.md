# Session-417 — Nonfinite geometry and fallback parity regression

Continued uncommitted Sessions 411–416 on `chore/reconstruction-build-ci`.

## Changes
- `scripts/test_dock_geometry_vectors.py`: added finite/positive rectangle validation in reference geometry paths; tested `NaN`, infinity, negative width and zero height; nonfinite shell fallback via measured dock; malformed coverage rectangle classified `no-window`.
- `scripts/hostflow_preflight_smoke.m`: added native Objective-C assertions for nonfinite usable bounds returning `invalid-geometry` without mutating output CGRect/reason, and nonfinite shell falling back to valid usable bounds for measured-dock-nofrome.
- No production changes; runtime CarPlay safety still subject to live validation.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (6 tests), PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. Native macOS compiled smoke, Theos arm64 and actual CarPlay not run. No commit/push.
