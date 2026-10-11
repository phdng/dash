# Session-371 — Guarded live prepared-host composition

Continued uncommitted Sessions 361–370 on `chore/reconstruction-build-ci`.

## Change
- New `DDHostPreparedRequestReadyUsingSpringBoard` in shared header and compiled HostFlowAdapter.m; validates source shapes and active slot count, normalizes with guarded `SBApplicationController` selector path recovered from decoded `3DD4C.c`, then runs the per-slot BID and first-dimension prepared check recovered from `218D8.c`.
- Expanded macOS Objective-C smoke harness mock with integrated happy-path, CarPlay UI exemption causing expected BID mismatch, undersized slot rejection and unavailable shared controller fallback.
- Entrypoint is opt-in. No UI mutation, private hostSlots dispatch or startup invocation.

## Verification
PASS reconstruction verifier (30 modules) and `git diff --check`. macOS Objective-C smoke execution and arm64 Theos CI remain unconfirmed. No commit/push.
