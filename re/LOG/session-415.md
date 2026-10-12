# Session-415 — Portable end-to-end packed dock geometry regression

Continued uncommitted Sessions 411–414 on `chore/reconstruction-build-ci`.

## Changes
Expanded `scripts/test_dock_geometry_vectors.py` with independent `resolve_state` reference logic linking packed decode (83FC), initial region (23D94), edge trim (26654), covered expansion (269FC) and final label synthesis. New test checks packed subrect left-dock covered -> exit-disabled -> dock removed -> dock restored transitions, checking initial and resolved geometry, coverage reason, and final diagnostic label. Also tests invalid-shell fallback with/without measured dock and unusable bounds rejection. Updated module docstring. Corrected previous state header typo.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (4 methods), PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. Not executed: compiled macOS Objective-C smoke, Theos arm64 build and live CarPlay. No commit or push.
