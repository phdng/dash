# LOG/session-292.md
_Date: 2026-10-09. Objective: continue respring reconstruction with the exact pure carsleep admission predicate embedded in 8097C while excluding notify acquisition and respring execution state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 27b0eaf.
- Working tree clean; branch ahead 107.

## Evidence
Inside `sub_8097C`, after the cooldown passes:
- `notify_register_check("com.sensetechlab.carsleep/sleeping", &token)` is evaluated first;
- a nonzero registration result short-circuits the OR and proceeds;
- on successful registration, state storage is zero-initialized, `notify_get_state` is called, token is cancelled, and the branch proceeds only when the resulting 64-bit state equals zero.

## Executable promotion
Added `DDRespringCarsleepGateAllows(notifyRegisterResult,sleepingState)` to compiled `Respring.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No notify registration/get/cancel calls, token management, state initialization/error handling, `sub_9C790`, latch mutation, respring_last file touch, ack notify, delayed scheduling or actual respring execution is enabled.
