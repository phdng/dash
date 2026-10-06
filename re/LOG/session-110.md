# LOG/session-110.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-109 commit aec5629; complete R-109 by promoting exact data-only `3FBC8` scene/client identity-resolution exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-109 — evidence source

Reviewed:
- `3FBC8.c`;
- raw ARM64 for `3FBC8` from the first arm64 FAT slice;
- Mach-O LSDA `0x114A18`;
- existing post-identity routing contracts (`DDResolveFBSUpdateIdentityRoute`, `DDResolveAVCSceneHandleIdentityRoute`).

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3FBC8 -> LSDA 0x114A18`.

## Call-site table

Decoded protected ranges include:
- `0x3FBF0..0x3FBFC` -> `0x3FF9C`, action 7;
- `0x3FC00..0x3FC14` -> `0x3FF90`, action 5;
- `0x3FC20..0x3FC34` -> `0x3FF98`, action 5;
- `0x3FC50..0x3FC74` -> `0x3FFA0`, action 5;
- `0x3FC94..0x3FCA0` -> `0x3FFA0`, action 5;
- `0x3FCA4..0x3FCD4` -> `0x3FF8C`, action 5;
- `0x3FCD8..0x3FCEC` -> `0x3FF74`, action 5;
- `0x3FCF8..0x3FD0C` -> `0x3FF80`, action 5;
- `0x3FD3C..0x3FD48` -> `0x3FFA0`, action 5;
- `0x3FD4C..0x3FD60` -> `0x3FF84`, action 5;
- `0x3FD6C..0x3FD80` -> `0x3FF94`, action 5;
- `0x3FDAC..0x3FDB0` -> `0x3FFA8`, action 5;
- `0x3FDF0..0x3FDF4` -> `0x3FF78`, action 5;
- `0x3FE00..0x3FE30` -> `0x3FF88`, action 5;
- `0x3FE4C..0x3FE5C` -> `0x3FF88`, action 5;
- `0x3FE84..0x3FEA0` -> `0x3FFA4`, action 5;
- `0x3FED4..0x3FEF4` -> `0x3FF7C`, action 5.

The surrounding non-protected ranges contain local branches/releases and the final return path.

## One common identity-resolution catch

Raw ARM64 proves that every small landing stub from `0x3FF74` through `0x3FFA4` branches to one common catch at `0x3FFA8`.

Common catch:
- `0x3FFA8`: compare landing/catch discriminator with expected value 1;
- expected value:
  - begin catch at `0x3FFB0`;
  - end catch at `0x3FFB4`;
  - branch to `0x3FF30`;
- `0x3FF30`: set resolved identity result register to nil and branch to final cleanup/return;
- nonmatching value:
  - branch to `0x3FFBC`;
  - resume unwind.

Therefore every expected exception from a protected identity-discovery step has the same semantic outcome:
- swallow locally;
- abandon the remaining identity search;
- force resolved identity to nil;
- continue normal retained-object cleanup/return.

There is no reason probe, retry, diagnostic counter, or alternate fallback traversal after the catch.

## Protected identity-discovery stages

The protected regions span the private/public traversal sequence used by `3FBC8`, including:

### Client-process path
- `respondsToSelector:clientProcess`;
- `clientProcess` send/retain-autoreleased handling;
- `3EFD4(clientProcess, "bundleIdentifier")`;
- returned string length check.

### Scene-handle / definition / client-identity path
- `respondsToSelector:sceneHandle`;
- `sceneHandle` send/retain;
- fallback to retained original object when sceneHandle is unsupported;
- `respondsToSelector:_definition`;
- `_definition` send/retain;
- `respondsToSelector:clientIdentity`;
- `clientIdentity` send/retain;
- `3EFD4(clientIdentity, "bundleIdentifier")`;
- returned string length check.

### Application path
- `respondsToSelector:application`;
- `application` send/retain;
- `3EFD4(application, "bundleIdentifier")`;
- returned string length check.

### Private identifier fallbacks
When direct bundle identity is still unresolved and host/aux state allows further matching, protected calls include:
- `3EFD4(object, "identifier")`;
- fallback `3EFD4(object, "sceneID")`;
- fallback `3EFD4(object, "sceneIdentifier")`.

### Host-slot / aux matching
Protected string calls include:
- host bundle `length` checks while searching non-CarPlay slots;
- private identifier `containsString:` checks against configured host bundle IDs;
- aux bundle `length` checks;
- private identifier `length` checks;
- private identifier `containsString:` against the configured aux bundle ID.

The reconstruction still does not reproduce any of this private traversal. R-109 only models the exception continuation once a caller/tooling layer identifies an exception site inside the original protected ranges.

## Nil-result semantics

The catch jumps to `0x3FF30`, which explicitly sets the result register used by final autorelease-return handling to nil.

This means the exception outcome is stronger than merely “skip current branch”:
- an earlier partially discovered identity is not preserved;
- no later identity fallback is attempted;
- the function returns nil after cleanup.

This is promoted as `shouldReturnNilIdentity = YES`.

## Nonmatching catch discriminator

When the landing discriminator is not the expected typed catch:
- common catch branches to `0x3FFBC`;
- runtime resume-unwind is invoked.

Promoted metadata:
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

The reconstruction does not synthesize foreign/nonmatching exceptions and does not execute unwind machinery.

## Promoted runtime contract

Added:
- `DDSceneIdentityResolutionExceptionOutcome`;
- `DDResolveSceneIdentityResolutionExceptionOutcome(void)`.

Exact constant outcome for the expected typed path:
- `shouldSwallowException = YES`;
- `shouldReturnNilIdentity = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

No site enum is needed because all protected call-site landings converge to the same common catch/continuation.

## Explicit exclusions

R-109 does not:
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs;
- traverse `clientProcess`, `sceneHandle`, `_definition`, `clientIdentity`, or `application`;
- invoke `3EFD4`;
- invoke `identifier`, `sceneID`, or `sceneIdentifier`;
- invoke NSString `length` or `containsString:` as part of private identity resolution;
- retain/release real private traversal objects;
- mutate host slots, CarPlay flags, aux identity, or any globals.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3EFD4`

Mach-O maps:
- `3EFD4 -> LSDA 0x114924`.

Decoded call-site table:
- `0x3EFD4..0x3EFF4` -> no landing pad;
- `0x3EFF4..0x3F000` -> landing `0x3F050`, action 7;
- `0x3F004..0x3F034` -> landing `0x3F054`, action 5;
- `0x3F034..0x3F088` -> no landing pad.

Raw ARM64 shows:
- `0x3F050` is only a branch into common catch `0x3F054`;
- common catch compares discriminator with expected value 1;
- expected type begin/end-catches then falls to `0x3F064`, setting return result nil;
- nonmatching type branches to `0x3F084` and resumes unwind.

Protected stages cover:
- `respondsToSelector:<caller-supplied selector>`;
- selector send + retain-autoreleased result;
- `NSString` class lookup;
- kind-of-class validation of the returned object.

Thus R-110 can remain data-only and compact:
- expected protected exception -> swallow + nil return;
- nonmatching discriminator -> resume unwind;
- no selector retry or reason probe.

## Next

R-110 after compiler green:
- promote exact `3EFD4` common catch→nil and nonmatching-type unwind metadata;
- keep selector invocation, runtime class/kind checks, real-object retain/release, exception synthesis, and unwind execution excluded.
