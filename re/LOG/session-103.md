# LOG/session-103.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-102 commit d7fd24d; complete R-102 by promoting the exact data-only `41F50` private scene-settings mutation exception outcome. Per user workflow, commit locally but do not push._

## R-102 — evidence source

Reviewed:
- `41F50.c`;
- raw ARM64 for `41F50` from the first arm64 FAT slice;
- Mach-O `__unwind_info` / `__gcc_except_tab` mapping;
- existing R-088 private `_frame` / `_foreground` plan;
- existing R-101 `421CC` flag-clear exception outcome.

The first arm64 FAT slice begins at file offset `0x4000`.

`__unwind_info` maps:
- `41F50` -> LSDA `0x114E8C`.

Decoded call-site table:
- `0x41F50..0x41F9C` -> no landing pad;
- `0x41F9C..0x41FF8` -> landing `0x42108`, action 5;
- `0x41FF8..0x42020` -> no landing pad;
- `0x42020..0x42068` -> landing `0x4210C`, action 5;
- `0x42068..0x42074` -> no landing pad;
- `0x42074..0x420AC` -> landing `0x4210C`, action 5;
- `0x420AC..0x420F8` -> no landing pad;
- `0x420F8..0x420FC` -> landing `0x4210C`, action 5;
- `0x420FC..0x42124` -> no landing pad.

`0x42108` is only a branch into `0x4210C`, so all typed catches share one catch body.

## Protected region 1 — frame private-ivar path

`0x41F9C..0x41FF8` covers:
- private `_frame` lookup through `9C24C`;
- ivar/type-encoding validation;
- unsupported-type diagnostic through `9C2C4`;
- ivar-offset resolution immediately before the raw frame write.

The raw memory stores that actually write origin/size begin at `0x41FF8`, outside this typed protected range.

An exception in the protected frame preparation path therefore goes to the common catch and skips the later foreground/update/control logic entirely.

## Protected region 2 — foreground private-ivar path

`0x42020..0x42068` covers:
- private `_foreground` lookup through `9C24C`;
- exact `c` / `B` type validation;
- unsupported-type diagnostic through `9C2C4`.

An exception there uses the same common catch and abandons the rest of the mutation flow.

## Protected region 3 — force-IO / orientation repair / nested flag-clear

`0x42074..0x420AC` covers:
- `42124` force-IO toggle read;
- landscape/global orientation checks;
- private integer write through `9C3BC` when repair is required;
- nested `421CC` other-settings flag clear.

Any typed exception from those helper boundaries is swallowed by `41F50` itself and does not continue into its normal failure-budget handling.

This is distinct from the inner `421CC` catch: an exception already swallowed by `421CC` never reaches this outer catch, while an exception that escapes another protected helper in this range does.

## Protected region 4 — direct foreground offset resolution

Normal foreground-write setup branches to `0x420F8` after exact `c`/`B` type acceptance.

`0x420F8..0x420FC` protects the ivar-offset resolver call immediately before the raw byte write at `0x420FC..0x42100`.

An exception while resolving that offset is swallowed by the common catch, so the raw byte write is skipped.

## Common catch continuation

Raw ARM64:
- `0x42108`: branch to `0x4210C`;
- `0x4210C`: compare catch type;
- expected type -> begin catch, end catch;
- `0x4211C`: branch to `0x420C8`;
- unexpected type -> resume unwind at `0x42120`.

`0x420C8` is the final normal-return path:
- retain the original settings object;
- release the retained outer object;
- autorelease-return the retained object.

Therefore every typed `41F50` exception:
- is swallowed;
- skips all remaining private mutation/control work;
- skips any later private helper calls;
- returns through normal final retain/cleanup/return.

## Failure-budget nuance

The normal failure-budget logic is at `0x420AC..0x420C4`:
- combine frame/foreground handled bits;
- when either is unhandled and `dword_162F34 >= 1`, decrement `dword_162F34`.

The common catch jumps directly to `0x420C8`.

So a typed exception in any protected range bypasses the failure-budget decrement entirely, regardless of what the normal handled-bit state would have been.

This is promoted explicitly as `shouldSkipFailureBudgetDecrement = YES` rather than inferred indirectly from the general skip-mutation flag.

## No reason-probe path

The common catch does not call `41BA0` and does not inspect the caught exception's `reason`.

There is therefore no probe-count or nested-probe metadata in the R-102 outcome.

## Promoted runtime contract

Added:
- `DDSceneSettingsPrivateIvarExceptionOutcome`;
- `DDResolveSceneSettingsPrivateIvarExceptionOutcome(void)`.

Exact constant outcome:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingPrivateMutation = YES`;
- `shouldSkipFailureBudgetDecrement = YES`;
- `shouldReturnThroughNormalCleanup = YES`.

## Explicit exclusions

R-102 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke `9C24C`, `9C2C4`, `9C3BC`, `42124`, or `421CC`;
- inspect or dereference private ivars;
- resolve private ivar offsets;
- write `_frame` or `_foreground`;
- mutate `dword_162F34`;
- record diagnostics;
- mutate scene settings or any other global state.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — 400D0

`400D0` already has data-only identity-routing and post-frame/orientation update-gate contracts, but its exception continuations have not yet been promoted.

Mach-O unwind mapping:
- `400D0` -> LSDA `0x114AD8`.

Decoded call-site table:
- `0x400D0..0x4014C` -> no landing pad;
- `0x4014C..0x4018C` -> `0x40478`, action 7;
- `0x4018C..0x4019C` -> no landing pad;
- `0x4019C..0x401C8` -> `0x4040C`, action 7;
- `0x401C8..0x401D8` -> no landing pad;
- `0x401D8..0x40204` -> `0x403F0`, action 7;
- `0x40204..0x4020C` -> no landing pad;
- `0x4020C..0x40210` -> `0x403EC`, action 7;
- `0x40210..0x40218` -> `0x403E8`, action 5;
- `0x40284..0x40290` -> `0x40428`, action 5;
- `0x40294..0x402A0` -> `0x403E4`, action 5;
- `0x402A0..0x402E4` -> no landing pad;
- `0x402E4..0x402FC` -> `0x40428`, action 5;
- `0x402FC..0x40318` -> no landing pad;
- `0x40318..0x40364` -> `0x40428`, action 5;
- `0x40364..0x40390` -> no landing pad;
- `0x40390..0x403A8` -> `0x40438`, action 7;
- `0x403A8..0x40458` -> no landing pad;
- `0x40458..0x4045C` -> `0x4046C`, cleanup/action 0;
- `0x4045C..0x4049C` -> no landing pad.

Because `400D0` has multiple action-7, action-5, and cleanup continuations across routing, settings, private executors, and callback-adjacent work, it should be decoded as a separate batch rather than folded into R-102.

## Next

R-103 after compiler green:
- decode `400D0` LSDA `0x114AD8` + raw ARM64 around host/aux identity routing, scene/settings reads, frame/orientation decision paths, `3F5C0` / `3E670`, and each catch/cleanup continuation;
- promote only evidence-safe data-only continuation/probe/unwind metadata;
- keep private traversal/executors, side effects, counter/global mutation, and exception synthesis excluded.
