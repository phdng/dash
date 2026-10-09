# LOG/session-290.md
_Date: 2026-10-09. Objective: switch away from exhausted A2800 crash parsing and promote the exact pure respring cooldown decision embedded in 8097C while excluding filesystem/notify/global execution state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 02e365c.
- Working tree clean; branch ahead 105.

## Evidence
Inside `sub_8097C`:
- `v0` starts at `-1.0`, representing no prior `respring_last` timestamp;
- jailbreak prefix is acquired elsewhere, then null is normalized to `""`;
- nonempty prefix selects cooldown `60.0`;
- empty prefix selects cooldown `8.0`;
- the guarded body continues when `v0 < 0.0 || v0 >= cooldown`.

## Executable promotion
Added `DDRespringCooldownSecondsForJailbreakPrefixCString(prefix)` and `DDRespringCooldownAllowsElapsed(elapsedSeconds,prefix)` to compiled `Respring.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `stat`, NSDate acquisition, pthread_once/global jailbreak-prefix acquisition, carsleep notify state, `sub_9C790`, respring latch mutation, file touch/chmod, ack notify, delayed block scheduling or actual respring execution is enabled.
