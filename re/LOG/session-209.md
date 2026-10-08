# LOG/session-209.md
_Date: 2026-10-08. Objective: promote the exact picker array-selection preference read path from 89D10 without compiling UIKit picker controllers._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD e0b5a08.
- Working tree clean; branch ahead 24.

## Exact 89D10 array read semantics
- Read controller arrayKey length.
- Non-empty arrayKey => use it directly.
- Nil/empty arrayKey => use exact fallback `bridgedApps`.
- Synchronize `com.sensetechlab.duodash.settings` CurrentUser/AnyHost.
- Copy selected key with CFPreferencesCopyValue.
- Missing value => empty array.
- Only CFArray is accepted; non-array => empty array.
- No element filtering, string validation, deduplication, or sorting occurs in the read path.
- The controller next passes this raw array to NSMutableSet setWithArray:; that UIKit/controller state remains outside this helper.

## Executable promotion
Added `DDCopyPickerArrayPreferenceAnyHost(NSString *key)` to compiled PrefsResolver.m and public reconstruction header.

## Boundary
No CNABAppPickerController, maxSel mutation, NSMutableSet writeback ordering, settings.changed post, or appbridge.listchanged post is compiled in this batch.

## Next
After compiler green, inspect writeback/notification helpers only if their exact ordering can be isolated from UIKit controller state.