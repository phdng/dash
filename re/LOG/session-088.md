# LOG/session-088.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-087 commit df6696d; complete R-087 by promoting only data-only private-ivar type/access/write-width decisions from 9C24C/9C3BC/9C4AC. Per user workflow, commit locally but do not push._

## R-087 — 9C24C boundary

Directly reviewed:
- `9C24C.c`
- `9C3BC.c`
- `9C4AC.c`

The original 9C24C:
- requires a non-null object and non-null ivar name before calling Objective-C runtime lookup;
- returns the runtime ivar descriptor when found;
- optionally returns that ivar's type-encoding pointer.

The reconstruction keeps 9C24C as a strict boundary:
- callers supply `ivarFound`;
- callers supply only the first type-encoding byte;
- no `object_getClass`, `class_getInstanceVariable`, `ivar_getTypeEncoding`, or `ivar_getOffset` call is introduced.

## R-087 — 9C3BC integer ivar write-width plan

Exact accepted first encoding bytes:
- `c` / `C` -> one-byte write;
- `s` / `S` -> two-byte write;
- `i` / `I` -> four-byte write;
- `q` / `Q` -> eight-byte write.

Behavior preserved:
- missing ivar -> no write, no unsupported-type diagnostic;
- existing ivar with missing/empty/other encoding -> no write + mark unsupported-type diagnostic;
- supported encoding -> exact width plan, no diagnostic.

Promoted:
- `DDPrivateIvarWriteWidth`;
- `DDPrivateIntegerIvarWritePlan`;
- `DDResolvePrivateIntegerIvarWritePlan(ivarFound, typeEncodingFirstByte)`.

The helper never writes `_interfaceOrientation` or any object memory.

## R-087 — 9C4AC object ivar access plan

Exact object rule:
- existing ivar with first type byte `@` -> object read is eligible;
- existing ivar with missing/non-`@` type -> mark unsupported-type diagnostic;
- missing ivar -> no read and no diagnostic.

Promoted:
- `DDPrivateObjectIvarAccessPlan`;
- `DDResolvePrivateObjectIvarAccessPlan(ivarFound, typeEncodingFirstByte)`.

The helper never dereferences object ivar memory and never returns a private object.

## Cross-check for next batch

Reviewed:
- `9C2C4.c`
- `41F50.c`

9C2C4 constructs a diagnostic key as `<ClassName>.<ivarName>`, with `nil` and `?` fallbacks, then deduplicates it in a locked mutable set. 41F50 records `_frame` only when its frame-size input is positive and 9C24C finds that ivar; it also records `_foreground` whenever 9C24C finds it.

## Explicit exclusions

R-087 does not:
- invoke Objective-C runtime ivar lookup APIs;
- compute or use an ivar memory offset;
- read object ivar memory;
- write private integer ivars;
- write `_interfaceOrientation`;
- return `_otherSettings` or any other private object;
- mutate or emit the 9C2C4 diagnostic set.

## Next

R-088 after compiler green:
- inspect 9C2C4 diagnostic key/dedup semantics and 41F50 `_frame/_foreground` probe-record decisions;
- promote only data-only key/record eligibility;
- do not mutate the original global set, unfair lock, private ivars, or logging side effects.
