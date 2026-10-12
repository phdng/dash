# Session-419 — Dock layout transition decision through complete CarPlay pipeline

Continued uncommitted Sessions 411–418 on `chore/reconstruction-build-ci`. User expects groups of related paths per session, not isolated selectors.

## Context and implementation
- Current packed-state adapter resolved only one snapshot; hosting callers had no explicit way to decide whether the next dock notification needs relayout, can skip geometry, or restores usable bounds.
- Exported and implemented `DDHostDockLayoutTransition` in DuoDashShared.h / HostFlowAdapter.m. It evaluates both states using the complete 83FC -> 23D94 -> 26654 -> 269FC packed decode/initial geometry/dock trim/coverage/final diagnostic path and compares `CGRectEqualToRect`/final reason.
- Returns `unchanged` when rectangle and reason are identical, `reason-only` when only the final reason changes, `updated` for different resolved geometry, `restored` for changed geometry after measured dock becomes absent/invalid, and `invalid-geometry` on failure without writing any caller outputs.
- Does not register notifications, mutate hosting, or manage a persistent cache; it is a pure-data gating helper for future safe integration.
- Extended Objective-C smoke with no-op, removal/restoration, republish, exit flag coverage, reason-only, and output-preserving invalid cases.
- Extended portable Python `test_dock_geometry_vectors.py` with independent `layout_transition` reference and test method; registered export in verifier.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (7 tests), PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check` (Windows CRLF warnings only). No compiled macOS Objective-C smoke or Theos arm64 build run here; CarPlay device integration unverified. No commit/push.
