# Session-420 — Independent CarPlay shell/usable snapshot transition pipeline

Started from a clean `chore/reconstruction-build-ci` after Session-419. No commit or push in this session.

## Motivation
Session-419 compared packed dock/exit state before and after while reusing a single `shellBounds` and `carPlayUsableBounds`. That could skip relayout when the CarPlay usable region changes or the hosted shell moves even though dock state is unchanged. This matters for hosting lifecycle transitions and restoration after dock loss.

## Changes
- `DuoDashShared.h` / `HostFlowAdapter.m`: new pure-data `DDHostDockLayoutTransitionForSnapshots` evaluates the full 83FC -> 23D94 -> 26654 -> 269FC path for independent before/after shell, usable bounds, dock state and exit flag. Returns `unchanged`, `reason-only`, `updated`, `restored` or `invalid-geometry` and retains output atomicity on invalid snapshots.
- Existing `DDHostDockLayoutTransition` now delegates to the new evaluator with shared shell/usable values, preserving its signature and avoiding duplicate comparison logic.
- Objective-C smoke tests: dock remains published while usable bounds grow; shell moves without dock change; usable changes but final geometry remains fixed; dock disappears as usable bounds resize; reason changes despite identical CGRect; malformed next/previous snapshot leaves every caller output untouched.
- Python oracle and tests: added `layout_transition_for_snapshots`, routed the prior `layout_transition` through it, and added the independent snapshot regression matrix. Structural verifier export registry updated.

## Verification
PASS `python scripts/test_dock_geometry_vectors.py` (8 tests), PASS `python scripts/verify_reconstruction.py` (30 synthesis modules), PASS `git diff --check` (Windows line-ending notices only). Objective-C compiled macOS smoke, Theos arm64 build and live CarPlay/device hosting remain unverified. No UI writes or notify registrations introduced. No commit/push.
