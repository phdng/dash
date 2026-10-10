# Session-348 — Staged Objective-C switch preflight

Continued `chore/reconstruction-build-ci`, retaining uncommitted Sessions 346-347.

## Compiled Objective-C
- `DuoDashShared.h`: `DDHostSwitchPreflightResult` and exported `DDHostSwitchPreflight` accepting the early snapshot, normalized BID arrays, measured hosted-slot size and observed shell-bounds mismatch.
- `HostFlowAdapter.m`: short-circuit early 208F4 guards, then ordered BID matching, then size/bounds checks. Return distinct diagnostic fields and `canProceedToPrivateSwitchChecks` only if all supplied predicates pass.
- Does not acquire private host state, normalize via private 3DD4C, call UI selectors, or authorize final switching.

## Verification
PASS reconstruction verifier (30 modules) and git diff --check (CRLF conversion warnings only). No arm64 Theos compiler locally; CI unconfirmed. No commit/push.
