# LOG/session-087.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-086 commit b797b03; complete R-086 with data-only 421CC private flag-clear eligibility and 41BA0 bounded exception-reason probe decisions. Per user workflow, commit locally but do not push._

## R-086 — 421CC private other-settings flag clear

Directly reviewed:
- `421CC.c`
- caller context in `400D0.c`
- caller context in `41F50.c`
- private ivar helpers `9C24C.c/9C4AC.c`

Exact original action:
- if the settings object exists;
- resolve private object ivar `_otherSettings`;
- if that object exists and responds to `_setFlag:forSetting:`;
- send `_setFlag:0 forSetting:6`.

Promoted only as data:
- `DDOtherSettingsFlagClearDecision`
  - `shouldClear`
  - fixed `flagValue = 0`
  - fixed `settingIndex = 6`
- `DDResolveOtherSettingsFlagClearDecision(settingsObjectPresent, otherSettingsPresent, flagSetterSupported)`.

The reconstruction does not fetch `_otherSettings` and never sends the private setter.

## R-086 — 41BA0 bounded exception reason probe

Direct decompile shows:
- global probe counter `qword_163EA0`;
- gate `counter <= 0x13`;
- increment once inside the gate;
- only then check `respondsToSelector:@selector(reason)`;
- if supported, retrieve/release `reason`;
- counts above 19 do nothing.

Therefore the exact budget is 20 attempts for initial counts 0 through 19.

### Raw ARM64 cross-check

The decompiler metadata listed `41BA0` as a callee of exception catch stubs, but their displayed bodies omitted the call. Raw ARM64 from the first arm64 slice confirms calls at:
- `0x40458: bl 0x41ba0`;
- `0x40ac4: bl 0x41ba0`;
- `0x41114: bl 0x41ba0`.

The surrounding paths call Objective-C catch helpers before/after the probe, confirming 41BA0 is an exception-path diagnostic helper.

Promoted:
- `DDExceptionReasonProbeDecision`
  - `withinBudget`
  - `shouldReadReason`
  - `nextProbeCount`
- `DDResolveExceptionReasonProbeDecision(currentProbeCount, reasonSelectorSupported)`.

Exact pure semantics:
- `currentProbeCount > 19` -> not within budget, no reason read, count unchanged;
- `0..19` -> within budget, next count is `current + 1`;
- reason read eligibility equals caller-supplied selector support.

## Explicit exclusions

R-086 does not:
- access private `_otherSettings` ivar memory;
- send `_setFlag:forSetting:`;
- mutate `_interfaceOrientation`;
- invoke exception `reason`;
- mutate the original global probe counter;
- add exception logging or catch behavior.

## Next

R-087 after compiler green:
- inspect `9C3BC/9C4AC/9C24C` private ivar type-decision rules;
- promote only data-only ivar access/write-width plans from caller-supplied ivar/type-encoding inputs;
- do not read object ivar memory, write `_interfaceOrientation`, or return private `_otherSettings` objects.
