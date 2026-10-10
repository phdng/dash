# Session-344 — Objective-C early switch failure diagnostics

Worktree was clean on `chore/reconstruction-build-ci` at start; prior Session-343 code already present in HEAD.

## Compiled-source changes
- `DuoDashShared.h`: declare `DDHostSwitchEarlyGuardFailure` bitmask enum with interaction, consistency, slot-count and mode-flags reasons, and `DDHostSwitchEarlyGuardFailures`.
- `HostFlowAdapter.m`: independently evaluate four previously promoted guards and OR the applicable reason bits; `DDHostSwitchEarlyGuardsAllow` delegates to zero-failure result.
- Caller must supply a fully populated snapshot. Zero failure does not authorize live switching because BID matching, bounds and other private checks remain outside the seam. No hook/UI actions added.

## Verification
PASS reconstruction verifier (30 synthesis modules) and git diff --check (line-ending warnings only). No local arm64 compiler; Theos CI not confirmed. No commit/push.
