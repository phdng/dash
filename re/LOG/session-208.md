# LOG/session-208.md
_Date: 2026-10-08. Objective: leave hook-heavy SiriProbe work and promote exact picker scalar preference helper 8C2A0 into the existing executable PrefsResolver without compiling UIKit picker classes._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 8bb8153.
- Working tree clean; branch ahead 23.

## Exact 8C2A0 semantics
- Retain input key.
- Empty/nil key => nil.
- For non-empty key, synchronize `com.sensetechlab.duodash.settings` under CurrentUser/AnyHost.
- Copy exactly that key with `CFPreferencesCopyValue`.
- Missing value => nil.
- Only CFString values are retained.
- Empty CFString => nil.
- Non-empty CFString => returned string.

## Executable promotion
Added `DDCopyNonemptyStringPreferenceAnyHost(NSString *key)` to compiled PrefsResolver.m and public reconstruction header.

## Boundary
No CNABAppPickerController/UIKit class, table view, selection mutation, or layout behavior is compiled or wired.

## Next
After compiler green, inspect the array-selection read path or another bounded preference helper only if its exact type/default semantics can be isolated.