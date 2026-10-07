# LOG/session-119.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-118 commit d5fa917; complete R-118 by promoting exact data-only `3E33C` scene-resolver exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-118 — evidence source

Reviewed:
- `3E33C.c`;
- raw ARM64 for `3E33C` from the first arm64 FAT slice;
- Mach-O LSDA `0x114860`.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3E33C -> LSDA 0x114860`.

Decoded call-site table:
- `0x3E33C..0x3E3C8` -> no landing pad;
- `0x3E3C8..0x3E3EC` -> landing `0x3E3F4`, action 5;
- `0x3E3EC..0x3E428` -> no landing pad.

This helper therefore has a deliberate exception split between its primary `sceneIfExists` resolution path and its fallback `scene` path.

## Normal scene resolution structure

The helper retains the supplied object and returns nil for a nil input.

For a non-nil input it first prefers a dynamically-validated `sceneIfExists` selector:
- construct selector via `NSSelectorFromString("sceneIfExists")`;
- test `respondsToSelector:`;
- fetch runtime class;
- fetch instance method;
- read/validate method return type;
- when valid, invoke `sceneIfExists`;
- retain autoreleased returned scene and return it.

When that primary path is unavailable or has the wrong signature, the helper falls back to:
- `respondsToSelector:scene`;
- optional `scene` send;
- retain autoreleased returned scene.

## Primary `sceneIfExists` path — no local catch

Raw ARM64 `0x3E358..0x3E3BC` covers the primary work:
- `NSSelectorFromString`;
- capability check;
- object class lookup;
- instance-method lookup;
- `method_getReturnType`;
- return-type validation;
- optional primary selector send;
- retain-autoreleased handling.

Every one of those instructions/calls lies inside the LSDA range `0x3E33C..0x3E3C8`, whose call-site entry has `landing = none` / `action = 0`.

Therefore an exception from the primary path:
- is **not** swallowed by `3E33C`;
- does not fall back to `scene` because of a local catch;
- propagates out of the helper through normal Objective-C/foreign unwinding.

The reconstruction exposes only `exceptionWouldPropagate = YES` for this site. It does not synthesize or execute an unwind.

## Fallback `scene` path — protected typed catch

Protected range:
- `0x3E3C8..0x3E3EC` -> landing `0x3E3F4`, action 5.

Raw ARM64 covers:
- `respondsToSelector:scene`;
- optional `scene` send;
- retain-autoreleased handling.

Landing `0x3E3F4`:
- compare catch discriminator with expected value 1;
- expected value:
  - begin catch at `0x3E3FC`;
  - end catch at `0x3E400`;
  - fall through to `0x3E404`;
  - set scene result register to nil;
  - release retained input object;
  - return nil through autorelease-return handling;
- nonmatching value:
  - branch to `0x3E424`;
  - resume unwind.

Exact expected fallback-catch semantics:
- swallow locally;
- abandon the fallback selector operation;
- force scene result nil;
- perform normal retained-input cleanup;
- no retry;
- no reason probe;
- no alternate scene source after the catch.

## Promoted runtime contract

Added:
- `DDSceneResolverExceptionSite` with:
  - `PrimarySceneIfExistsPath`;
  - `FallbackScenePath`;
- `DDSceneResolverExceptionOutcome`;
- `DDResolveSceneResolverExceptionOutcome(site)`.

Primary site:
- `exceptionWouldPropagate = YES`;
- no swallow/nil/nonmatching-catch fields are set because no local catch exists.

Fallback site:
- `shouldSwallowException = YES`;
- `shouldReturnNilScene = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Unknown/None site returns an all-false outcome.

## Explicit exclusions

R-118 does not:
- construct or invoke `sceneIfExists` or `scene`;
- invoke `respondsToSelector:` as part of private resolution;
- inspect runtime classes/methods/type encodings;
- retain/release live scene objects;
- synthesize/catch Objective-C or foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3E02C`

Mach-O maps:
- `3E02C -> LSDA 0x114818`.

Decoded call-site table:
- `0x3E02C..0x3E05C` -> no landing pad;
- `0x3E05C..0x3E080` -> landing `0x3E27C`, action 5;
- `0x3E090..0x3E0B4` -> landing `0x3E278`, action 5;
- `0x3E0C4..0x3E0E8` -> landing `0x3E274`, action 5;
- `0x3E0F0..0x3E0FC` -> landing `0x3E268`, action 5;
- `0x3E0FC..0x3E10C` -> landing `0x3E264`, action 5;
- `0x3E10C..0x3E130` -> landing `0x3E26C`, action 5;
- `0x3E130..0x3E1B0` -> no landing pad;
- `0x3E1B0..0x3E23C` -> landing `0x3E270`, action 5;
- `0x3E23C..0x3E29C` -> no landing pad.

Small landing stubs:
- `0x3E264 -> 0x3E27C`;
- `0x3E268 -> 0x3E27C`;
- `0x3E26C -> 0x3E27C`;
- `0x3E270 -> 0x3E27C`;
- `0x3E274 -> 0x3E27C`;
- `0x3E278 -> 0x3E27C`.

All protected sites therefore converge on common typed catch `0x3E27C`.

### Protected diagnostic-summary stages

The protected ranges span:
- `sceneHandle` capability/send/retain;
- nested `scene` capability/send/retain;
- nested `settings` capability/send/retain;
- `NSSelectorFromString("isForeground")`;
- `NSSelectorFromString("deactivationReasons")`;
- `3E29C` selector-type probes and the foreground getter;
- later deactivation type probe/getter;
- `+[NSString stringWithFormat:]` formatting for deactivation reason and final `fg=%@ deact=%@` summary.

Normal unprotected branches still provide the ordinary `"-"`, `"no-scene"`, and `"no-settings"`-style outputs seen in the decompile.

### Common catch `0x3E27C`

Raw ARM64:
- compare catch discriminator with expected value 1;
- expected value:
  - begin catch;
  - end catch;
  - load fixed CFString object referenced at image address `0x147C18` into the return-value register;
  - branch to the normal final return path at `0x3E174`;
- nonmatching value:
  - branch to `0x3E298`;
  - resume unwind.

Thus the high-level expected-catch outcome is:
- swallow;
- replace the in-progress diagnostic summary with one fixed fallback CFString;
- return through the function's normal outer-input cleanup;
- no retry of any scene/settings/type/string-format operation.

The fixed CFString object's content was not promoted in R-118; R-119 should decode/verify it before exposing a literal value.

### Lifetime/cleanup nuance for R-119

Because every landing stub jumps directly to `0x3E27C`, the expected catch then branches to `0x3E174`, bypassing normal intermediate releases that would occur on some later successful paths (`x20`/`x21`/`x22`/formatted intermediates depending on the protected site reached).

R-119 should inspect each protected site's already-retained intermediates before deciding whether to expose site-specific release-bypass metadata. The reconstruction must not intentionally reproduce leaked/retained real objects; only control-flow metadata is appropriate.

## Next

R-119 after compiler green:
- decode the fixed fallback CFString referenced at `0x147C18`;
- promote exact `3E02C` expected catch -> fallback summary string + final return, and nonmatching catch -> resume unwind;
- add site-specific retained-intermediate cleanup-bypass metadata only where directly proven useful;
- keep scene/settings traversal, selector/type probes, NSString formatting, real object lifetime changes, exception synthesis, and unwind execution excluded.
