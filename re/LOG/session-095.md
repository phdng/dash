# LOG/session-095.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-094 commit 82afb91; complete R-094 by attaching only the data-only 40DA8 successful-substitution counter outcome to the existing callback size-rewrite descriptor. Per user workflow, commit locally but do not push._

## R-094 — 40DA8 successful substitution counter

Directly reviewed:
- `40DA8.c`
- `40C5C.c`

Raw ARM64 for `40DA8` and `40C5C` was cross-checked.

The two callbacks share the same rewrite gate:
- hosting active;
- 41CBC route accepted;
- original width >0;
- original height >0;
- resolve native size through 41D80;
- apply accepted-landscape swap;
- substitute only when final replacement width and height are both >0.

ARM64 explicitly contains self-comparisons on the original floating-point inputs before 41D80:
- `fcmp d8,d8; b.vs ...`
- `fcmp d9,d9; b.vs ...`

Therefore NaN original dimensions must not reach substitution. The shared reconstruction helper now uses strict-positive checks:
- `originalSize.width > 0 && originalSize.height > 0`;
- `replacement.width > 0 && replacement.height > 0`.

This naturally rejects NaN while preserving the same positive-number behavior.

## 40DA8-only counter effect

After a replacement size has passed both final positivity tests, raw ARM64 shows:

```asm
ldr  w9, [dword_162F40]
subs w9, w9, #1
b.lt ...
str  w9, [dword_162F40]
```

Exact meaning:
- size substitution succeeds independently of the counter value;
- when signed `dword_162F40 >= 1`, the original decrements it once;
- when the counter is 0 or negative, no counter write occurs;
- the replacement width/height are still used.

40C5C performs the same successful size substitution but has no corresponding `dword_162F40` decrement.

## Promoted runtime contract

`DDSceneCallbackSizeRewrite` now carries:
- final `size`;
- `substituted`;
- `shouldAttemptSuccessCounterDecrement`;
- `nextSuccessCounter`.

The existing base helper:
- `DDResolveSceneCallbackSizeRewrite(...)`
continues to model the shared 40C5C/40DA8 substitution only;
- counter action remains false.

New 40DA8 wrapper:
- `DDResolveSceneCallbackSizeRewriteWithSuccessCounter(bundleIdentifier, originalSize, successCounter)`.

Behavior:
- reuse the exact base rewrite;
- preserve caller-supplied counter as next value by default;
- only when `rewrite.substituted && successCounter >= 1`:
  - report pending decrement;
  - next counter = current - 1.

No counter is mutated.

## Explicit exclusions

R-094 does not:
- invoke the original 40C5C or 40DA8 callback;
- reproduce 3FBC8/41CBC private identity traversal;
- mutate `dword_162F40`;
- invoke private scene/settings executors.

## Scout for next batch

Raw ARM64 after both callback bodies exposes exception landing pads not visible in the decompiler:
- 40C5C has a bounded `qword_163EA8` increment path;
- 40DA8 has a bounded `qword_163EB0` increment path;
- both compare the unsigned count to 9 before increment.

Catch-to-operation mapping needs to be confirmed before promotion; these paths are intentionally not reconstructed in this batch.

## Next

R-095 after compiler green:
- inspect raw ARM64 exception landing pads around 40C5C/40DA8;
- confirm which private/original invocation each catch corresponds to;
- promote only data-only bounded diagnostic-counter outcomes;
- do not synthesize/catch exceptions, invoke callbacks, or mutate diagnostic counters.
