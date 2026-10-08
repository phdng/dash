# LOG/session-167.md
_Date: 2026-10-07. Objective: continue R-166 by promoting exact data-only 34020 Phase-4a display-OK UI builder exception behavior, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 6acd5f3.
- Working tree clean; branch was ahead of origin by one commit.
- Continued from session-166 scout of 34020 -> LSDA 0x113C1C.

## Exact LSDA table
1. 0x34038..0x3403C -> 0x341B8, action 7.
2. 0x34048..0x340A8 -> 0x341BC, action 5.
3. 0x340A8..0x340B8 unprotected.
4. 0x340B8..0x34118 -> 0x341C0, action 5.
5. 0x34118..0x34128 unprotected.
6. 0x34128..0x34148 -> 0x341C0, action 5.
7. 0x34148..0x34150 unprotected.
8. 0x34150..0x34180 -> 0x341C0, action 5.
9. 0x34180..0x341E0 unprotected.

## Semantics promoted
- Action-7 site: buildShellIfNeeded gate.
- Action-5 root-view site: UIView/bounds/init/background-color construction.
- Unprotected background-color release.
- Action-5 label site: UILabel creation/properties/white-color styling.
- Unprotected white-color release.
- Action-5 font site.
- Unprotected font release.
- Action-5 late site: label text, addSubview, installContent, present.
- Unprotected tail: captured present-result byte store followed by normal label/root-view cleanup.

## Catch behavior
All expected typed landing aliases converge at 0x341C0. The catch begin/end-catches and returns immediately. It does not continue remaining UI work and does not run normal label/root-view cleanup. A protected present exception therefore occurs before the captured result byte store at 0x34180. Nonmatching typed exceptions resume unwind at 0x341DC. Interleaved style releases and the result-store/final-cleanup tail are unprotected and propagate.

## Runtime contract
Added DDDisplayOKUIBuilderExceptionSite, DDDisplayOKUIBuilderExceptionOutcome, and DDResolveDisplayOKUIBuilderExceptionOutcome(site). The resolver records shell-result timing, temporary-vs-committed root-view/label ownership, background/white/font release milestones, possible label/hierarchy/install/present side effects, present-result-store skip, cleanup bypass, nonmatching unwind, and unprotected propagation.

## Explicit exclusions
Data-only only. No UIKit/private presentation invocation, live view hierarchy mutation, ownership mutation, exception runtime, or unwind execution.

## Next scout
R-167: 33F5C -> LSDA 0x113C08. Single action-1 catch-all 0x33F70..0x33F88 -> 0x33FA0 over buildShellIfNeeded, conditional installContent, and present. Landing unconditionally begin/end-catches and returns; captured present-result byte store at 0x33F90 is outside protection. Direct next is 33DB4 -> 0x113BE8.
