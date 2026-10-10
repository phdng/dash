# Session-312 — Pure full-host versus reshow route decision

User confirmed Theos arm64 CI green after session-311. Working tree started clean.

## Evidence
`re/EVIDENCE/hosting_engine.md`, `218D8:307-313`: full-host is chosen when `23454()` indicates deactivate-dismiss, OR inactive, OR not split-hosting, OR visible, OR geometry `1639B8!=1639BC`, OR dirty `v28`, OR present is false. Otherwise the branch chooses reshow. Sources/gate acquisition are not promoted.

## Changes
- Added pure `DDHostRequiresFullHost(deactivateDismissPresent, active, splitHosting, visible, geometryMismatch, dirty, canPresent)` to already-compiled `HostFlowAdapter.m`.
- Exported via `DuoDashShared.h`; structural verifier guard added.
- Updated `re/STATE.md`. No runtime hook wiring or private APIs.

## Verification
PASS reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warnings only). Full arm64 CI for session-312 code pending; no push.
