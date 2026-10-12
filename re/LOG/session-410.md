# Session-410 — Compose 23D94 resolved geometry and final diagnostic

Continued uncommitted Sessions 408–409 on `chore/reconstruction-build-ci`.

## Changes
- Added `DDHostResolvedGeometryFinalReason` (DuoDashShared.h / HostFlowAdapter.m) combining `DDHostResolvedGeometryForDock`, initial reason selection and `DDHostFinalGeometryReason` into a source-derived pure-data facade.
- Exposes initial and covered-resolved rectangles plus optional intermediate coverage label. Invalid geometry returns `invalid-geometry` without writing output arguments.
- Extended hostflow Objective-C smoke assertions for covered subrect (`carplay-subrect+dock`), unpublished dock (`carplay-subrect`) and failure preserving outputs; added export registry entry.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `python scripts/test_dock_geometry_vectors.py` (2 tests); PASS `git diff --check` (Windows CRLF warnings only). macOS compiled smoke / Theos arm64 / real CarPlay unverified. No commit or push.
