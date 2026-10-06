# LOG/session-089.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-088 commit 78a44ac; complete R-088 with data-only 9C2C4 diagnostic-key/dedup and 41F50 private frame/foreground probe-record/mutation decisions. Per user workflow, commit locally but do not push._

## R-088 — 9C2C4 diagnostic key and dedup

Directly reviewed:
- `9C2C4.c`
- `9C24C.c`

Exact key construction:
- non-null object -> original uses its runtime class name;
- null object -> class component is `nil`;
- non-null ivar-name pointer -> use the supplied name;
- null ivar-name pointer -> ivar component is `?`;
- final key format is `<class>.<ivar>`.

The original then:
- locks a global unfair lock;
- lazily creates a mutable set;
- tests `containsObject:key`;
- adds only if absent;
- unlocks.

Promoted only as data:
- `DDBuildPrivateIvarDiagnosticKey(className, ivarName)`;
- `DDShouldInsertPrivateIvarDiagnostic(alreadyRecorded)`.

The caller supplies the class-name result and prior membership result. The reconstruction never touches the original set or lock.

## R-088 — raw ARM64 correction for 41F50

The decompiler hid several important operations, so raw ARM64 for the first arm64 slice was reviewed.

### Frame path

At entry:
- d0 is retained as width;
- d1 is retained as height.

If width <= 0:
- frame path counts as handled;
- no `_frame` lookup is attempted.

If width > 0:
- resolve `_frame` through 9C24C;
- missing ivar -> not handled, no diagnostic;
- existing ivar with missing/wrong type -> call 9C2C4 diagnostic;
- accepted type uses an 8-byte comparison against `{CGRect=`, so any type encoding with that exact prefix is accepted.

For an accepted frame ivar, ARM64 shows the pending direct write:
- origin x/y = zero;
- size = width/height.

The reconstruction records this as a write action + frame size and never dereferences/writes the private ivar.

### Foreground path

41F50 always probes `_foreground` when the settings object exists.

Raw ARM64 requires:
- first type byte is `c` or `B`;
- second byte is NUL.

Therefore accepted type encodings are exactly:
- `c`;
- `B`.

Accepted foreground would receive byte value 1 / YES.
Missing ivar is silent and not handled.
Existing ivar with missing/other type requests the 9C2C4 diagnostic.

The reconstruction records only the action and pending YES value.

## Failure-budget condition

The decompiler suggested an unconditional decrement, but ARM64 shows otherwise:
- frame handled flag and foreground handled flag are ANDed;
- only if either is false does the code attempt to decrement `dword_162F34`;
- decrement occurs only while that counter is >= 1.

Frame width <= 0 sets frame handled=true even though no frame lookup/write occurs.

Promoted:
- `DDPrivateSceneIvarAction`
  - None
  - Write
  - RecordUnsupported
- `DDSceneSettingsPrivateIvarPlan`
- `DDResolveSceneSettingsPrivateIvarPlan(width, height, frameIvarFound, frameTypeEncoding, foregroundIvarFound, foregroundTypeEncoding)`.

The descriptor includes:
- frame action;
- foreground action;
- pending frame size;
- pending foreground YES;
- whether the caller should attempt the original failure-budget decrement.

## Explicit exclusions

R-088 does not:
- call object/class/ivar runtime lookup APIs;
- calculate or dereference ivar offsets;
- write `_frame`;
- write `_foreground`;
- mutate `dword_162F34`;
- mutate the 9C2C4 global mutable set;
- take the original unfair lock;
- emit private diagnostics/logging beyond returning data-only decisions.

## Next

R-089 after compiler green:
- inspect `3FA90` interface-orientation read eligibility;
- inspect the post-frame/orientation update decision in `400D0`;
- promote only caller-supplied selector/frame/orientation decisions;
- do not invoke `3F5C0` or private scene-settings mutation.
