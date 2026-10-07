# LOG/session-135.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-134 commit `7fa7b80`; decode and promote exact data-only `39884` top-level host/split/root transparency catch-all behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `7fa7b80`.
- Working tree: clean.
- Local tracking ref reported ahead 1 at session start; assistant did not fetch/push.
- User explicitly confirmed session-134 macOS CI/compiler GREEN.

## Target

- Function: `sub_39884`.
- LSDA: `0x114330`.
- Role: top-level transparency wrapper for:
  - host view `qword_163C78`;
  - split view `qword_163C68`;
  - recursive root view `qword_163C70`.

Reviewed:
- `decompile/39884.c`;
- raw ARM64 `0x39884..0x39954`;
- Mach-O LSDA bytes at `0x114330`;
- prior exact recursive helper `39954 -> 0x11435C`.

## Exact LSDA table

Decoded 6 entries:

1. `0x39884..0x398A8` -> no landing.
2. `0x398A8..0x398C4` -> landing `0x3993C`, action 1.
3. `0x398C4..0x398D0` -> no landing.
4. `0x398D0..0x39904` -> landing `0x3993C`, action 1.
5. `0x39904..0x39910` -> no landing.
6. `0x39910..0x3992C` -> landing `0x3993C`, action 1.

Action 1 is a catch-all path here.

Landing `0x3993C`:
- `objc_begin_catch`;
- restores saved frame/registers;
- tail-branches to `objc_end_catch`.

There is no catch-type discriminator.

Therefore every Objective-C exception covered by these ranges is swallowed and the wrapper returns immediately.

## Normal wrapper order

When the relevant globals are non-null, the normal order is:

1. host `clearColor`;
2. host `setBackgroundColor:`;
3. release host clearColor;
4. host `setOpaque:NO`;
5. split `clearColor`;
6. split `setBackgroundColor:`;
7. release split clearColor;
8. split `setOpaque:NO`;
9. if recursive root exists, call `39954(root, 0)`;
10. return.

A caught exception skips every later step.

## Catch-all range 1 — host background

`0x398A8..0x398C4` covers:
- `+[UIColor clearColor]`;
- retain-autoreleased clearColor;
- host `setBackgroundColor:`.

If the background setter throws:
- the host background mutation may already have occurred.

If clearColor acquisition/retain/setter throws after a retained clearColor exists:
- the normal release at `0x398C4` is bypassed by catch-all return.

No later work occurs:
- host opaque is skipped;
- split transparency is skipped;
- root recursion is skipped.

R-134 models:
- host background possible;
- retained clearColor release possible bypass;
- immediate return.

## Catch-all range 2 — host opaque or split background

Broad range `0x398D0..0x39904` contains two semantic sites.

### Host opaque sub-site

`0x398D0..0x398D8`:
- host `setOpaque:NO`.

Reached only after:
- host background setter completed;
- host clearColor was released.

Therefore:
- host background is definitely applied;
- host opaque may already have applied before its exception;
- no split work has started.

Catch-all returns immediately.

### Split background sub-site

`0x398E4..0x39904` covers:
- split `+[UIColor clearColor]`;
- retain-autoreleased color;
- split `setBackgroundColor:`.

Reached only after:
- host background completed;
- host opaque completed.

Therefore:
- host background + opaque are definitely applied;
- split background may already have applied;
- retained split clearColor release at `0x39904` can be bypassed.

Split opaque and recursive root work are skipped.

## Catch-all range 3 — split opaque or recursive root

Broad range `0x39910..0x3992C` also contains two semantic sites.

### Split opaque sub-site

`0x39910..0x39918`:
- split `setOpaque:NO`.

Reached only after:
- host background + opaque completed;
- split background completed;
- split clearColor was released.

Therefore:
- host background + opaque are definitely applied;
- split background is definitely applied;
- split opaque may already have applied before its exception.

Recursive root traversal is skipped.

### Recursive-root sub-site

`0x39918..0x3992C`:
- load recursive root;
- skip if nil;
- otherwise call `39954(root, 0)`.

A propagated exception from `39954` can reach this outer catch-all only when it escapes the recursive helper's own local catch structure, for example through an unprotected/action-0 path.

By the time this call is reached:
- host background definitely applied;
- host opaque definitely applied;
- split background definitely applied;
- split opaque definitely applied.

The recursive root subtree may already have been partially mutated before the exception escapes.

Outer `39884` then:
- swallows the propagated exception;
- returns immediately;
- performs no rollback.

Thus partial root-subtree transparency is preserved.

## Unprotected ranges

No-landing ranges propagate normally.

In particular, the explicit clearColor releases at:
- `0x398C4..0x398D0`;
- `0x39904..0x39910`

are outside the catch-all ranges.

## Promoted runtime contract

Added:
- `DDTopLevelTransparencyExceptionSite`:
  - `HostBackgroundColor`;
  - `HostOpaqueSetter`;
  - `SplitBackgroundColor`;
  - `SplitOpaqueSetter`;
  - `RecursiveRoot`;
  - `UnprotectedRange`.
- `DDTopLevelTransparencyExceptionOutcome`.
- `DDResolveTopLevelTransparencyExceptionOutcome(site)`.

Caught sites:
- `shouldSwallowException = YES`;
- `shouldReturnImmediately = YES`.

Site-sensitive persistence:
- host background:
  - host background may have applied;
  - retained clearColor release may be bypassed.
- host opaque:
  - host background definitely applied;
  - host opaque may have applied.
- split background:
  - host background + opaque definitely applied;
  - split background may have applied;
  - retained clearColor release may be bypassed.
- split opaque:
  - host background + opaque definitely applied;
  - split background definitely applied;
  - split opaque may have applied.
- recursive root:
  - host background + opaque definitely applied;
  - split background + opaque definitely applied;
  - recursive-root exception may be swallowed by wrapper;
  - root subtree may have been partially mutated before the exception.

Unprotected:
- propagates.

## Explicit exclusions

R-134 does not:
- call `+[UIColor clearColor]`;
- invoke host/split `setBackgroundColor:` or `setOpaque:`;
- call `39954`;
- traverse live views;
- mutate live transparency;
- alter real retain/release ownership;
- synthesize/catch exceptions;
- execute Objective-C catch runtime machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 38EF8

Direct Mach-O unwind enumeration identifies the next earlier LSDA-bearing function below `39884`:
- `38EF8 -> LSDA 0x114308`.
- Identity: `sub_38EF8`, constructor for `CNABKeyPaneHideKey`.

The normal function:
- creates the key view and transparent/background container views;
- prefers SF Symbol `keyboard.chevron.compact.down`;
- falls back to a manually drawn chevron using UIView + UIBezierPath + CAShapeLayer when the symbol path is unavailable.

Decoded LSDA call-site table:

1. `0x38EF8..0x39050` -> no landing.
2. `0x39050..0x39064` -> landing `0x39244`, action 5.
3. `0x39070..0x390A4` -> landing `0x39248`, action 5.
4. `0x390A4..0x39260` -> no landing.

`0x39244` aliases the common typed catch at `0x39248`.

Expected catch:
- begin catch;
- end catch;
- branch to `0x390C8`.

`0x390C8` is the normal manual chevron fallback path.

### Protected range 1 — symbol configuration

`0x39050..0x39064` covers:
- `+[UIImageSymbolConfiguration configurationWithPointSize:weight:]`;
- retain-autoreleased configuration.

An expected exception:
- is swallowed;
- abandons SF Symbol setup;
- enters manual chevron fallback.

If a configuration object had already been retained before the throw, its normal symbol-path release can be bypassed.

### Protected range 2 — symbol image / image view

`0x39070..0x390A4` covers:
- `+[UIImage systemImageNamed:withConfiguration:]`;
- retain-autoreleased image;
- image-nil branch test;
- UIImageView allocation/init with that image.

Expected exception:
- is swallowed;
- enters manual chevron fallback.

Normal successful symbol path would release:
- retained image at `0x390A8`;
- retained symbol configuration at `0x390B0`.

The catch jump to `0x390C8` can bypass either/both depending on throw timing.

If the symbol image simply returns nil without throwing:
- normal code releases the configuration at `0x390C0`;
- then enters the same manual fallback.

Manual fallback construction itself is outside the protected ranges, so exceptions from:
- fallback UIView allocation;
- UIBezierPath work;
- CAShapeLayer setup;
- addSublayer

propagate normally.

Nonmatching catch type resumes unwind at `0x3925C`.

R-135 should promote only:
- expected typed symbol-path exception -> manual fallback continuation;
- site-aware possible retained config/image release bypass;
- nonmatching/unprotected propagation.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
