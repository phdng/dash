# LOG/session-271.md
_Date: 2026-10-09. Objective: continue exact toggle VALUE promotion with the live-present animation easing classifier embedded in 2A610 while excluding full animation orchestration._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 00d3366.
- Working tree clean; branch ahead 86.

## Evidence
Inside `/var/tmp/duodash_ab_livepresent_anim` parsing in `2A610`, the optional third component is classified independently:
- if the third component is absent, classifier result is false;
- otherwise call NSString `lowercaseString`;
- return true iff the lowercase token `hasPrefix:@"lin"`.

This makes matching case-insensitive and prefix-based: `lin`, `linear`, and `LINEAR` are true, while other tokens are false.

## Executable promotion
Added `DDLivePresentAnimationUsesLinearEasing(value)` to compiled `ToggleValueHelpers.m` and exported it through `DuoDashShared.h`.

## Boundary
No file read, top-level trim/split, alpha-list parsing, duration fallback, animation creation, presenter construction, or UI/window state is enabled.
