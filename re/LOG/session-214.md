# LOG/session-214.md
_Date: 2026-10-08. Objective: promote exact Keyinput force-I/O knob helper 42124 without enabling adjacent private settings mutation._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 2b7a6b5.
- Working tree clean; branch ahead 29.

## Exact 42124 semantics
- Read `/var/tmp/duodash_ab_forceio` via `NSString stringWithContentsOfFile:encoding:error:` with UTF-8 encoding.
- Get `NSCharacterSet whitespaceAndNewlineCharacterSet`.
- Trim the read string.
- Return `[trimmed isEqualToString:@"1"]`.
- Missing/unreadable file yields nil; trim/equality naturally returns false.
- Empty, whitespace-only, `0`, `01`, `true`, or any other content returns false.

## Executable promotion
Added `DDKeyinputForceIOEnabled()` to compiled KeyinputGate.m and exported it in DuoDashShared.h.

## Boundary
Adjacent `421CC` uses private `_otherSettings` and `_setFlag:forSetting:` and remains excluded. No relay hooks/globals/private UI behavior are activated.

## Next
After compiler green, inspect another pure Keyinput helper only if independent from relay globals/private selectors; otherwise switch subsystem.