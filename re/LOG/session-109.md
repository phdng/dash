# LOG/session-109.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-108 commit 406f424; complete R-108 by promoting exact data-only `3FA90` current-interface-orientation exception fallback from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-108 — evidence source

Reviewed:
- `3FA90.c`;
- raw ARM64 for `3FA90` from the first arm64 FAT slice;
- Mach-O LSDA index and `__gcc_except_tab` mapping;
- existing R-089/R-090 data-only current-orientation consumer behavior.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3FA90 -> LSDA 0x114A00`.

Decoded call-site table:
- `0x3FA90..0x3FAB0` -> no landing pad;
- `0x3FAB0..0x3FACC` -> landing `0x3FAD4`, action 1;
- `0x3FACC..0x3FAF8` -> no landing pad.

## Protected interfaceOrientation range

Raw ARM64 for `0x3FAB0..0x3FACC` covers exactly:
- `respondsToSelector:interfaceOrientation`;
- conditional `interfaceOrientation` selector send.

Normal behavior:
- if the settings object is absent or does not support `interfaceOrientation`, the function returns zero;
- if the selector is supported, the selector result becomes the return orientation.

This normal-path rule was already represented by `DDResolveCurrentInterfaceOrientation(settingsObjectPresent, interfaceOrientationSelectorSupported, currentOrientation)`.

## Landing `0x3FAD4` — unconditional local swallow

Raw ARM64:
- `0x3FAD4`: call Objective-C begin-catch runtime;
- `0x3FAD8`: call end-catch runtime;
- fall through to `0x3FADC`;
- `0x3FADC`: set return register to zero;
- release retained settings object;
- return zero.

Unlike several nearby typed catches (`3F990`, `3F7C8`, etc.), this landing does **not** compare the landing discriminator before beginning the catch. There is therefore no evidence for a separate nonmatching-catch continuation inside `3FA90`.

Exact local exception semantics for the protected range:
- swallow the exception locally;
- do not retry capability check or selector send;
- force return orientation to zero;
- perform normal retained-object cleanup;
- no reason probe;
- no counter/global mutation.

## Promoted runtime contract

Added:
- `DDCurrentInterfaceOrientationExceptionOutcome`;
- `DDResolveCurrentInterfaceOrientationExceptionOutcome(void)`.

Exact constant outcome:
- `shouldSwallowException = YES`;
- `fallbackOrientation = 0`.

The contract intentionally contains no site enum because the LSDA has one protected range and one local behavior.

It also intentionally contains no unwind/nonmatching-type field because raw ARM64 provides no discriminator branch for this landing.

## Explicit exclusions

R-108 does not:
- synthesize exceptions;
- execute begin-catch/end-catch runtime APIs;
- invoke `respondsToSelector:interfaceOrientation`;
- invoke `interfaceOrientation`;
- mutate the settings object;
- read exception `reason`;
- mutate counters or globals;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3FBC8`

Mach-O maps:
- `3FBC8 -> LSDA 0x114A18`.

Decoded call-site table contains many protected identity-resolution regions, including:
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

Raw ARM64 shows all small landing stubs `0x3FF74..0x3FFA4` branch to common catch `0x3FFA8`.

Common catch `0x3FFA8`:
- compare discriminator with expected value 1;
- expected type: begin catch, end catch, branch to `0x3FF30`;
- `0x3FF30`: set resolved identity result to nil and continue final cleanup/return;
- nonmatching discriminator: branch to `0x3FFBC` and resume unwind.

The protected regions span the private identity-discovery chain:
- `clientProcess` capability/read + bundle ID helper;
- `sceneHandle` capability/read;
- `_definition` capability/read;
- `clientIdentity` capability/read + bundle ID helper;
- `application` capability/read + bundle ID helper;
- host-slot bundle length checks;
- private `identifier`/`sceneID`/`sceneIdentifier` reads;
- contains-string host matching;
- aux identity matching.

This gives a compact next contract despite the large call-site table:
- expected protected exception -> swallow + return nil;
- nonmatching catch discriminator -> resume unwind.

## Next

R-109 after compiler green:
- promote exact `3FBC8` common identity-resolution catch→nil outcome and nonmatching-type unwind metadata;
- keep private scene/client traversal, selectors, string helpers/matching calls, exception synthesis, and global mutation excluded.
