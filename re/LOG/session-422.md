# Session-422 — Compose dock geometry transition with hosting lifecycle decisions

User confirmed the Session-421 build is green; started from clean `chore/reconstruction-build-ci`. User requests continued implementation of multiple related pathways per session. No commit/push.

## Changes
- `DuoDashShared.h`: added caller-fed `DDHostCarPlayLayoutSnapshot` and `DDHostHostingLifecycleSnapshot` structs; declared `DDHostDockHostingPlanForSnapshots` as a pure-data, advisory host decision interface.
- `HostFlowAdapter.m`: combined previous/next 83FC/23D94/26654/269FC dock geometry via `DDHostDockLayoutTransitionForSnapshots` with the existing 218D8 `DDHostRequiresFullHost` fallback predicate. Distinguishes `invalid-geometry`, `no-change`, `diagnostic-only`, `full-host-required`, `restore-layout`, `update-layout`. Geometry-unchanged events cannot start relayout solely due to dirty/active flags; geometry-changing events defer to full-host when existing guard says so. Invalid geometry does not write outputs. No private selector calls or UI mutations.
- `scripts/hostflow_preflight_smoke.m`: added native decision-matrix smoke tests for unchanged, dock loss/restoration, republish/update, reason-only despite dirty lifecycle, dirty/inactive/geometry-mismatch full-host fallback, shell motion and invalid output preservation.
- `scripts/test_dock_geometry_vectors.py`: independent `hosting_plan_for_snapshots` oracle and test including seven full-host flag branches, no-change and no-op under fallback flags, dock restore/update, shell motion, reason-only and malformed geometry.
- `scripts/verify_reconstruction.py`: registered the new exported helper.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (9 tests); PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `git diff --check`. User-confirmed prior Session-421 macOS build green; current Session-422 Objective-C/macOS CI and Theos arm64 have not been run here, nor has physical CarPlay. Do not claim newly compiled native PASS. No commit/push.
