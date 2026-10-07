# LOG/session-115.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-114 commit 72b94ef; complete R-114 by promoting exact data-only `3EDFC` frontmost-phone identity exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-114 — evidence source

Reviewed:
- `3EDFC.c`;
- raw ARM64 for `3EDFC` from the first arm64 FAT slice;
- Mach-O LSDA `0x1148F4`;
- existing `3EFD4` data-only string-selector helper exception contract.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3EDFC -> LSDA 0x1148F4`.

Decoded call-site table:
- `0x3EDFC..0x3EE20` -> no landing pad;
- `0x3EE20..0x3EE2C` -> landing `0x3EEE4`, action 5;
- `0x3EE38..0x3EE60` -> landing `0x3EEE8`, action 5;
- `0x3EE64..0x3EE78` -> landing `0x3EEDC`, action 5;
- `0x3EE84..0x3EEA8` -> landing `0x3EEE0`, action 5;
- `0x3EEA8..0x3EF20` -> no landing pad.

## Protected frontmost-phone identity stages

The helper retains the requested bundle identifier and immediately returns false for an empty input. The LSDA protection begins only after that initial input-length gate.

### SpringBoard class lookup

Protected range:
- `0x3EE20..0x3EE2C` -> landing `0x3EEE4`.

Raw ARM64 covers:
- loading the `"SpringBoard"` class-name string;
- runtime class lookup.

Landing `0x3EEE4` is only a branch to the common catch at `0x3EEE8`.

### Shared application / capability path

Protected range:
- `0x3EE38..0x3EE60` -> common catch `0x3EEE8`.

Raw ARM64 covers:
- `sharedApplication` send;
- retain-autoreleased-return handling;
- capability check for `_accessibilityFrontMostApplication`.

### Frontmost-application send

Protected range:
- `0x3EE64..0x3EE78` -> landing `0x3EEDC` -> common catch.

It covers:
- private `_accessibilityFrontMostApplication` send;
- retain-autoreleased-return handling.

### Bundle-string extraction and comparison

Protected range:
- `0x3EE84..0x3EEA8` -> landing `0x3EEE0` -> common catch.

Raw ARM64 covers:
- nested `3EFD4(frontmostApplication, bundleIdentifier-selector)` helper call;
- retain-autoreleased returned string;
- returned string `length`;
- `isEqualToString:` against the requested bundle when non-empty.

The normal boolean result is therefore true only when all lookups succeed and the extracted frontmost bundle equals the requested bundle.

## Common typed catch `0x3EEE8`

Small landing stubs:
- `0x3EEDC -> 0x3EEE8`;
- `0x3EEE0 -> 0x3EEE8`;
- `0x3EEE4 -> 0x3EEE8`.

Raw ARM64 common catch:
- compare catch discriminator with expected value 1;
- expected value:
  - begin catch at `0x3EEF0`;
  - end catch at `0x3EEF4`;
  - fall through to `0x3EEF8`;
  - set result register to zero/false;
  - release retained input bundle and return false;
- nonmatching value:
  - branch to `0x3EF1C`;
  - resume unwind.

Exact expected-catch semantics:
- swallow locally;
- abandon all remaining frontmost-app lookup/comparison work;
- force result false;
- perform normal retained-input cleanup;
- no retry, reason probe, counter mutation, or alternate identity source.

## Nested `3EFD4` relationship

`3EFD4` has its own LSDA and may internally swallow selector/type-check exceptions and return nil. If it returns nil normally, `3EDFC` sees a zero-length/nil result and returns false through its normal path.

Separately, if a protected exception reaches `3EDFC`'s own LSDA range, `3EDFC`'s common catch also forces false.

The reconstruction keeps these two contracts separate:
- `DDResolveStringSelectorExceptionOutcome` models `3EFD4`;
- `DDResolveFrontmostPhoneIdentityExceptionOutcome` models the enclosing `3EDFC` frontmost-phone test.

## Promoted runtime contract

Added:
- `DDFrontmostPhoneIdentityExceptionOutcome`;
- `DDResolveFrontmostPhoneIdentityExceptionOutcome(void)`.

Exact constant outcome for the expected typed path:
- `shouldSwallowException = YES`;
- `shouldReturnFalse = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

No site enum is required because every protected range converges on the same common catch and false-result continuation.

## Explicit exclusions

R-114 does not:
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs;
- query the SpringBoard class;
- invoke `sharedApplication`;
- invoke `_accessibilityFrontMostApplication`;
- traverse or retain live frontmost-app objects;
- invoke `3EFD4`;
- compare live private bundle identity strings;
- mutate state, counters, diagnostics, or globals.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3EB9C`

Mach-O maps:
- `3EB9C -> LSDA 0x1148D8`.

Decoded call-site table:
- `0x3EB9C..0x3EBC8` -> no landing pad;
- `0x3EBC8..0x3EC34` -> landing `0x3EC58`, action 1;
- `0x3EC34..0x3EC64` -> no landing pad.

Raw ARM64 protected range covers the entire live mutation sequence:
- `respondsToSelector:setFrame:`;
- optional `setFrame:` send;
- frame-applied byref write at `0x3EBF0..0x3EBFC` after a successful frame setter return;
- desired-orientation gate;
- runtime class lookup;
- `3ECD0` validation for `setInterfaceOrientation:`;
- optional `setInterfaceOrientation:` send ending at `0x3EC30`.

Landing `0x3EC58` is a local catch-all:
- begin catch;
- end catch;
- branch to `0x3EC44`, normal retained-settings cleanup/return.

There is no catch-discriminator comparison at this landing.

### Frame-path exception persistence

For an exception thrown by frame capability/send operations:
- the catch swallows and cleans up;
- the frame-applied byref write at `0x3EBF0..0x3EBFC` has not executed when `setFrame:` itself throws;
- orientation processing is skipped because the catch jumps directly to cleanup.

### Orientation-path exception persistence

If frame processing completed first, its byref flag may already be set to 1 before orientation work begins.

For an exception from orientation class/signature/setter work:
- catch swallows and cleans up;
- any already-recorded frame-applied flag is not rolled back;
- the orientation-applied write begins at `0x3EC34`, immediately after the protected range, so a throwing `setInterfaceOrientation:` never reaches that write.

Thus R-115 should distinguish frame-path vs orientation-path exception state persistence even though both sites share the same catch/cleanup continuation.

## Next

R-115 after compiler green:
- promote exact `3EB9C` catch-all swallow+cleanup outcome with site-aware byref persistence metadata;
- keep `setFrame:`, `3ECD0`, `setInterfaceOrientation:`, real settings/byref mutation, exception synthesis, and landing-pad execution excluded.
