# LOG/session-184.md
_Date: 2026-10-08. Objective: continue LocaleFlow executable promotion by reconstructing the exact 9AFB0/9B314 cache and invalidation boundary, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD dc8b1a4.
- Working tree clean; branch ahead 3.

## Evidence
- 9AFB0 reads qword_164C38 under unk_164C58 unfair lock and returns it when present.
- On miss, resolution work happens outside the lock.
- Before returning, 9AFB0 re-locks and stores the resolved value only when qword_164C38 is still empty; then returns the current cached value.
- 9B314 locks the same unfair lock, clears qword_164C38 and qword_164C40, releases both, then unlocks.
- qword_164C40 is used by 9B360 as a mutable dictionary lookup cache, so its contents are not reconstructed in this batch.

## Executable promotion
- LocaleFlow.m now imports <os/lock.h>.
- gDDLocaleCacheLock uses OS_UNFAIR_LOCK_INIT.
- gDDLocaleResolvedLanguage models qword_164C38.
- gDDLocaleLookupCache reserves the qword_164C40 cache slot for future exact 9B360 promotion.
- DDLocaleResolveLanguage now uses cache-check / uncached-resolution / store-if-empty semantics.
- DDLocaleInvalidateCaches clears both cache slots under the same unfair lock.

## Explicit exclusions
- 9B360 lookup dictionary population and translation-table semantics.
- language-change observers and UI reload fan-out.
- write+notify language setter.

## Next
After compiler green, decode 9B360 only if its translation key/table behavior can be made exact; otherwise continue another Foundation/CoreFoundation-safe synthesis slice.