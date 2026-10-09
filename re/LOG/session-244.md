# LOG/session-244.md
_Date: 2026-10-08. Objective: promote the separable decision-only core of A8009C without enabling AirPlay preference mutation, backup, notify, or global latch behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD aa2b183.
- Working tree clean; branch ahead 59.

## Exact A8009C decision slice
Before any mutation, A8009C resolves `perf_tweak_enabled` so only CFBoolean true means enabled. It reads `maxFPS` and `encoderFPSFixed` through A81B14, chooses a target of 15 when enabled and -1 when disabled, and considers the current state matched only when both values equal the target.

## Executable promotion
Added three helpers to `PerfTuning.m`:
- `DDPerfTweakEnabledFromPreferenceValue(value)`
- `DDAirPlayTargetFPSForPerfEnabled(enabled)`
- `DDAirPlayFPSPreferencesMatchTarget(maxFPS, encoderFPSFixed, enabled)`

## Boundary
No `airplay_backup.plist`/`airplay_absent` creation, `com.apple.airplay` SetValue/removal, synchronize-after-write, async restart/notify path, `byte_164800/byte_164801` mutation, or A7FE78 notify-token state is activated.
