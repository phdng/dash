# LOG/session-164.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-163 commit `316f678`; decode and promote exact data-only `345E4` server-notice UI exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `316f678`.
- Working tree clean.
- User confirmed session-163 macOS CI/compiler GREEN.
- Local tracking still reported ahead 2; assistant did not fetch/push.

## Target
- Function: `sub_345E4`.
- LSDA: `0x113CD4`.
- Role: no-notice/text/backdrop admission, existing-notice removal, label/container construction and styling, hierarchy attach/current-notice store, presentation/deadline/6s delayed cleanup, and failed-present teardown.

## Exact LSDA call-site table
1. `0x3461C..0x34638 -> 0x34BA8`, action 7.
2. `0x34638..0x3466C` unprotected.
3. `0x3466C..0x34688 -> 0x34BA8`, action 7.
4. `0x34698..0x346C0 -> 0x34B9C`, action 5.
5. `0x346C0..0x346D0` unprotected.
6. `0x346D0..0x346D8 -> 0x34B94`, action 5.
7. `0x3470C..0x34710 -> 0x34B90`, action 5.
8. `0x34718..0x34770 -> 0x34BA0`, action 5.
9. `0x34770..0x34780` unprotected.
10. `0x34780..0x3479C -> 0x34BA0`, action 5.
11. `0x3479C..0x347A4` unprotected.
12. `0x347A4..0x347C8 -> 0x34BA0`, action 5.
13. `0x347F4..0x34804 -> 0x34B8C`, action 5.
14. `0x34824..0x3488C -> 0x34BA4`, action 5.
15. `0x3488C..0x34894` unprotected.
16. `0x34894..0x348BC -> 0x34BA4`, action 5.
17. `0x348BC..0x348C4` unprotected.
18. `0x348C4..0x348E0 -> 0x34BA4`, action 5.
19. `0x348E0..0x348EC` unprotected.
20. `0x348EC..0x34904 -> 0x34BA4`, action 5.
21. `0x34904..0x3490C` unprotected.
22. `0x3490C..0x34930 -> 0x34BA4`, action 5.
23. `0x34930..0x34940` unprotected.
24. `0x34940..0x34994 -> 0x34BA4`, action 5.
25. `0x34994..0x349B0` unprotected.
26. `0x349B0..0x349F0 -> 0x34B98`, action 5.
27. `0x349F0..0x34B0C` unprotected.
28. `0x34B0C..0x34B14 -> 0x34B98`, action 5.
29. `0x34B14..0x34C00` unprotected.

## Action-chain distinction
Action index 7:
- typed filter 1 only.

Action index 5:
- typed filter 1;
- cleanup action 0.

Thus:
- marker/text early gates are typed-only;
- later contentView/UI-build/presentation/remove ranges carry typed+cleanup action metadata;
- expected typed exceptions share the same catch;
- nonmatching exceptions resume unwind.

## Common expected catch
Landing aliases `0x34B8C/90/94/98/9C/A0/A4` all branch to `0x34BA8`.

Raw catch:
```
34BA8 cmp w1,#1
34BAC b.ne 34BFC
34BB0 objc_begin_catch
34BB4 load captured/byref reason slot
34BC0 load CFString constant 0x147C18
34BC8 store new reason
34BCC objc_release(previous reason)
34BF8 tail objc_end_catch
34BFC resume unwind
```

The string identity is confirmed two ways:
- pointer map: `34BC0 -> 147C18 -> cfstr_Threw`;
- decompile `34B8C.c`: `*reasonSlot = CFSTR("threw")`.

Therefore expected catch:
1. stores `"threw"` into captured reason;
2. then releases previous reason;
3. then ends catch / returns.

The reason store definitely precedes the previous-reason release.

The catch-internal release is outside local protected call-site coverage; if it throws, local code does not swallow it.

## Explicit normal early-exit reasons
The normal non-exception path also writes:
- marker exists -> `"kill-switch"`;
- invalid/empty text -> `"no-text"`;
- missing backdrop -> `"no-backdrop"`;
- too-small backdrop -> `"box-too-small"`;
- failed presentation -> `"present-failed"`.

These are distinct from exception fallback `"threw"`.

## Action-7 marker probe
Protected `0x3461C..0x34638`:
- NSFileManager defaultManager;
- retain-autoreleased manager;
- manager commit x20;
- fileExistsAtPath `/var/tmp/duodash_ab_nonotice`.

Semantic split:
- manager acquisition may throw before x20 commit;
- file probe begins after x20 committed.

Expected catch:
- sets reason to `"threw"`;
- manager normal release at `0x34640` may be bypassed.

Unprotected bridge commits file-probe result, releases manager, and writes `"kill-switch"` if present.

## Action-7 text validation
Protected `0x3466C..0x34688`:
- NSString class/type check;
- text length.

Expected catch:
- sets reason `"threw"`;
- returns.

Normal invalid/empty result writes `"no-text"`.

No UI object ownership exists yet.

## ContentView/backdrop acquisition
Protected `0x34698..0x346C0`:
- first contentView getter + retain -> x21 commit;
- second contentView getter + retain;
- range ends before x20 second-backdrop commit.

Site-aware contract:
- first acquisition may fail before commit;
- second acquisition begins with x21 committed;
- x21 release can be bypassed;
- second retained result may exist temporarily without x20 commit.

Unprotected `0x346C0..0x346D0`:
- commits second backdrop x20;
- releases first x21;
- null-checks x20.

Normal missing backdrop writes `"no-backdrop"`.

## Backdrop bounds
Protected `0x346D0..0x346D8`:
- sends `bounds` to committed retained backdrop x20.

Range ends before returned width/height are captured into d11/d10.

Expected catch:
- reason `"threw"`;
- x20 final release at `0x34B5C` can be bypassed;
- bounds dimensions are uncommitted.

Normal too-small dimensions write `"box-too-small"` and release x20.

## Existing notice removal
Protected `0x3470C..0x34710`:
- calls `removeServerNotice`.

Before call:
- retained backdrop x20 committed;
- previous `byte_163C38` copied to w27.

If call throws:
- remove side effects may already have happened;
- expected catch writes `"threw"`;
- backdrop release can be bypassed.

## Label construction/text/font
Protected `0x34718..0x34770`:
- UILabel alloc/init -> x21 commit;
- setText;
- UIFont systemFontOfSize:weight: + retain -> x22 commit;
- setFont.

Semantic split:
- label construction may fail before x21 commit;
- text mutation begins after label commit;
- font mutation begins after retained font commit.

Expected catch can bypass:
- retained label final release;
- retained font release at `0x34774`;
- retained backdrop release.

Text/font side effects may persist.

Font release is unprotected.

## Label text color
Protected `0x34780..0x3479C`:
- UIColor whiteColor + retain -> x22 commit;
- setTextColor.

Expected catch:
- retained color release at `0x347A0` can be bypassed;
- text-color mutation may persist;
- label/backdrop releases can be bypassed.

Color release is unprotected.

## Label properties
Protected `0x347A4..0x347C8`:
- setNumberOfLines:0;
- setTextAlignment:1;
- setUserInteractionEnabled:NO.

A later exception preserves earlier property writes.
Expected catch skips label/backdrop normal cleanup.

## Label sizing
Protected `0x347F4..0x34804`:
- sizeThatFits.

The protected range ends before returned dimensions are consumed/canonicalized.

Caught exception:
- sizing result remains uncommitted;
- label/backdrop cleanup may be bypassed;
- reason becomes `"threw"`.

## Container construction/background
Protected `0x34824..0x3488C`:
- UIView alloc/initWithFrame -> x22 container commit;
- UIColor colorWithWhite:alpha: + retain -> x23 commit;
- setBackgroundColor.

Semantic split:
- container construction may fail before x22 commit;
- background mutation begins after retained color commit.

Expected catch can bypass:
- background color release;
- container release;
- label release;
- backdrop release.

Background mutation may persist.

## Corner radius
Protected `0x34894..0x348BC`:
- container layer acquisition + retain -> x23 commit;
- setCornerRadius.

Expected catch:
- retained layer release at `0x348C0` can be bypassed;
- radius mutation may persist;
- container/label/backdrop releases can be bypassed.

## Border width
Protected `0x348C4..0x348E0`:
- container layer acquisition + retain -> x23 commit;
- setBorderWidth:1.0.

Expected catch mirrors corner-radius lifetime and can preserve partial border-width write.

## Border-color acquisition
Protected `0x348EC..0x34904`:
- UIColor colorWithWhite:alpha: + retain.

Range ends before x23 border-color commit at `0x34904`.

Thus this site exposes temporary border-color acquisition/release-bypass only.

The following retainAutorelease bridge is unprotected.

## Border-color layer mutation
Protected `0x3490C..0x34930`:
- CGColor retrieval from committed border color x23;
- container layer getter + retain -> x25 commit;
- setBorderColor.

At setter:
- border color is definitely committed;
- style layer is definitely committed.

Expected catch can bypass x25/x23 normal releases and preserve border-color mutation.

Their normal releases are unprotected at `0x34930..0x34940`.

## Final properties + hierarchy
Protected `0x34940..0x34994`:
- setClipsToBounds:YES;
- setOpaque:NO;
- setUserInteractionEnabled:NO on container;
- setFrame on label;
- addSubview label -> container;
- addSubview container -> backdrop.

Earlier writes/hierarchy changes are not rolled back if a later call throws.

Expected catch:
- writes reason `"threw"`;
- bypasses container/label/backdrop releases.

## Current-notice strong store
Unprotected `0x34994..0x349B0`:
- strong-stores container x22 into owner/current notice slot +0x28;
- reads presentation-state byte +0x58.

Therefore all protected presentation/failure-remove sites begin after current notice strong store returned successfully.

Exceptions in this store itself are unprotected and may partially mutate ownership.

## Protected presentation path
Protected `0x349B0..0x349F0`.

If owner presentation byte is not already set:
- calls `present`;
- false result branches to failed-present remove path.

Successful/pre-enabled continuation:
- updates `byte_163C38`;
- CACurrentMediaTime;
- stores deadline `qword_163C40 = now + 6.0 + 0.75`;
- disables user interaction on backdrop contentView.

Semantic ordering:
- PresentationCall: current-notice store definitely committed; present may have side effects before throw.
- PresentationStateAndDeadline: admission already passed; state byte is definitely written before media-time/deadline work; deadline may remain uncommitted if media-time call throws.
- BackdropInteractionDisable: state byte + deadline definitely committed before setter; interaction disable may apply before throw.

Expected catch always sets reason `"threw"`; no rollback of current notice/global state/deadline/UI mutations.

## Success weak/dispatch tail
Unprotected `0x349F0..0x34B0C` on successful/pre-enabled presentation path:
- init weak owner;
- dispatch_time for 6s;
- copy weak into block;
- retain container into block capture;
- dispatch_after main queue;
- release strong capture;
- destroy copied weak;
- destroy original weak;
- normal container/label/backdrop cleanup.

At entry:
- current-notice store committed;
- presentation state byte committed;
- deadline committed;
- backdrop interaction-disable call completed.

Exceptions propagate.

Depending on site:
- weak capture may be initialized;
- container block capture may be retained;
- delayed dispatch may already be scheduled.

No local typed catch covers this tail.

## Failed-present protected remove
Failed presentation is reachable only when:
- presentation byte was not already set;
- `present` returned false.

Protected `0x34B0C..0x34B14`:
- `removeFromSuperview` on container x22.

Before call:
- current-notice strong store committed;
- present definitely returned false.

If remove throws:
- partial removal may persist;
- expected catch writes reason `"threw"`;
- container/label/backdrop releases can be bypassed.

## Failed-present unprotected teardown
Unprotected `0x34B14..` after remove returns normally:
- if current-notice slot still equals container, clear slot and release old slot object;
- set captured reason to `"present-failed"`;
- release previous reason;
- release container x22;
- release label x21;
- release backdrop x20.

Exceptions propagate.

Possible persistent milestones:
- container removal definitely completed before tail;
- current-notice slot may already be cleared;
- captured reason may already be `"present-failed"`.

## Promoted runtime contract
Added:
- `DDServerNoticeBuildExceptionSite`;
- `DDServerNoticeBuildExceptionOutcome`;
- `DDResolveServerNoticeBuildExceptionOutcome(site)`.

Semantic sites cover:
- no-notice manager/file probe;
- text type/length;
- first/second backdrop;
- bounds;
- remove existing notice;
- label construction/text/font/text-color/properties/sizing;
- container construction/background/corner/border width/border color;
- final hierarchy/property writes;
- present/state+deadline/interaction disable;
- unprotected success weak-dispatch tail;
- failed-present remove;
- unprotected failed-present teardown;
- generic unprotected propagation.

Metadata records:
- action-7 vs action-5 chain family;
- expected typed swallow;
- confirmed catch reason `"threw"`;
- reason-store-before-old-release ordering;
- catch-internal release propagation;
- temporary-vs-committed manager/backdrop/label/container/style/color ownership;
- release bypass;
- UI/hierarchy/global side-effect persistence;
- current-notice store timing;
- presentation/deadline ordering;
- success dispatch milestones;
- failed-present removal/slot/reason milestones.

## Explicit exclusions
R-163 does not:
- access live files/preferences;
- build/mutate real UIKit objects;
- mutate real current-notice/global deadline state;
- call live presentation helpers;
- schedule live dispatch;
- retain/release live objects;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier precision pass:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 34524
Next earlier LSDA-bearing function:
- `34524 -> LSDA 0x113CB8`.

Exact table:
1. `0x34524..0x34598` unprotected.
2. `0x34598..0x345A4 -> 0x345B0`, action 1 catch-all.
3. `0x345A4..0x345C0` unprotected.

Reset-path prefix when flag byte +0xA9 == 1:
- clears +0xA9;
- writes -1 sentinel +0xB0;
- writes CGRectNull at +0xC0;
- clears +0x130/+0x131;
- clears +0x138;
- clears strong slot +0x140 and releases prior object;
- loads mutable collection +0x148.

Protected range:
- `removeAllObjects`;
- `teardownWindow`.

If flag is not set, control enters the protected range directly at `teardownWindow`.

Landing `0x345B0`:
- unconditional begin/end-catch;
- immediate return.

R-164 should distinguish:
- removeAllObjects after reset (all prior reset writes definitely committed; collection clear may apply; teardown skipped on catch);
- teardownWindow after reset (reset + removeAllObjects definitely completed; teardown may apply);
- teardownWindow without reset (no reset/collection-clear milestone);
- unprotected prefix failures, which propagate and may leave partial reset state.

## Scout after R-164 — 34250
Next earlier LSDA-bearing function:
- `34250 -> LSDA 0x113C60`.
- Role: resolve CarPlay CADisplay by external-device screen ID.

Exact LSDA table has 13 entries:
- many action-0 cleanup ranges;
- typed action-5 `0x34440..0x34448 -> 0x3448C` around bounds capability check;
- typed action-5 `0x3444C..0x34458 -> 0x34488` around bounds read.

Typed expected catch:
- begin/end-catch;
- releases retained candidate display x24;
- forces x24=nil;
- continues final collection/device cleanup;
- returns nil.

Action-0 cleanup/nonmatching paths resume unwind at `0x34520`.

R-165 should map CADisplay/AVExternalDevice acquisition, screenIDs/NSArray/firstObject ownership, displays enumeration, uniqueId match, candidate bounds capability/read, candidate nil fallback, and each cleanup-unwind range.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
