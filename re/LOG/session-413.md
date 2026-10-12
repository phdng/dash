# Session-413 — Packed dock covered and exit-state regression

Continued uncommitted Sessions 411–412 on `chore/reconstruction-build-ci`.

## Changes
Added a full packed-state covered-dock transition sequence to `scripts/hostflow_preflight_smoke.m`. Dock `{20,40,20,80}` is encoded in original 83FC 16-bit tenth-point packed form, with candidate subrect `{40,40,100,80}` and usable `{10,10,180,180}`. Test asserts initial rectangle unchanged, resolved expansion `{20,40,120,80}`, final reason `carplay-subrect+dock`, coverage `covered`; disabled exit yields `no-exit` and unexpanded bounds; dock removal yields `no-strip-published`; republishing yields covered again.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 tests), PASS `git diff --check`. Compiled macOS Objective-C smoke, Theos arm64 and CarPlay device not run. No commit/push.
