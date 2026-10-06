# LOG/session-111.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-110 commit 517beec; complete R-110 by promoting exact data-only `3EFD4` string-selector helper exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-110 — evidence source

Reviewed:
- `3EFD4.c`;
- raw ARM64 for `3EFD4` from the first arm64 FAT slice;
- Mach-O LSDA `0x114924`;
- callers including `3FBC8` and `41730`, which use this helper for caller-supplied object/string selector extraction.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3EFD4 -> LSDA 0x114924`.

Decoded call-site table:
- `0x3EFD4..0x3EFF4` -> no landing pad;
- `0x3EFF4..0x3F000` -> landing `0x3F050`, action 7;
- `0x3F004..0x3F034` -> landing `0x3F054`, action 5;
- `0x3F034..0x3F088` -> no landing pad.

## Normal helper behavior

The helper:
1. retains the supplied object;
2. if non-nil, tests `respondsToSelector:` with a caller-supplied selector;
3. if supported, invokes that selector and retains the autoreleased result;
4. checks whether the result is an `NSString` instance;
5. returns a retained/autoreleased string only when the type check succeeds; otherwise returns nil.

The reconstruction does not reproduce this private selector/runtime traversal. R-110 only promotes the exception continuation semantics.

## Protected capability-check range

Protected range:
- `0x3EFF4..0x3F000` -> landing `0x3F050`, action 7.

Raw ARM64 covers:
- receiver setup;
- caller-supplied selector setup;
- `respondsToSelector:` runtime send.

Landing `0x3F050` is only a branch to the common catch at `0x3F054`.

Therefore an expected protected exception from the capability check does not attempt the selector send afterward; it goes directly to the common catch/fallback.

## Protected selector-send / string-type range

Protected range:
- `0x3F004..0x3F034` -> landing `0x3F054`, action 5.

Raw ARM64 covers:
- caller-supplied selector send;
- retain-autoreleased-return handling;
- `NSString` class lookup;
- runtime kind-of-class validation.

Any expected exception from those operations reaches the same common catch as the capability range.

## Common catch `0x3F054`

Raw ARM64:
- `0x3F054`: compare catch discriminator with expected value 1;
- nonmatching value -> branch `0x3F084` -> resume unwind;
- expected value:
  - `0x3F05C`: begin catch;
  - `0x3F060`: end catch;
  - fall through to `0x3F064`;
- `0x3F064`: set string result register to nil;
- release the retained input object;
- return nil through autorelease-return handling.

Exact expected-catch semantics:
- swallow locally;
- do not retry `respondsToSelector:`;
- do not retry the caller-supplied selector;
- skip all remaining string type validation;
- force returned string to nil;
- continue normal retained-input cleanup.

There is no reason probe, diagnostic counter, state mutation, or alternate selector fallback inside this helper.

## Nonmatching catch discriminator

When the landing discriminator is not the expected type:
- common catch branches to `0x3F084`;
- runtime resume-unwind is invoked.

Promoted metadata:
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

No foreign/nonmatching exception is synthesized by the reconstruction.

## Promoted runtime contract

Added:
- `DDStringSelectorExceptionOutcome`;
- `DDResolveStringSelectorExceptionOutcome(void)`.

Exact constant outcome for the expected typed path:
- `shouldSwallowException = YES`;
- `shouldReturnNilValue = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

A site enum is unnecessary because both protected ranges converge on the same common catch and return behavior.

## Relationship to `3FBC8`

`3FBC8` invokes `3EFD4` for several bundle/private-identifier fallbacks. There are therefore two distinct catch layers in the original:
- `3EFD4` can swallow its own protected selector/type-check exception and return nil to `3FBC8`;
- if an exception escapes outside `3EFD4`'s protected ranges or arises in surrounding `3FBC8` protected work, `3FBC8`'s separate LSDA may catch it and force the entire identity resolution to nil.

R-110 intentionally keeps the helper outcome separate from `DDResolveSceneIdentityResolutionExceptionOutcome` so callers can preserve this layering in evidence-driven simulations without invoking either private path.

## Explicit exclusions

R-110 does not:
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs;
- invoke caller-supplied selectors;
- invoke `respondsToSelector:` as part of this private helper;
- invoke runtime NSString class lookup/kind checking;
- retain/release real private objects;
- mutate host/aux state, counters, diagnostics, or globals.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3F100`

Mach-O maps:
- `3F100 -> LSDA 0x114948`.

Decoded call-site table:
- `0x3F100..0x3F128` -> no landing pad;
- `0x3F128..0x3F144` -> landing `0x3F158`, action 1;
- `0x3F144..0x3F164` -> no landing pad.

Raw ARM64 shows the protected range covers exactly:
- `respondsToSelector:setActivatingEntity:`;
- optional `setActivatingEntity:` send using the captured entity at block offset `+0x20`.

Landing `0x3F158`:
- unconditionally begin-catches;
- end-catches;
- branches to `0x3F144`, the normal retained-object cleanup/return path.

There is no discriminator comparison, reason probe, retry, counter mutation, or alternate continuation.

Thus R-111 can remain compact:
- protected exception -> local catch-all swallow + cleanup/return;
- no nonmatching-type branch to model.

## Next

R-111 after compiler green:
- promote exact `3F100` protected `setActivatingEntity:` capability/send catch-all swallow+cleanup outcome;
- keep private setter invocation, captured-entity access, exception synthesis, state mutation, and landing-pad execution excluded.
