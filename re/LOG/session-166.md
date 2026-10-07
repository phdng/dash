# LOG/session-166.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-165 commit 723505f; decode and promote exact data-only 34250 CarPlay CADisplay resolver exception behavior, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 723505f.
- Working tree clean and synchronized with origin.
- User confirmed session-165 macOS CI/compiler GREEN.

## Target
- Function sub_34250.
- LSDA 0x113C60.
- Role: resolve the CarPlay CADisplay whose uniqueId matches the first screen ID of the current AVExternalDevice, then require usable bounds before returning the display.

## Exact LSDA call-site table
1. 0x34250..0x342B8 unprotected.
2. 0x342B8..0x342E8 -> 0x34520, action 0.
3. 0x342E8..0x34308 unprotected.
4. 0x34308..0x34338 -> 0x34520, action 0.
5. 0x34338..0x3434C unprotected.
6. 0x3434C..0x34404 -> 0x34520, action 0.
7. 0x34404..0x34440 unprotected.
8. 0x34440..0x34448 -> 0x3448C, action 5.
9. 0x3444C..0x34458 -> 0x34488, action 5.
10. 0x3446C..0x34474 -> 0x34520, action 0.
11. 0x34474..0x344A0 unprotected.
12. 0x344A0..0x344E0 -> 0x34520, action 0.
13. 0x344E0..0x34524 unprotected.

Action 5 chain is typed filter 1 followed by cleanup action 0. Action-0 and nonmatching typed paths resume unwind at 0x34520.

## Admission and early ownership
- CADisplay and AVExternalDevice class lookups are unprotected; missing class returns nil.
- Action-0 0x342B8..0x342E8 covers currentCarPlayExternalDevice + retain and screenIDs + retain. The screenIDs subsite begins with retained external device x19 committed.
- 0x342E8..0x34308 performs NSArray type admission unprotected with external device and screenIDs committed.
- Action-0 0x34308..0x34338 covers firstObject + retain and CADisplay displays + first retain. The displays subsite begins with retained first screen ID x21 committed.
- The explicit second displays retain at 0x34344 is unprotected. If it throws, the first displays retain already completed and its release can be bypassed. On success x22 represents a double-retained displays collection, later released twice.

## Enumeration action-0 range
0x3434C..0x34404 covers initial countByEnumeratingWithState, mutation handling, per-item uniqueId acquisition, NSString type check, isEqualToString against first screen ID, and enumeration advance. All failures resume unwind directly.
R-165 splits uniqueId acquisition from type/equality: acquisition may fail before x23 commit; type check starts with x23 retained; equality starts only after the type check passed.

## Matched candidate and typed bounds checks
- A uniqueId match leads to unprotected candidate retain at 0x34430, then x24 commit.
- Typed action-5 0x34440..0x34448 protects respondsToSelector(bounds). Expected catch has no committed capability result.
- Typed action-5 0x3444C..0x34458 protects bounds. It is reachable only after capability returned true; caught bounds result dimensions are not committed.
- Both expected typed paths begin/end-catch and then continue at 0x344A0.
- Nonmatching typed exceptions resume unwind at 0x34520.

## Catch cleanup nuance
The typed catch does not assign nil inside the landing. objc_end_catch at 0x3449C is unprotected; candidate release at 0x344A0 is action-0. Only after candidate release returns does 0x344A8 set x24=nil and final cleanup continue.
Therefore the promoted contract says candidate becomes nil if catch cleanup completes. An exception from end-catch or candidate-release cleanup can propagate and bypass later cleanup.

## Normal bounds validation
After a successful bounds call both dimensions are compared against 20.0. Candidate release at 0x3446C is action-0. If bounds are valid, 0x34478 unprotectedly re-retains the candidate for return; a failure there propagates after bounds validity is definite. Invalid bounds converge on nil cleanup.

## Final action-0 cleanup
0x344A0..0x344E0 contains staged releases: candidate, uniqueId x23, displays x22 first release, displays x22 second release, first screen ID x21, screenIDs, and external device x19. Any release exception resumes unwind and bypasses later stages.

## Promoted runtime contract
Added DDCarPlayDisplayResolverExceptionSite, DDCarPlayDisplayResolverExceptionOutcome, and DDResolveCarPlayDisplayResolverExceptionOutcome(site).
Metadata records typed swallow, nonmatching/action-0 unwind, catch-internal end-catch propagation, conditional nil fallback, temporary-vs-committed device/screenIDs/firstObject/displays/uniqueId/candidate ownership, double-retain displays lifetime, uniqueId type/equality milestones, bounds capability/read/validation, return re-retain, and staged cleanup bypass.

## Explicit exclusions
R-165 does not query live CADisplay/AVExternalDevice objects, enumerate live displays, mutate ownership, or execute exception/unwind machinery.

## Verification
- python scripts/verify_reconstruction.py -> PASS.
- python -m py_compile scripts/verify_reconstruction.py -> PASS.
- Final standard verifier and git diff --check run immediately before commit.

## Scout for next batch — 34020
- Next earlier LSDA-bearing function: 34020 -> LSDA 0x113C1C.
- Exact 9-entry table:
  1) 0x34038..0x3403C -> 0x341B8 action 7.
  2) 0x34048..0x340A8 -> 0x341BC action 5.
  3) 0x340A8..0x340B8 unprotected.
  4) 0x340B8..0x34118 -> 0x341C0 action 5.
  5) 0x34118..0x34128 unprotected.
  6) 0x34128..0x34148 -> 0x341C0 action 5.
  7) 0x34148..0x34150 unprotected.
  8) 0x34150..0x34180 -> 0x341C0 action 5.
  9) 0x34180..0x341E0 unprotected.
- Semantic groups: buildShellIfNeeded gate; UIView/bounds/init/background color; UILabel/properties/white color; bold font; text/addSubview/installContent/present.
- Expected typed catch converges at 0x341C0, begin/end-catches and returns immediately. Root view/label normal releases are bypassed; a caught present exception occurs before captured result-byte store at 0x34180.
- Nonmatching typed exceptions resume unwind at 0x341DC.

## Scout after R-166 — 33F5C
- 33F5C -> LSDA 0x113C08.
- Single action-1 catch-all 0x33F70..0x33F88 -> 0x33FA0, then unprotected tail.
- Protected sequence: buildShellIfNeeded; if true installContent; then present.
- Captured present-result byte store at 0x33F90 is outside protection, so any caught protected exception skips it.
- Landing unconditionally begin/end-catches and returns.
- Direct next after this is 33DB4 -> LSDA 0x113BE8.

Known unresolved remain: 73E8/80D0, full 7E908, and jailbroken-device smoke testing.
