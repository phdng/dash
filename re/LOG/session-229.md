# LOG/session-229.md
_Date: 2026-10-08. Objective: promote whole exact AppBridge section-override sanitizer 9D4B4 without enabling preference writeback or private app-object behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 335c35d.
- Working tree clean; branch ahead 44.

## Candidate selection
- `9D048` parses crash-state text but its parameter decompile is ambiguous enough to avoid naming/promoting yet.
- `9D4B4` has a fully bounded whole-helper contract: app preference read plus pure dictionary sanitization.
- `9DA04` mutates and writes the override dictionary, so only its read/sanitize dependency is promoted in this batch.

## Exact 9D4B4 semantics
- `CFPreferencesAppSynchronize` settings domain.
- Copy `appbridge_app_sections` from the same app domain.
- Missing value or non-NSDictionary => empty dictionary.
- Enumerate dictionary keys.
- Key must be NSString and nonempty.
- Value must be NSString and exactly lowercase `user` or `system`.
- Retain only those valid pairs in the returned dictionary.

## Executable promotion
Added `DDCopyAppBridgeSectionOverrides()` to already-compiled PrefsResolver.m and exported it in DuoDashShared.h.

## Boundary
No preference writeback, classification mutation, app object selector probing, hidden/prohibited flags, private frameworks, or UI behavior are activated.

## Next
After compiler green, inspect another pure AppBridge helper only if independent from private app-object selectors/flags and writeback side effects; otherwise switch subsystem.