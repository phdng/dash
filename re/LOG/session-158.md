# LOG/session-158.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-157 commit `dde603e`; decode and promote exact data-only `35FBC` splash-fade UIView-animation action-0 cleanup behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `dde603e`.
- Working tree clean and synchronized with origin.
- User confirmed session-157 macOS CI/compiler GREEN.

## Target
- Function: `sub_35FBC`.
- LSDA: `0x113F94`.
- Role: construct animation/completion stack blocks around a target splash view + weak owner, invoke `+[UIView animateWithDuration:animations:completion:]`, then tear down copied weak and retained captures.

## Exact LSDA
1. `0x35FBC..0x3606C` -> no landing.
2. `0x3606C..0x36084 -> 0x360B4`, action 0.
3. `0x36084..0x360C8` -> no landing.

There is no typed/catch-all swallow in this function.

## Raw ARM64 ownership setup
Before the protected range:
```
360028  ldr x0,[x19,#0x20]
36002C  objc_retain
360030  str x0,[sp,#0x58]      ; animation-block strong capture committed

360050  ldr x0,[x19,#0x20]
360054  objc_retain
360058  str x0,[sp,#0x28]      ; completion-block strong capture committed

36005C  add x21,sp,#8
360060  add x0,x21,#0x28
360064  add x1,x19,#0x28
360068  objc_copyWeak          ; copied weak owner initialized
```

Thus, before `0x3606C` begins:
- animation strong capture is retained and committed;
- completion strong capture is retained and committed;
- completion weak owner capture has been copied/initialized.

## Protected UIView animation range
```
36006C  load duration 0.3
360074  animations block = sp+0x38
360078  completion block = sp+0x08
36007C  load UIView class
360080  +[UIView animateWithDuration:animations:completion:]
```

If the animation call returns normally, execution continues at `0x36084`.

The animation machinery may already have scheduled/applied animation state before an exception is thrown. Local code has no rollback path.

## Normal post-call cleanup
Outside protection:
```
360084  objc_destroyWeak(completion copied weak)
36008C  load completion strong capture
360090  objc_release
360094  load animation strong capture
360098  objc_release
```

Normal flow therefore destroys the weak capture first, then releases completion strong capture, then animation strong capture.

Any exception in this post-call cleanup is unprotected.

## Action-0 landing
```
3600B4  mov x19,x0            ; preserve active exception
3600B8  add x0,x21,#0x28
3600BC  objc_destroyWeak
3600C0  mov x0,x19            ; restore active exception
3600C4  resume unwind
```

This landing:
- does not invoke `objc_begin_catch`;
- does not swallow;
- preserves the active exception;
- definitely destroys the copied weak capture;
- resumes unwind.

Because control does not return to `0x36084`, normal strong-capture releases at `0x36090` and `0x36098` are bypassed on this local unwind path.

## Promoted runtime contract
Added:
- `DDSplashFadeAnimationExceptionSite`:
  - `UIViewAnimationInvocation`;
  - `UnprotectedRange`.
- `DDSplashFadeAnimationExceptionOutcome`.
- `DDResolveSplashFadeAnimationExceptionOutcome(site)`.

Animation invocation site records:
- action-0 resume unwind;
- exception propagation;
- copied weak capture definitely initialized before protected call;
- copied weak capture definitely destroyed before resume unwind;
- animation strong capture definitely committed before protected call;
- animation strong-capture release may be bypassed;
- completion strong capture definitely committed before protected call;
- completion strong-capture release may be bypassed;
- animation side effects may already have applied before throw.

Unprotected site:
- propagates.

## Explicit exclusions
R-157 does not:
- invoke UIKit animation APIs;
- create/copy/destroy real captures;
- retain/release live objects;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 358F0
Next earlier LSDA-bearing function:
- `358F0 -> LSDA 0x113EDC`.
- Role: large splash creation/preferences/image/dispatch pipeline.

Decoded header:
- LPStart omitted;
- TType encoding `0x9B`;
- call-site encoding ULEB128;
- call-site table length 162 bytes;
- **29 call-site entries**.

Exact call-site table:
1. `0x35924..0x35940 -> 0x35F84`, action 7.
2. `0x35940..0x3595C` -> no landing.
3. `0x3595C..0x35984 -> 0x35F70`, action 5.
4. `0x35984..0x359B4` -> no landing.
5. `0x359B4..0x359BC -> 0x35F60`, action 5.
6. `0x359F4..0x35A3C -> 0x35F7C`, action 5.
7. `0x35A3C..0x35A50` -> no landing.
8. `0x35A50..0x35AF4 -> 0x35F7C`, action 5.
9. `0x35AF4..0x35B10` -> no landing.
10. `0x35B10..0x35B18 -> 0x35F7C`, action 5.
11. `0x35B1C..0x35B5C -> 0x35F78`, action 5.
12. `0x35B5C..0x35B80` -> no landing.
13. `0x35B80..0x35BB0 -> 0x35F78`, action 5.
14. `0x35BB0..0x35BC8` -> no landing.
15. `0x35BC8..0x35BCC -> 0x35F78`, action 5.
16. `0x35BD4..0x35C14 -> 0x35F80`, action 5.
17. `0x35C14..0x35C1C` -> no landing.
18. `0x35C1C..0x35C5C -> 0x35F80`, action 5.
19. `0x35C64..0x35C8C -> 0x35F6C`, action 5.
20. `0x35C98..0x35D04 -> 0x35F74`, action 5.
21. `0x35D04..0x35D0C` -> no landing.
22. `0x35D0C..0x35D18 -> 0x35F6C`, action 5.
23. `0x35D18..0x35D2C` -> no landing.
24. `0x35D2C..0x35D78 -> 0x35F68`, action 5.
25. `0x35D78..0x35D8C` -> no landing.
26. `0x35D8C..0x35DB0 -> 0x35F64`, action 5.
27. `0x35DB0..0x35F2C` -> no landing.
28. `0x35F2C..0x35F30 -> 0x35F7C`, action 5.
29. `0x35F30..0x35FBC` -> no landing.

Landing topology:
- aliases `0x35F60/64/68/6C/70/74/78/7C/80` all branch to `0x35F84`;
- `0x35F84` checks discriminator against expected type 1;
- expected type begin/end-catches and returns;
- nonmatching type resumes unwind at `0x35FB8`.

Important: the initial call-site uses action index 7 while the other protected entries use 5. R-158 must decode the action chain before assigning site semantics rather than assuming every protected site is identical.

R-158 should map, site-by-site:
- NSFileManager no-splash marker gate;
- content-view selection and retained view lifetime;
- bounds/geometry;
- splash_selected preference synchronization/copy/type parsing;
- custom/default image path selection;
- file-existence and image-data loading;
- splash UIView/ImageView construction and hierarchy mutation;
- global splash strong store;
- splash duration file/string parsing;
- `qword_163C30` timing;
- weak owner capture initialization;
- first dispatch_after animation block;
- second dispatch_after watchdog block;
- capture teardown/release timing;
- side-effect persistence before typed catch return.

## Scout after R-158 — 35880
Next earlier LSDA-bearing function:
- `35880 -> LSDA 0x113EC8`.

Exact table:
1. `0x35894..0x358D4 -> 0x358E0`, action 1 catch-all.
2. `0x358D4..0x358F0` -> no landing.

Protected path covers:
- opacity getter;
- equality check admission into CATransaction path;
- CATransaction begin;
- disable-actions;
- setOpacity:1.0;
- CATransaction commit.

Landing `0x358E0` unconditionally begin/end-catches and returns.

R-159 should split pre-transaction opacity read from begin/disable/setOpacity/commit side-effect timing and record no rollback when a later transaction operation throws.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
