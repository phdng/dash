# LOG/session-213.md
_Date: 2026-10-08. Objective: promote exact Keyinput knob path resolution/cache helpers 42F10/453B8 without compiling relay hooks._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD bcb197f.
- Working tree clean; branch ahead 28.

## Exact 42F10 resolver
- Read `NSTemporaryDirectory()`.
- Empty temp path or empty name => nil.
- Check `<temp>/<name>` first; if it exists, return it.
- Only when name has prefix `duodash_`, take substring from index 8, prepend `carnav_`, and check `<temp>/<legacyName>`.
- Existing legacy file => return legacy path; otherwise nil.

## Exact 453B8 cache
- Sample `NSProcessInfo.systemUptime`.
- Refresh when cached int has sign bit set / is negative, or `now - timestamp >= 1.0`.
- On refresh, check `/var/tmp/<name>` first.
- If absent, call the 42F10-equivalent resolver and treat non-nil as present.
- Store presence as 0/1 and sampled uptime, then return presence.
- If cache younger than 1s and state nonnegative, return `state != 0` without filesystem work.
- No lock in original; reconstruction adds none.

## Executable promotion
Added `DDKeyinputResolvedTemporaryKnobPath` and `DDKeyinputKnobPresentCached` to compiled KeyinputGate.m and exported them in DuoDashShared.h.

## Boundary
No Keyinput relay globals, hooks, Darwin observers, plist IO, card state, or private UI behavior are activated.

## Next
After compiler green, inspect another pure Keyinput helper only if it stays independent of relay globals/private hooks; otherwise switch subsystem.