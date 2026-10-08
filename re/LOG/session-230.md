# LOG/session-230.md
_Date: 2026-10-08. Objective: promote whole exact AnyHost CString string preference reader 9DE28 while preserving its empty-string behavior and excluding notify/global/private state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 7c57f01.
- Working tree clean; branch ahead 45.

## Candidate filtering
- `9DD9C` relaunches SpringBoard / signals the process and remains excluded.
- `9DEEC` mutates global cache state and posts Darwin notifications and remains excluded.
- `9DFD4` is dispatch-once global object state and remains excluded.
- `9DE28` is a bounded preference reader with no side effects beyond preference synchronization.

## Exact 9DE28 semantics
- Synchronize settings domain for CurrentUser/AnyHost.
- Convert caller-provided C key using `NSString stringWithUTF8String:`.
- `CFPreferencesCopyValue` from the settings domain with CurrentUser/AnyHost.
- Missing value => nil.
- Return the copied value only if it is NSString; otherwise nil.
- Empty NSString is valid and preserved. This intentionally differs from the R-207 nonempty-string helper.

## Executable promotion
Added `DDCopyStringPreferenceAnyHostForCString(const char *key)` to already-compiled PrefsResolver.m and exported it in DuoDashShared.h.

## Boundary
No Darwin notification, global cache, crash-status publication, private API, or preference writeback is activated.

## Next
After compiler green, inspect another pure helper only if independently evidenced and non-duplicative; otherwise switch subsystem.