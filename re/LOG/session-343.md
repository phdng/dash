# Session-343 — Compiled early switch guard composition

User requested actual code work instead of additional verifier-only updates. At session start the worktree was clean.

## Objective-C changes
- `re/RECONSTRUCTION/DuoDashShared.h`: added caller-supplied `DDHostSwitchEarlyGuardSnapshot` and public `DDHostSwitchEarlyGuardsAllow` API.
- `re/RECONSTRUCTION/HostFlowAdapter.m`: implemented a pure conjunction of four previously evidence-backed 208F4:170-206 predicates: interaction, generation/geometry/layout, hosted/runtime/layout slot counts/capacity and mode flags.
- This is compile-target source but has no new private state access, UI switching or selector calls. No caller is yet wired; it does not make dual-pane hosting complete.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check` (LF/CRLF warnings only). No local iOS arm64 toolchain; CI remains unconfirmed. No commit/push.
