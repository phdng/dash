# LOG/session-204.md
_Date: 2026-10-08. Objective: move to a non-license subsystem and promote the exact 891F0 voicecmd preference resolver into compiled SiriProbe.m without activating Siri hooks._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 02ea354.
- Working tree clean; branch ahead 19.

## Exact 891F0 semantics
- `voicecmd_enabled`: CFPreferencesGetAppBooleanValue; true only when returned value is true and `keyExistsAndHasValidFormat` is true.
- `voicecmd_selected`: CopyAppValue; only CFString is copied to a zeroed 97-byte UTF-8 buffer.
- Validation: length 1..96, no leading/trailing `.`, bytes only ASCII 0-9/A-Z/a-z/`-`/`.`, and at least one dot.
- Any invalid/missing/non-string/conversion-failed value clears selected to empty.

## Executable promotion
- Added `DDResolveVoiceCommandPreferences(NSString **selectedOut)`.
- Added SiriProbe.m to Makefile target.
- Existing hook/swallow/logger/cache synthesis remains inert and is not wired from Tweak.x.

## Next
After compiler green, inspect 88FD0/890A0 cache wrapper only if exact lock/timestamp semantics can be represented without activating hooks.