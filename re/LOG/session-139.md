# LOG/session-139.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-138 commit `f1ef1bf`; decode and promote exact data-only `3896C` property-list writer exception behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `f1ef1bf`.
- Working tree: clean.
- Branch synchronized with origin at session start.
- User explicitly confirmed session-138 macOS CI/compiler GREEN.

## Target

- Function: `sub_3896C(propertyList, path)`.
- LSDA: `0x114250`.
- Role: serialize a property list to NSData, write it to a file, then best-effort apply POSIX permissions.

Reviewed:
- `decompile/3896C.c`;
- raw ARM64 `0x3896C..0x38B0C`;
- Mach-O LSDA bytes at `0x114250`.

## Normal behavior

The function:
1. retains property-list input and path;
2. requires nonnull property list + nonempty path;
3. serializes using `NSPropertyListSerialization dataWithPropertyList:format:options:error:`;
4. retains serialized NSData;
5. writes data with `writeToFile:options:error:` and options `536870913`;
6. if write succeeds:
   - obtains `NSFileManager defaultManager`;
   - builds a one-entry permissions dictionary keyed by `NSFilePosixPermissions`;
   - sends `setAttributes:ofItemAtPath:error:`;
   - returns success;
7. otherwise returns false;
8. releases retained intermediates and final arguments.

The LSDA shows that attribute-setting is intentionally treated as best effort: an expected exception after the data write does not convert the write result to failure.

## Exact LSDA call-site table

Decoded 8 entries:

1. `0x3896C..0x389C4` -> no landing.
2. `0x389C4..0x389E0` -> landing `0x38AAC`, action 5.
3. `0x389E8..0x38A00` -> landing `0x38A94`, action 5.
4. `0x38A0C..0x38A6C` -> landing `0x38A98`, action 5.
5. `0x38A6C..0x38A90` -> landing `0x38B08`, action 0.
6. `0x38A90..0x38AC0` -> no landing.
7. `0x38AC0..0x38AD0` -> landing `0x38B08`, action 0.
8. `0x38AD0..0x38B0C` -> no landing.

## Typed failure catch — serialization/write

Landing `0x38A94` is only:
- branch to `0x38AAC`.

At `0x38AAC`:
- compare discriminator with expected type;
- expected:
  - begin catch;
  - end catch;
  - `mov w22,#0`;
  - fall through to final argument cleanup `0x38AC0`;
- nonmatching:
  - resume unwind at `0x38B08`.

Thus serialization and file-write expected exceptions both return false.

### Serialization range

`0x389C4..0x389E0` covers:
- `+[NSPropertyListSerialization dataWithPropertyList:format:options:error:]`;
- retain-autoreleased NSData result.

Important boundary:
- `mov x21,x0` is at `0x389E0`, immediately outside the protected range.

Expected exception:
- swallowed;
- return false;
- final path/property-list cleanup still runs;
- no committed x21 retained-data release bypass is asserted.

### Data-write range

`0x389E8..0x38A00` covers:
- `-[NSData writeToFile:options:error:]`.

At entry:
- retained NSData x21 is already committed.

Expected exception:
- swallowed;
- return false;
- normal retained-data release at `0x38A88` is bypassed;
- final path/property-list cleanup still runs.

This differs from a normal `writeToFile:` false result: normal false follows the ordinary path and releases x21 before returning false.

## Typed post-write attribute catch

`0x38A0C..0x38A6C` is reachable only after:
- retained NSData exists;
- `writeToFile:options:error:` returned true.

Landing `0x38A98`:
- compare discriminator with expected type;
- expected:
  - begin catch;
  - end catch;
  - branch to `0x38A7C`;
- nonmatching:
  - eventually resumes unwind via `0x38B08`.

At `0x38A7C`:
- force success flag `w22=1`;
- branch to `0x38A88`;
- release retained NSData x21;
- continue final path/property-list cleanup.

Therefore an expected exception while applying file attributes:
- does **not** undo or negate the already successful data write;
- returns true;
- still performs retained-data cleanup;
- still performs final argument cleanup.

## Attribute sub-site 1 — file-manager acquisition

Raw order:

- `0x38A0C`: `+[NSFileManager defaultManager]`;
- `0x38A14`: retain-autoreleased result;
- `0x38A18`: `mov x22,x0`.

A throw before `0x38A18` may occur after manager acquisition/retain work began but before x22 is committed.

Expected catch:
- returns true because data write already succeeded;
- releases retained NSData;
- final-cleans input arguments;
- does not run normal manager release at `0x38A74`.

R-138 records:
- manager acquisition may have started;
- temporary manager release may be bypassed;
- no guaranteed committed x22 manager before every exception at this sub-site.

## Attribute sub-site 2 — permissions dictionary construction

After manager x22 commit, the function prepares:
- key `NSFilePosixPermissions`;
- value from `off_1543D0`;
- calls `+[NSDictionary dictionaryWithObjects:forKeys:count:]`;
- retain-autoreleased dictionary;
- commits it to x23 at `0x38A54`.

A throw during dictionary creation/retain:
- occurs after manager x22 is definitely committed;
- may occur after temporary dictionary construction began but before x23 commit.

Expected catch:
- returns true;
- skips normal manager release;
- may skip release of a temporary dictionary;
- releases retained NSData;
- final-cleans arguments.

## Attribute sub-site 3 — setAttributes

At `0x38A58..0x38A6C`:
- manager x22 is committed;
- permissions dictionary x23 is committed;
- path x20 is retained;
- `setAttributes:ofItemAtPath:error:` is sent.

If the setter throws:
- manager and dictionary normal releases at `0x38A6C..0x38A78` are bypassed by the catch;
- the attribute operation may already have partially applied POSIX permissions before the exception;
- the successful data write remains authoritative;
- catch returns true;
- retained NSData still releases;
- final path/property-list cleanup still runs.

No rollback of file contents or attributes exists.

## Action-0 cleanup ranges

### Intermediate cleanup

`0x38A6C..0x38A90` covers:
- dictionary release;
- file-manager release;
- success flag setup;
- retained-data release.

LSDA action 0 routes to `0x38B08`.

An exception in this cleanup:
- is not locally swallowed;
- resumes unwind.

### Final argument cleanup

`0x38AC0..0x38AD0` covers:
- path release;
- property-list release.

This is also action 0:
- cleanup exception resumes unwind.

## Unprotected ranges

No-landing ranges propagate normally.

## Promoted runtime contract

Added:
- `DDPropertyListWriterExceptionSite`:
  - `Serialization`;
  - `DataWrite`;
  - `FileManagerAcquisition`;
  - `PermissionsDictionaryConstruction`;
  - `SetAttributes`;
  - `IntermediateCleanupUnwind`;
  - `FinalArgumentCleanupUnwind`;
  - `UnprotectedRange`.
- `DDPropertyListWriterExceptionOutcome`.
- `DDResolvePropertyListWriterExceptionOutcome(site)`.

Serialization:
- swallow expected exception;
- return false;
- final argument cleanup continues.

Data write:
- swallow expected exception;
- return false;
- retained data definitely committed;
- retained-data release can be bypassed;
- final argument cleanup continues.

All three attribute sub-sites:
- swallow expected exception;
- data write definitely succeeded;
- return true;
- retained data definitely committed;
- retained-data cleanup continues;
- final argument cleanup continues.

File-manager acquisition additionally:
- temporary manager acquisition may have started;
- temporary manager release may be bypassed.

Permissions-dictionary construction:
- manager definitely committed;
- manager release may be bypassed;
- temporary dictionary construction may have started;
- temporary dictionary release may be bypassed.

SetAttributes:
- manager + dictionary definitely committed;
- both releases may be bypassed;
- attributes may already have partially applied.

Cleanup-unwind sites:
- propagate/resume unwind.

Unprotected:
- propagate.

## Explicit exclusions

R-138 does not:
- serialize property lists;
- write files;
- obtain real NSFileManager state;
- build/apply permissions dictionaries;
- chmod or mutate file attributes;
- mutate real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 38240

Direct unwind order identifies the next earlier LSDA-bearing function:
- `38240 -> LSDA 0x1141D0`.
- Identity: large keypane/aux-scene host construction helper.

The LSDA header declares a `0x71`-byte call-site table.

Decoded 16 entries:

1. `0x38240..0x3852C` -> no landing.
2. `0x3852C..0x38590` -> `0x388E0`, action 5.
3. `0x38590..0x38598` -> no landing.
4. `0x38598..0x385A4` -> `0x388E0`, action 5.
5. `0x385A8..0x38680` -> `0x388E4`, action 5.
6. `0x38680..0x38688` -> no landing.
7. `0x38688..0x386AC` -> `0x388E4`, action 5.
8. `0x386BC..0x386C0` -> `0x388D4`, action 5.
9. `0x386C0..0x386D8` -> `0x388D0`, action 5.
10. `0x386D8..0x3870C` -> `0x388DC`, action 5.
11. `0x3870C..0x3875C` -> no landing.
12. `0x3875C..0x387A0` -> `0x388DC`, action 5.
13. `0x38814..0x38818` -> `0x388D8`, action 5.
14. `0x38818..0x38878` -> no landing.
15. `0x38878..0x38890` -> `0x388D8`, action 5.
16. `0x38890..0x388AC` -> no landing.

Landing aliases `0x388D0..0x388E0` converge at common typed catch `0x388E4`.

### Protected range groups

- `0x3852C..0x38590`: outer/container UIView construction, clips, clear background.
- `0x38598..0x385A4`: outer/container `setOpaque:NO`.
- `0x385A8..0x38680`: inner UIView construction and host-scene transform/frame/autoresizing/addSubview/center/background setup.
- `0x38688..0x386AC`: inner opaque + hierarchy insertion into outer/splitHost.
- `0x386BC..0x386C0`: `38E14` keypane gap read.
- `0x386C0..0x386D8`: left `38EF8` hide-key creation/retain.
- `0x386D8..0x3870C`: right hide-key creation/retain + add both key views.
- `0x3875C..0x387A0`: `39260` geometry sync plus subsequent global size/flag/time writes through the protected end.
- `0x38814..0x38818`: `39884` transparency wrapper.
- `0x38878..0x38890`: late bringSubviewToFront + `30F48(1)`.

### Common expected catch

At `0x388E4` expected type:
- begin catch;
- retain caught object;
- explicitly load/nil/release global `qword_163C88`;
- explicitly load/nil/release global `qword_163C90`;
- call the teardown selector/helper on retained DDz2 object x21;
- explicitly load/nil/release global `qword_163C78`;
- release caught object;
- end catch;
- force result register `w25=0`;
- release retained aux-scene x22;
- release retained DDz2 x21;
- rejoin splitHost/input cleanup and return false.

Nonmatching type resumes unwind at `0x38964`.

### Important R-139 questions

The protected ranges cross several state-commit boundaries.

R-139 should map exactly:
- which outer/inner/key retained objects can bypass their normal releases at each site;
- when globals `qword_163C78`, `qword_163C68`, `qword_163C70`, `qword_163C88`, and `qword_163C90` have already been stored;
- catch explicitly clears C78/C88/C90, but raw local catch does not explicitly clear C68/C70;
- which size globals `163CB8/CC0/CC8/CD0`, flags `163C98/CD8`, time `163CE0`, and generation `163CE8` have already been committed for late catches;
- whether the late `39884` or bringSubview/30F48 ranges can leave transparency/activation side effects despite catch cleanup;
- teardown helper effects must not be invented beyond directly evidenced local calls/stores.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
