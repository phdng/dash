# Session-414 — Portable packed dock decode, clipping and restore regression

Continued uncommitted Sessions 411–413 on `chore/reconstruction-build-ci`.

## Changes
Extended CI-invoked `scripts/test_dock_geometry_vectors.py` with standalone `decode_dock` for 83FC tenth-point fields and `trim_edge` geometry oracle for 26654 four-edge clipping; added Python unittest for left/right/top/bottom packed-state vectors, absent/invalid state, non-edge dock and left dock -> absent -> left dock restoration. Retained existing 269FC coverage vectors. This is an independent Python reference check, not compiled Objective-C.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (3 tests), PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. macOS Objective-C smoke, arm64 Theos and device testing not executed here. No commit/push.
