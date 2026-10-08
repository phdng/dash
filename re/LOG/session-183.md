# LOG/session-183.md
_Date: 2026-10-08. Objective: continue executable promotion by moving the exact Foundation/CoreFoundation language-resolution core of existing LocaleFlow.m into the tweak target, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 61c61ed.
- Working tree clean; branch ahead 2 at start.
- CrashReporting executable slices already compiled from prior sessions.

## Evidence re-check
9AFB0 resolution order:
- first read /var/tmp/duodash_lang_force as UTF-8 and trim whitespace/newlines;
- if the force file exists but trims to empty, resolve `en` immediately;
- if the trimmed force value passes 9B284 whitelist, use it;
- otherwise CFPreferencesAppSynchronize(settings domain), then read duodash_language;
- if current value is not a valid whitelisted CFString, read legacy carnav_language;
- if valid legacy value exists, write it to duodash_language using CurrentUser/AnyHost and synchronize;
- otherwise resolve `en`.

9B284 whitelist table off_130E88 was fully decoded from __const as 17 code/name pairs.
Promoted code set:
- en
- zh-Hans
- es
- ja
- ko
- de
- fr
- pt-BR
- ru
- ar
- zh-Hant
- it
- tr
- vi
- pl
- id
- th

## Executable promotion
Existing re/RECONSTRUCTION/LocaleFlow.m is now compiled and bootstrapped.

Added public surface:
- DDLocaleFlowStart()
- DDLocaleFlowReady()
- DDLocaleIsSupportedLanguage()
- DDLocaleResolveLanguage()

Resolution behavior mirrors the evidence-safe core above, including legacy preference migration.

## Explicit exclusions
- original unfair-lock cache qword_164C38 / qword_164C40;
- 9B314 cache invalidation;
- language.changed post path;
- observer fan-out / UI reload callbacks;
- DDWriteLanguage setter path;
- unrelated version/device helpers.

## Build integration
- Makefile includes LocaleFlow.m.
- Tweak.x bootstraps DDLocaleFlowStart().
- verifier requires the source, Makefile entry, bootstrap, whitelist markers, force path, current+legacy keys, migration write, and en fallback.

## Next
After compiler green, promote cache/invalidation only if exact locking/lifetime behavior can be preserved; otherwise continue with another existing Foundation/CoreFoundation-safe synthesis slice.