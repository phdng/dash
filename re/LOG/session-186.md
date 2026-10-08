# LOG/session-186.md
_Date: 2026-10-08. Objective: continue executable LocaleFlow promotion with the exact language setter + Darwin invalidation observer chain, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 6127c9d.
- Working tree clean; branch ahead 1.

## Evidence
6A4E4 valid-language branch:
- validates via 9B284;
- CFPreferencesSetAppValue(duodash_language, selected, settings domain);
- CFPreferencesAppSynchronize(settings domain);
- 9B314 cache clear;
- notify_post(com.sensetechlab.language.changed);
- caller then performs deferSwapToKitLevel:0 outside the reusable language-write chain.

9B848 / 9B87C:
- registers Darwin observer for com.sensetechlab.language.changed;
- suspension behavior DeliverImmediately;
- callback thunk calls only 9B314 cache clear.

## Executable promotion
- Added DD_N_LANGUAGE_CHANGED.
- Added DDLocaleSetLanguage().
- Invalid language returns NO with no write/notify.
- Valid language writes app preference, synchronizes, invalidates both locale caches, posts exact notify, returns YES.
- DDLocaleFlowStart now registers the exact Darwin observer once.
- Callback invokes DDLocaleInvalidateCaches only.

## Explicit exclusions
- caller-specific deferSwapToKitLevel:0 UI behavior;
- full 9B360 translation tables;
- other UI reload fan-out observers.

## Next
After compiler green, move to another bounded Foundation/CoreFoundation synthesis module unless the full 9B360 translation dataset is decoded completely.