# LOG/session-255.md
_Date: 2026-10-09. Objective: switch from nearly exhausted F-013 pure decisions to the toggle-matrix VALUE-file scope and promote one exact parser without file/preferences/global state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 8a044ec.
- Working tree clean; branch ahead 70.

## Candidate selection
`re/EVIDENCE/toggle_matrix.md` marks `/var/tmp/duodash_ab_fontfloor_force` at `7EA4` as CONFIRMED. Direct decompile shows a separable string parser before the stateful CFPreferences fallback/cache write.

## Exact 7EA4 string branch
- trim `whitespaceAndNewlineCharacterSet`;
- empty after trim -> 0;
- every UTF-16 code unit must be ASCII `0`..`9`, otherwise 0;
- parse with `integerValue`;
- the decompiled unsigned range test is equivalent to accepting integers 8 through 96 inclusive;
- values <=7 or >=97 -> 0.

## Executable promotion
Added new compiled `ToggleValueHelpers.m` with `DDFontFloorOverrideValue(value)`, exported via `DuoDashShared.h`, added to the root Makefile and structural verifier.

## Boundary
No read of `/var/tmp/duodash_ab_fontfloor_force`, no `bridged_font_floor` CFPreferences lookup, no CF type handling, and no `qword_163448` cache mutation is enabled.
