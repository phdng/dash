# LOG/session-252.md
_Date: 2026-10-09. Objective: switch from completed init-role pure scope to the evidence-only AZ CarPlay spoof subsystem and promote only its shared decision core._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD e15fb92.
- Working tree clean; branch ahead 67.

## Evidence
F-017 resolves seven AZ hooks: `49870`, `498A0`, `498D0`, `49900`, `49930`, `49960`, and `49990`. Direct decompile of all seven confirms identical control flow apart from counter/original slots:
1. increment a per-hook counter;
2. if `(byte_163ED8 & 1) != 0`, return 0;
3. otherwise call the corresponding original function and return its result.

## Executable promotion
Added new compiled `CarPlaySpoofHelpers.m` with `DDAZCarPlaySpoofedResult(forceDisconnected, originalResult)`, exported through `DuoDashShared.h`, added to root Makefile and structural verifier.

## Boundary
The helper receives both gate and original result from the caller. It does not install MSHooks, increment the seven counters, read `byte_163ED8`, call any original function pointer, or mutate process-global state.
