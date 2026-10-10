# Session-313 — Pure no-display refusal predicate

User confirms arm64 Theos CI green through session-312. Workspace branch started clean.

## Evidence
`re/EVIDENCE/hosting_engine.md`, 218D8:315-327: when CarPlay usable bounds are empty and `prepareShell` fails, report `no-display` refusal and exit. The exact pure predicate is `usableBoundsEmpty && !prepareShellSucceeded`. Acquisition, private shell calls, errors, notifications, and hosting state are not promoted.

## Changes
- Added exported `DDHostShouldRefuseNoDisplay` pure boolean helper in compiled `HostFlowAdapter.m` and `DuoDashShared.h`.
- Added structural regression guard to `scripts/verify_reconstruction.py`.
- Updated `re/STATE.md` for session-313.

## Verification
PASS: reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warnings only). New helper requires Theos arm64 CI validation; no auto push.
