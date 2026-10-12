# Session-423 — Reconcile desired dock geometry with observed hosted bounds

Date: 2026-10-12. Continued from Session-422 after user confirmed preceding build green. Branch `chore/reconstruction-build-ci` was clean at start. No commit/push.

## Why
Session-422 computed layout/hosting actions by comparing two caller-supplied CarPlay snapshots. It could incorrectly recommend `no-change` when those snapshots match but the actual hosted frame is stale, and could recommend `restore-layout` or `update-layout` when the desired new rectangle was already applied. The documented original `sub_9D64` B07/B08 fast/already paths compare the stored host rectangle using `CGRectEqualToRect` (re/RECONSTRUCTION/functions/9D64.md), so observed frame comparison is relevant. This remains an advisory data-only approximation, not a copy of a full private host lifecycle.

## Changes
- `re/RECONSTRUCTION/DuoDashShared.h`: exported `DDHostDockHostingPlanForObservedBounds(previous,next,lifecycle,hostedBoundsPresent,hostedBounds,...)`.
- `re/RECONSTRUCTION/HostFlowAdapter.m`: composes the existing 83FC/23D94/26654/269FC snapshot planner with the externally observed host CGRect. Rejects invalid *present* hosted geometry without writing outputs. If no trusted hosted frame, requests `full-host-required`. With frame already equal to destination, returns `no-change` or `diagnostic-only` regardless of prior calculated relayout/restore; if divergent, respects existing `DDHostRequiresFullHost` guard then returns `restore-layout` or `update-layout`. Publishes before/after rect and diagnostics only on success. No notification reads/private runtime calls/host UI mutations.
- `scripts/hostflow_preflight_smoke.m`: native smoke matrix covering stale frame despite unchanged dock state, dock removal/restoration, destination already applied, unchanged healthy host, missing hosted frame, dirty lifecycle full-host fallback, invalid hosted negative width, and malformed next snapshot with atomic output preservation.
- `scripts/test_dock_geometry_vectors.py`: independent `hosting_plan_for_observed_bounds` oracle plus regression matrix for stale frame, restoration, applied target, idempotence, missing host, dirty lifecycle, invalid NaN/negative/zero rectangles and invalid snapshots.
- `scripts/verify_reconstruction.py`: export registry updated.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py`: 10 methods. PASS `python scripts/verify_reconstruction.py`: 30 synthesis modules. PASS `git diff --check`. Native macOS compiled smoke, Theos arm64 CI and physical CarPlay remain unverified for Session-423, notwithstanding user's confirmation of previous build. Do not claim native green until rerun. No commit/push.
