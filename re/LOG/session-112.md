# LOG/session-112.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-111 commit a9914d4; complete R-111 by promoting exact data-only `3F100` activating-entity setter exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-111 — evidence source

Reviewed:
- `3F100.c`;
- raw ARM64 for `3F100` from the first arm64 FAT slice;
- Mach-O LSDA `0x114948`.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3F100 -> LSDA 0x114948`.

Decoded call-site table:
- `0x3F100..0x3F128` -> no landing pad;
- `0x3F128..0x3F144` -> landing `0x3F158`, action 1;
- `0x3F144..0x3F164` -> no landing pad.

## Protected activating-entity setter range

Raw ARM64 for `0x3F128..0x3F144` covers exactly:
- `respondsToSelector:setActivatingEntity:`;
- if supported, loading the captured entity from block offset `+0x20`;
- optional `setActivatingEntity:` send.

No other call in `3F100` is covered by the LSDA entry.

## Landing `0x3F158` — unconditional catch-all continuation

Raw ARM64:
- `0x3F158`: begin catch;
- `0x3F15C`: end catch;
- `0x3F160`: branch to `0x3F144`.

`0x3F144` is the normal retained-object release/return path.

There is no catch discriminator comparison before begin-catch, so there is no evidence for a distinct nonmatching-type branch inside this function.

Exact local exception semantics:
- swallow the protected exception locally;
- do not retry the capability test;
- do not retry `setActivatingEntity:`;
- abandon the setter operation;
- release the retained receiver and return normally.

There is no reason probe, diagnostic counter, global/state mutation, or alternate continuation.

## Promoted runtime contract

Added:
- `DDActivatingEntitySetterExceptionOutcome`;
- `DDResolveActivatingEntitySetterExceptionOutcome(void)`.

Exact constant outcome:
- `shouldSwallowException = YES`;
- `shouldContinueCleanupAfterCatch = YES`.

A site enum is unnecessary because the LSDA has one protected range and one local continuation.

No unwind/nonmatching-type field is exposed because raw ARM64 contains no discriminator branch at the landing.

## Explicit exclusions

R-111 does not:
- synthesize exceptions;
- execute begin-catch/end-catch runtime APIs;
- invoke `respondsToSelector:setActivatingEntity:`;
- invoke `setActivatingEntity:`;
- dereference/use the captured entity as a runtime object;
- mutate the responder, entity, counters, diagnostics, or globals;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3F224`

Mach-O maps:
- `3F224 -> LSDA 0x114960`.

Decoded call-site table:
- `0x3F224..0x3F248` -> no landing pad;
- `0x3F248..0x3F26C` -> landing `0x3F350`, action 5;
- `0x3F26C..0x3F294` -> no landing pad;
- `0x3F294..0x3F29C` -> landing `0x3F34C`, action 5;
- `0x3F2B8..0x3F2D4` -> landing `0x3F354`, action 5;
- `0x3F310..0x3F324` -> landing `0x3F348`, action 5;
- `0x3F324..0x3F36C` -> no landing pad.

Raw ARM64 shows all small landing stubs `0x3F348`, `0x3F34C`, and `0x3F350` branch to common catch `0x3F354`.

Common catch:
- compare catch discriminator with expected value 1;
- expected type:
  - begin catch;
  - end catch;
  - branch to `0x3F32C`, skipping directly to final request-argument cleanup/return;
- nonmatching type:
  - branch to `0x3F368`;
  - resume unwind.

Protected regions cover:

### Request dictionary / bundle lookup
`0x3F248..0x3F26C` includes:
- notification/request `userInfo` retrieval;
- retain-autoreleased handling;
- `objectForKeyedSubscript:@"bundleIdentifier"`;
- retain-autoreleased bundle result.

Expected exception here skips all host-slot matching and request dispatch and goes to cleanup.

### Bundle length gate
`0x3F294..0x3F29C` covers the candidate bundle `length` read used before host-slot scanning.

Expected exception here skips slot matching and request dispatch.

### Host-slot matching
`0x3F2B8..0x3F2D4` covers per-slot hosted-bundle `length` and `isEqualToString:` checks while excluding CarPlay-marked slots.

Expected exception here aborts the slot scan and skips request dispatch.

### Final request dispatch
`0x3F310..0x3F324` covers the final `89D8(bundle, 1, qword_162F08, byte_163DC0, width, height)` call when selected width is positive.

Expected exception from `89D8` is swallowed and function proceeds directly to cleanup/return; no retry is visible.

Therefore R-112 can remain compact:
- all protected expected exceptions -> swallow + final cleanup/return;
- nonmatching discriminator -> resume unwind;
- no reason probe or per-site alternate continuation.

## Next

R-112 after compiler green:
- promote exact `3F224` common catch→cleanup and nonmatching-type unwind metadata;
- keep notification dictionary traversal, string/slot matching, `89D8` invocation, hosting state mutation, exception synthesis, and unwind execution excluded.
