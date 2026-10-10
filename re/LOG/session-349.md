# Session-349 — Objective-C preflight behavior test harness

Retains uncommitted Sessions 346–348 on `chore/reconstruction-build-ci`.

## Changes
- `DuoDashShared.h`: declare `DDHostSwitchPreflightSelfTest()` for explicit invocation only.
- `HostFlowAdapter.m`: add self-test of the compiled preflight API with six scenarios: accepted snapshot, reversed ordered BIDs, stale pending generation, invalid slot size, shell bounds mismatch, and combined size+bounds failures. Validates early short-circuit and failure bits.
- No self-test invocation from constructors or SpringBoard startup. No private selector/UI changes.

## Verification
PASS structural reconstruction verifier (30 modules) and git diff --check (line-ending warnings only). The Objective-C self-test has NOT been executed because local Windows environment lacks the iOS toolchain/runtime. Arm64 CI unconfirmed; no commit/push.
