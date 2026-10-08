# LOG/session-225.md
_Date: 2026-10-08. Objective: promote exact deep-sleep CurrentHost preference resolver 86338 without enabling CarSleeper system-control orchestration._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 8705290.
- Working tree clean; branch ahead 40.

## Candidate filtering
- Camera-relay helpers after 84258 were side-effectful: queue/global init, dispatch, process scan/injection, notify, file writes.
- Several 85xxx pure transforms were already reconstructed exactly in Migration/PrefsResolver (`DDMigrationUniqueNonemptyStrings`, `DDMigrationStringDictionary`, `DDMigrationJoinOrNone`, key counting, snapshot, default-true boolean).
- `86338` is independent and not duplicated.

## Exact 86338 semantics
- `CFPreferencesSynchronize` domain `com.sensetechlab.duodash.settings`, CurrentUser, CurrentHost.
- Copy `deepsleep_enabled` from the same scope.
- Missing value => false.
- Existing value => true only when type is CFBoolean and value is true.
- Nonboolean and CFBoolean false => false.

## Executable promotion
Added `DDDeepSleepEnabledCurrentHost()` to already-compiled PrefsResolver.m and exported it in DuoDashShared.h.

## Boundary
No autolock mutation, radio/location control, process suspend/resume, CarSleeper state files, private SpringBoard APIs, or global transition state are activated.

## Next
After compiler green, inspect another pure preference/state decoder only if independent from system-control/private APIs; otherwise switch subsystem.