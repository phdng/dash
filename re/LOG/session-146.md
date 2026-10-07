# LOG/session-146.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-145 commit `75828a5`; resolve the d10/d11 uncertainty in `37398`, promote exact data-only keypane center-forward exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `75828a5`.
- Working tree clean.
- User confirmed session-145 macOS CI/compiler GREEN.
- Local tracking ref still reported ahead 1 at session start; assistant did not fetch/push.

## Target
- Function: `sub_37398`.
- LSDA: `0x114114`.
- Registered by `sub_372CC` as the landscape wrapper for `_UIKeyboardLayerHostView -setCenter:`.

## Exact LSDA call-site table
1. `0x37398..0x373CC` -> no landing.
2. `0x373CC..0x373D0` -> `0x374A8`, action 5.
3. `0x373D0..0x373EC` -> `0x374AC`, action 5.
4. `0x373FC..0x37428` -> `0x374A4`, action 5.
5. `0x37428..0x374C4` -> no landing.

Landing aliases:
- `0x374A4 -> 0x374AC`;
- `0x374A8 -> 0x374AC`.

Common typed catch `0x374AC`:
- compare discriminator with expected type;
- expected:
  - begin catch;
  - end catch;
  - branch to `0x37468`;
- nonmatching:
  - resume unwind at `0x374C0`.

## Raw register/control-flow evidence

### Caller center preservation
At entry:
```
373B4  fmov d8,d1   ; caller center.y
373B8  fmov d9,d0   ; caller center.x
```

The function then double-retains the input view and commits it to x20:
```
373C0  objc_retain
373C4  objc_retain
373C8  mov x20,x0
```

Thus every protected site begins with:
- caller center preserved in d9/d8;
- retained input x20 committed with two local ownerships.

### Working candidate center
Candidate midpoint is built separately:
- d10 = working candidate MidX;
- d11 = working candidate MidY.

Normal adoption happens only after protected work and counter logic:
```
37458  mov x0,x20
3745C  objc_release          ; first normal local release
37460  fmov d9,d10           ; adopt candidate center.x
37464  fmov d8,d11           ; adopt candidate center.y
37468  load off_163C50
...
37478  fmov d0,d9
3747C  fmov d1,d8
37480  blr off_163C50
...
374A0  tail objc_release     ; final local release
```

### Resolution of prior d10/d11 evidence gap
The previous handoff noted that early catches can occur before local d10/d11 initialization.

Raw branch target resolves this completely:
- catch branches to **0x37468**;
- it does **not** branch to 0x37460;
- therefore catch skips both d10/d11 -> d9/d8 adoption instructions;
- the forward callback receives untouched d9/d8, which are the original caller center saved at entry.

So early catch behavior does not depend on the contents/source of d10/d11.

This removes the prior evidence gap.

## Protected range 1 — pre-geometry helper
`0x373CC..0x373D0` covers only:
- helper `37640`.

Expected exception:
- swallow;
- forward original caller center;
- skip all candidate geometry;
- skip counter decrement;
- skip first local x20 release;
- still invoke `off_163C50`;
- still execute final x20 release after callback.

## Protected range 2 — candidate geometry and null check
`0x373D0..0x373EC` covers:
- `376DC` candidate CGRect helper;
- candidate component capture into d11/d12/d13/d14;
- `CGRectIsNull`.

Semantic split:

### Candidate geometry helper
If `376DC` throws:
- candidate rectangle is not guaranteed complete;
- caller center remains d9/d8;
- catch forwards caller center.

### Candidate null check
Before `CGRectIsNull`:
- candidate rectangle has completed and all components are stored.

If the null check throws:
- candidate rectangle definitely exists;
- it still has not been converted into forwarding center;
- catch forwards caller center.

## Protected range 3 — candidate midpoint
`0x373FC..0x37428` covers:
- candidate setup for `CGRectGetMidX`;
- `CGRectGetMidX`;
- commit MidX into d10;
- candidate setup for `CGRectGetMidY`;
- `CGRectGetMidY`.

Semantic split:

### Candidate MidX
At MidX call:
- candidate rectangle definitely acquired;
- null check definitely completed as non-null;
- MidX not yet committed.

Expected exception:
- caller center still in d9/d8;
- catch forwards caller center.

### Candidate MidY
At MidY call:
- candidate rectangle definitely acquired;
- null check definitely completed;
- MidX already committed into d10.

If MidY throws:
- catch still skips the later d10/d11 -> d9/d8 adoption;
- caller center remains the callback value.

The protected range ends at `0x37428`, before the `fmov d11,d0` MidY commit.

## Counter behavior
The tolerance comparison and positive `dword_162EF0` decrement are in the unprotected tail after midpoint computation.

Every expected protected catch jumps directly to callback continuation:
- candidate difference checks are skipped;
- decrement is skipped;
- no catch-time counter mutation occurs.

## Ownership behavior
The input view is retained twice before protection.

Normal path:
- first release at `0x3745C`;
- final release at `0x374A0`.

Expected catch:
- branches directly to `0x37468`;
- bypasses first release;
- callback still runs;
- final release still runs.

R-145 therefore records:
- retained input definitely committed before all protected calls;
- one local release can be bypassed;
- final cleanup continues.

The callback itself is outside LSDA coverage; callback exceptions propagate.

## Promoted runtime contract
Added:
- `DDKeyPaneCenterForwardExceptionSite`:
  - `PreGeometryHelper`;
  - `CandidateGeometryHelper`;
  - `CandidateNullCheck`;
  - `CandidateMidX`;
  - `CandidateMidY`;
  - `UnprotectedRange`.
- `DDKeyPaneCenterForwardExceptionOutcome`.
- `DDResolveKeyPaneCenterForwardExceptionOutcome(site)`.

All typed sites:
- swallow expected exception;
- forward original caller center;
- skip candidate center adoption;
- skip geometry-counter decrement;
- invoke center-forward callback;
- continue final retained-input cleanup;
- retained input definitely committed;
- one retained-input release can be bypassed;
- nonmatching type resumes unwind.

Site timing:
- null/MidX/MidY => candidate rectangle definitely acquired;
- MidX/MidY => candidate null check definitely completed;
- MidY => candidate MidX definitely committed.

Unprotected:
- propagates.

## Explicit exclusions
R-145 does not:
- run `37640` or `376DC`;
- call CGRect helpers;
- mutate `dword_162EF0`;
- invoke `off_163C50`;
- mutate real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 37284
Next earlier LSDA-bearing function:
- `37284 -> LSDA 0x114100`.
- Role: DDz1 `dropSplashIfOverdue` wrapper.

LSDA header:
```
FF 9B 11 01 08
14 14 38 01
28 20 00 00
...
```

Decoded call-site table:
1. `0x37298..0x372AC -> 0x372BC`, action 1 catch-all.
2. `0x372AC..0x372CC` -> no landing.
The function prefix `0x37284..0x37298` is unprotected.

Protected raw sequence:
```
37298  +[DDz1 shared]
372A0  retain-autoreleased
372A4  mov x19,x0
372A8  dropSplashIfOverdue
```

Landing `0x372BC`:
- unconditional `objc_begin_catch`;
- restore frame;
- tail `objc_end_catch`;
- immediate return.

There is no discriminator/nonmatching path.

R-146 should split:
- shared-DDz1 acquisition: exception may occur before x19 commit; only temporary DDz1 acquisition/release-bypass metadata;
- `dropSplashIfOverdue` send: x19 retained DDz1 committed; catch skips normal release tail `0x372AC..0x372B8`; any selector side effect before throw may persist.

Unprotected tail exceptions propagate.

## Scout after R-146
Next earlier LSDA-bearing function:
- `371F4 -> LSDA 0x1140EC`.
- Same exact action-1 shape around DDz1 `dropServerNoticeNow`.
- Protected `0x37208..0x3721C -> 0x3722C`; tail `0x3721C..0x3723C` unprotected.

Next after that:
- `371AC -> LSDA 0x1140D8`.
- Same shape around DDz1 `dropOverdueNotice`.
- Protected `0x371C0..0x371D4 -> 0x371E4`.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
