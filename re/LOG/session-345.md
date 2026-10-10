# Session-345 — Compiled post-early switch rejection gates

Workspace was clean at start of session; previous Session-344 changes are in HEAD.

## Changes
- `re/RECONSTRUCTION/DuoDashShared.h`: declare `DDHostSwitchPostEarlyFailure` flags and `DDHostSwitchPostEarlyFailures` API.
- `re/RECONSTRUCTION/HostFlowAdapter.m`: aggregate evidenced 208F4:207-242 hosted-slot-size and shell-bounds rejection conditions into a diagnostic bitmask. Calls existing pure helpers, does not access private state.
- BID identity checks and shell-bound measurement remain excluded; a zero mask does not authorize switching. No live UI mutation or hooks.

## Verification
PASS reconstruction verifier (30 synthesis modules) and `git diff --check` (LF/CRLF warnings only). Arm64 Theos CI unconfirmed. No commit/push.
