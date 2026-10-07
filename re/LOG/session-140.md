# LOG/session-140.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-139 commit `f988197`; decode and promote exact data-only `38240` keypane/aux-scene host-construction exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`, HEAD `f988197`, clean and synchronized with origin.
- User confirmed session-139 macOS CI/compiler GREEN.

## Target
- Function: `sub_38240`.
- LSDA: `0x1141D0`.
- Large keypane/aux-scene host construction routine.

## Exact call-site table
16 entries, with ten action-5 ranges:
1. `0x3852C..0x38590 -> 0x388E0`
2. `0x38598..0x385A4 -> 0x388E0`
3. `0x385A8..0x38680 -> 0x388E4`
4. `0x38688..0x386AC -> 0x388E4`
5. `0x386BC..0x386C0 -> 0x388D4`
6. `0x386C0..0x386D8 -> 0x388D0`
7. `0x386D8..0x3870C -> 0x388DC`
8. `0x3875C..0x387A0 -> 0x388DC`
9. `0x38814..0x38818 -> 0x388D8`
10. `0x38878..0x38890 -> 0x388D8`

All aliases converge at common typed catch `0x388E4`. Unprotected gaps have no local catch.

## Range mapping
- Range 1: outer UIView allocation/frame, clips, clearColor acquisition/retain, background setter.
- Range 2: outer `setOpaque:NO`.
- Range 3: inner UIView creation, aux-scene transform/frame/autoresizing/addSubview, inner transform/center, clear background.
- Range 4: inner opaque + inner→outer + outer→splitHost insertion.
- Range 5: `38E14` hide-gap read.
- Range 6: left `38EF8` hide-key creation/retain.
- Range 7: commit left key, create/retain right key, add both key subviews.
- Unprotected `0x3870C..0x3875C`: store globals C78 outer, C68 inner, C70 aux scene, C88 left key, C90 right key.
- Range 8: `39260` geometry sync plus stores to CB8/CC0/CC8/CD0, C98/CD8; range ends after CACurrentMediaTime call but before CE0 store.
- Unprotected after range 8: store CE0, increment/store CE8, schedule 1.5s dispatch, call `39810` which schedules a 3s dispatch.
- Range 9: `39884` transparency wrapper.
- Unprotected after range 9: schedule four staggered delayed main-queue blocks.
- Range 10: bring outer view to front + `30F48(1)` activation.

## Common expected catch
At `0x388E4` expected type:
- begin catch and retain caught object;
- load/nil/release global C88;
- load/nil/release global C90;
- call teardown on retained controller/DDz2 x21;
- load/nil/release global C78;
- release caught object;
- end catch;
- force result false;
- release retained aux-scene x22;
- release retained controller x21;
- branch to common path that releases splitHost x20 and input x19.

Nonmatching discriminator resumes unwind at `0x38964`.

The catch does **not** explicitly clear C68 or C70. No additional teardown helper side effects are inferred.

## Site timing and persistence
- Outer local release can be bypassed at all ten typed sites once construction has progressed within the site.
- Inner local release can be bypassed from range 3 onward.
- Temporary clearColor release can be bypassed in range 1 and range 3.
- Range 4 may already have changed hierarchy before throw.
- From range 5 onward, outer/inner hierarchy insertion definitely completed.
- Range 7 may already have inserted left/right key subviews and can bypass committed key releases.
- From range 8 onward, both key subviews definitely completed and all five view globals were stored.
- At range 8 catch explicitly clears C78/C88/C90 but does not locally clear C68/C70. Geometry sync may already have started and CB8/CC0/CC8/CD0/C98/CD8 can be partially committed depending on throw point.
- From range 9 onward, geometry/size/flag stores, CE0, incremented CE8, and 1.5s + 3s delayed dispatch work are definitely committed before protected call.
- Range 9 may already have applied part of `39884` transparency before a propagated exception.
- Range 10 begins only after `39884` returned and four staggered dispatches were scheduled. Bring-to-front may already have applied, and `30F48(1)` activation may already have started before throw.
- None of the late committed state above is explicitly rolled back by the local catch.

## Promoted runtime contract
Added:
- `DDKeyPaneHostConstructionExceptionSite` with ten protected semantic sites plus unprotected.
- `DDKeyPaneHostConstructionExceptionOutcome`.
- `DDResolveKeyPaneHostConstructionExceptionOutcome(site)`.

The resolver exposes only:
- expected swallow/false continuation;
- explicit C88/C90/C78 clears;
- teardown-request flag;
- aux/controller then splitHost/input cleanup continuation;
- site-aware local release-bypass and hierarchy/key insertion timing;
- all-five-global commit boundary;
- explicit C68/C70 non-clear metadata;
- geometry/flag partial-vs-definite timing;
- CE0/CE8 and delayed-dispatch commit timing;
- late transparency/fronting/activation possible side effects;
- unprotected propagation and nonmatching unwind.

It never constructs views/scenes, mutates globals, schedules work, invokes teardown, changes ownership, catches exceptions, or executes unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.
Final verifier + `git diff --check` run immediately before commit.

## Scout for next batch — 3815C
Next earlier LSDA-bearing function:
- `3815C -> LSDA 0x1141AC`.
- Role: read plist file and return NSDictionary or nil.

Exact table:
1. `0x3815C..0x38184` no landing.
2. `0x38184..0x38194 -> 0x38208`, action 5: NSData file read + retain.
3. `0x381A4..0x381DC -> 0x3820C`, action 5: plist decode + retain + NSDictionary class/type check.
4. `0x381DC..0x38240` no landing.

Both expected catches converge to begin/end catch, set result nil, release input x19, and return nil.
- First range ends before `mov x20,x0`, so no committed NSData cleanup bypass is asserted.
- Second range starts with retained NSData x20 committed; catch bypasses its explicit release at `0x381FC`.
- Within the second range, retained plist x21 is committed at `0x381C0`; exceptions during later class/type check can additionally bypass x21 release at `0x381EC`.
- Nonmatching type resumes unwind at `0x3823C`.
- Unprotected ranges propagate.
Next earlier unwind-bearing function after 3815C is `37A7C -> 0x11418C`.

Known unresolved remain: `73E8/80D0`, full `7E908`, and jailbroken-device smoke testing.
