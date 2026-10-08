# LOG/session-215.md
_Date: 2026-10-08. Objective: promote exact Keyinput immediate knob probe 4A780 without pulling cache/global relay state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 264ed33.
- Working tree clean; branch ahead 30.

## Exact 4A780 semantics
- Retain knob name.
- Build `/var/tmp/<name>`.
- If supplied file manager reports that path exists, return true immediately.
- Otherwise call 42F10 with the same name and return whether the resolved path is non-nil.
- Release temporaries and return.

## Executable promotion
Added `DDKeyinputKnobPresentNow(NSString *name)` to compiled KeyinputGate.m and exported it in DuoDashShared.h. Reconstruction uses `NSFileManager defaultManager`, matching the surrounding callers' ordinary file-manager behavior while preserving exact path precedence.

## Boundary
No TTL cache, timestamps, relay globals, private selectors, keyboard hooks, or UIKit behavior are activated.

## Next
After compiler green, continue another pure helper only if independent from relay globals/private selectors; otherwise switch subsystem.