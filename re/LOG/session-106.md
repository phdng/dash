# LOG/session-106.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-105 commit 9cef813; complete R-105 by promoting the exact data-only `40AE8` presentation-update exception outcome. Per user workflow, commit locally but do not push._

## R-105 — evidence source

Reviewed:
- `40AE8.c`;
- raw ARM64 for `40AE8` from the first arm64 FAT slice;
- Mach-O `__unwind_info` / `__gcc_except_tab` mapping already scouted in session-105;
- existing `41BA0` bounded reason-probe contract.

The first arm64 FAT slice begins at file offset `0x4000`.

`__unwind_info` maps:
- `40AE8` -> LSDA `0x114C10`.

Decoded call-site table:
- `0x40AE8..0x40B40` -> no landing pad;
- `0x40B40..0x40B54` -> landing `0x40C18`, action 1;
- `0x40B54..0x40BB8` -> no landing pad;
- `0x40BB8..0x40BD4` -> landing `0x40BFC`, action 1;
- `0x40BD4..0x40C38` -> no landing pad;
- `0x40C38..0x40C3C` -> landing `0x40C4C`, cleanup/action 0;
- `0x40C3C..0x40C5C` -> no landing pad.

## Original callback catch — continue post-original evaluation

The hooked original callback is exactly:
- `0x40B40..0x40B54` -> landing `0x40C18`, action 1.

Raw ARM64 at `0x40C18`:
1. saves the thrown exception;
2. verifies expected catch type;
3. begins catch;
4. retains the caught exception;
5. calls `41BA0(exception)` at `0x40C38`;
6. releases the retained exception;
7. ends catch;
8. branches back to `0x40B54`.

`0x40B54` is not cleanup. It is the beginning of the post-original presentation-update policy:
- inspect cached `dword_162F3C` nopresupdate state;
- if unresolved, probe `/var/tmp/duodash_ab_nopresupdate` through NSFileManager;
- if not disabled and hosting is active, test `_updateFrameAndTransform` capability and potentially send it;
- then release the retained callback arguments.

Therefore an original-callback exception:
- is swallowed;
- original is not retried;
- applies the existing `DDResolveExceptionReasonProbeDecision` contract;
- after a normal probe completion, continues post-original evaluation rather than returning directly.

Promoted metadata:
- `shouldSwallowException = YES`;
- `shouldApplyReasonProbeDecision = YES`;
- `probeExceptionWouldResumeUnwind = YES`;
- `shouldContinuePostOriginalEvaluationAfterProbe = YES`.

## Nested reason-probe exception

The `41BA0` call itself is protected separately:
- `0x40C38..0x40C3C` -> landing `0x40C4C`, cleanup/action 0.

Raw ARM64 at `0x40C4C`:
- preserves the newly thrown exception;
- ends the outer catch;
- falls into unwind/resume at `0x40C54`.

Thus post-original evaluation occurs only if the reason probe completes normally.

## Nopresupdate file-manager probe — no local catch

The unresolved nopresupdate-cache path is inside:
- `0x40B54..0x40BB8` -> no landing pad.

The actual file-manager work is approximately `0x40B68..0x40B98`:
- obtain `+[NSFileManager defaultManager]`;
- retain autoreleased result;
- call `fileExistsAtPath:` for `/var/tmp/duodash_ab_nopresupdate`;
- store the result into `dword_162F3C`;
- release the file manager.

Because this entire range has no landing pad in `40AE8`, an exception from the file-manager probe:
- is not swallowed locally;
- propagates/resumes unwind out of `40AE8`.

Promoted metadata:
- `exceptionWouldResumeUnwind = YES`;
- `shouldSwallowException = NO`.

No file I/O is performed by the reconstruction.

## `_updateFrameAndTransform` catch — cleanup only

Protected range:
- `0x40BB8..0x40BD4` -> landing `0x40BFC`, action 1.

It covers:
- `respondsToSelector:_updateFrameAndTransform`;
- conditional `_updateFrameAndTransform` send.

Landing `0x40BFC`:
1. saves/verifies expected exception type;
2. begins catch;
3. ends catch;
4. branches to `0x40BD4`, normal retained-argument cleanup.

Therefore an exception in the capability/send path:
- is swallowed;
- does not retry the private selector;
- skips all remaining presentation-update work;
- continues normal cleanup/return;
- does not call `41BA0`.

Promoted metadata:
- `shouldSwallowException = YES`;
- `shouldContinueCleanupAfterCatch = YES`.

## Promoted runtime contract

Added:
- `DDFBSPresentationUpdateExceptionSite`
  - None
  - OriginalCallback
  - NoPresentationUpdateFileProbe
  - UpdateFrameAndTransform
- `DDFBSPresentationUpdateExceptionOutcome`
- `DDResolveFBSPresentationUpdateExceptionOutcome(site, currentProbeCount, reasonSelectorSupported)`.

Outcomes:
- OriginalCallback -> swallow + existing reason probe + nested-probe-unwind metadata + continue post-original evaluation after normal probe completion;
- NoPresentationUpdateFileProbe -> propagate/resume unwind, not swallowed;
- UpdateFrameAndTransform -> swallow + normal cleanup, no reason probe.

## Global/cache side-effect fidelity

The original increments `qword_163E08` before invoking original. None of the local catches roll that back.

The file-manager path may write `dword_162F3C`. If an exception occurs before that write completes, the local function provides no catch/repair path. If the write has already occurred and a later unprotected operation throws, there is likewise no rollback.

R-105 intentionally reports no global mutation or rollback behavior; it only reports continuation/unwind semantics.

## Explicit exclusions

R-105 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke the original callback;
- invoke `41BA0` or read exception `reason`;
- access NSFileManager;
- test `/var/tmp/duodash_ab_nopresupdate`;
- invoke `respondsToSelector:_updateFrameAndTransform`;
- invoke `_updateFrameAndTransform`;
- mutate `qword_163E08` or `dword_162F3C`;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Next — R-106

The next focused gap is the private scene-settings executor layer:
- `3F5C0` normal-path admission/counter-class behavior is already represented data-only;
- `3F7C8` dispatched-block admission plus normal/exception slot-mark/counter outcome is already represented data-only;
- their exact Mach-O unwind/LSDA continuation behavior has not yet been audited/promoted as a dedicated exception layer.

R-106 after compiler green:
- locate/decode the unwind/LSDA records for `3F5C0` and `3F7C8`;
- reconcile exact catches/cleanup/unwind with existing admission, slot-mark, reentrancy-clear, and counter-class descriptors;
- promote only evidence-safe data-only continuation/counter-class/unwind metadata;
- keep private selector dispatch, block execution, slot writes, reentrancy/counter/global mutation, exception synthesis, and runtime catches excluded.
