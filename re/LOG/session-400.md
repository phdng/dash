# Session-400 — Integrated 269FC dock coverage decision

Continued uncommitted Sessions 390–399 on `chore/reconstruction-build-ci`.

## Changes
- Exported and implemented `DDHostDockCoverageReason` in `DuoDashShared.h` and `HostFlowAdapter.m`, composing existing source-derived early reason, adjacency and covered expanded bounds pure-data helpers.
- Reasons: `no-exit`, `no-strip-published`, `no-window`, `already-inside`, `strip-not-adjacent`, `outside-usable`, `covered`.
- Added smoke assertions for each return reason, exact covered rectangle and output preservation on failure.
- Added helper to `scripts/verify_reconstruction.py` export check.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 synthesis modules) and `git diff --check`. macOS compiled Objective-C smoke, Theos arm64 and live CarPlay not executed. No commits/push.
