# LOG/session-136.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-135 commit `686806a`; decode and promote exact data-only `38EF8` CNABKeyPaneHideKey SF-Symbol exception fallback behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `686806a`.
- Working tree: clean.
- Local tracking ref reported ahead 2 at session start; assistant did not fetch/push.
- User explicitly confirmed session-135 macOS CI/compiler GREEN.

## Target

- Function: `sub_38EF8`.
- LSDA: `0x114308`.
- Identity: constructor/helper building `CNABKeyPaneHideKey`.
- Relevant behavior: prefer SF Symbol `keyboard.chevron.compact.down`; if symbol path is unavailable, construct a manual chevron using UIView + UIBezierPath + CAShapeLayer.

Reviewed:
- `decompile/38EF8.c`;
- raw ARM64 around `0x39040..0x39260`;
- Mach-O LSDA bytes at `0x114308`.

## Exact LSDA call-site table

Decoded 4 entries:

1. `0x38EF8..0x39050` -> no landing.
2. `0x39050..0x39064` -> landing `0x39244`, action 5.
3. `0x39070..0x390A4` -> landing `0x39248`, action 5.
4. `0x390A4..0x39260` -> no landing.

`0x39244` aliases common typed catch `0x39248`.

Expected discriminator:
- begin catch;
- end catch;
- branch to `0x390C8`.

Nonmatching discriminator:
- resume unwind at `0x3925C`.

## Normal SF-Symbol path

Relevant raw order:

```
39050  configurationWithPointSize:weight:
39060  retainAutoreleasedReturnValue
39064  mov x24,x0                  ; retained configuration becomes committed here

3907C  systemImageNamed:withConfiguration:
39084  retainAutoreleasedReturnValue
39088  mov x25,x0                  ; retained image becomes committed here
3908C  cbz x0,390C0
39098  objc_alloc UIImageView
390A0  initWithImage:
390A4  mov x23,x0                  ; image view result committed outside protected range
390A8  release x25                 ; normal image release
390B0  release x24                 ; normal config release
390B8  cbnz x23,391D0
390BC  b 390C8
390C0  release x24                 ; nil-image path
390C8  manual chevron fallback
```

The manual fallback:
- allocates a UIView;
- builds a UIBezierPath with three points;
- creates/configures a CAShapeLayer;
- adds the shape layer;
- later tags/adds the fallback view into the hide-key view.

The constructor continues after fallback; the catch does not force constructor failure.

## Protected range 1 — symbol configuration

`0x39050..0x39064` covers:
- `+[UIImageSymbolConfiguration configurationWithPointSize:weight:]`;
- retain-autoreleased return.

Important boundary:
- `mov x24,x0` is at `0x39064`, immediately outside the protected range.

Therefore if an expected exception occurs in this range:
- expected catch swallows it;
- remaining SF-Symbol path is skipped;
- execution enters manual chevron fallback at `0x390C8`;
- there is no evidence that a retained configuration had been committed to `x24` before catch.

R-135 therefore deliberately does **not** mark a retained-config release bypass for this site.

## Protected range 2 — symbol image and image-view init

`0x39070..0x390A4` is one LSDA range but contains two semantic sub-sites.

### Symbol image lookup sub-site

`0x39070..0x3908C`:
- symbol name/config arguments;
- `+[UIImage systemImageNamed:withConfiguration:]`;
- retain-autoreleased image;
- store retained image into `x25` at `0x39088`;
- nil test.

At range entry:
- `x24` already holds the retained symbol configuration.

If expected exception occurs during symbol-image lookup/retain before an image is committed:
- catch jumps to manual fallback;
- normal config releases at `0x390B0` / `0x390C0` are bypassed.

R-135 records:
- symbol configuration definitely retained before protected call;
- retained config release could be bypassed.

It does not claim the image is definitely retained for this earlier sub-site.

### UIImageView init sub-site

`0x39090..0x390A4`:
- UIImageView class load;
- alloc;
- `initWithImage:`.

This site is reached only after:
- config `x24` is retained;
- image `x25` is nonnil and retained.

If expected exception occurs here:
- catch enters manual fallback;
- normal image release `0x390A8` is bypassed;
- normal config release `0x390B0` is bypassed.

R-135 therefore records both:
- retained configuration definitely present;
- retained image definitely present;
- both local releases could be bypassed.

## Normal nil cases are different from exception cases

If `systemImageNamed:withConfiguration:` returns nil normally:
- `0x3908C` branches to `0x390C0`;
- configuration is released;
- control enters manual fallback.

If `UIImageView initWithImage:` returns nil normally:
- image and configuration are released at `0x390A8..0x390B4`;
- `0x390BC` branches to manual fallback.

Thus release-bypass metadata is specific to exception routing, not to ordinary symbol-unavailable behavior.

## Manual fallback is unprotected

All manual chevron construction starting at `0x390C8` lies outside the typed LSDA ranges.

Exceptions from:
- fallback UIView allocation/init;
- UIBezierPath creation or point mutations;
- CAShapeLayer creation/configuration;
- layer lookup/addSublayer;
- later tag/addSubview constructor tail

propagate normally.

## Promoted runtime contract

Added:
- `DDCNABKeyPaneHideSymbolExceptionSite`:
  - `SymbolConfiguration`;
  - `SymbolImageLookup`;
  - `SymbolImageViewInit`;
  - `ManualFallbackUnprotected`;
  - `OtherUnprotectedRange`.
- `DDCNABKeyPaneHideSymbolExceptionOutcome`.
- `DDResolveCNABKeyPaneHideSymbolExceptionOutcome(site)`.

Symbol configuration site:
- swallow expected exception;
- skip remaining symbol path;
- continue manual chevron fallback;
- nonmatching type resumes unwind;
- no established config/image release bypass.

Symbol image lookup site:
- same fallback continuation;
- config definitely retained before protected call;
- config release could be bypassed.

Symbol image-view-init site:
- same fallback continuation;
- config + image definitely retained before protected call;
- both releases could be bypassed.

Manual fallback / other unprotected:
- propagate.

## Explicit exclusions

R-135 does not:
- invoke `UIImageSymbolConfiguration`;
- invoke `UIImage systemImageNamed:withConfiguration:`;
- allocate UIImageView/UIView;
- build UIBezierPath/CAShapeLayer;
- add real views/layers;
- mutate real ownership;
- synthesize/catch exceptions;
- execute catch/unwind runtime machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 38E14

Direct Mach-O `__unwind_info` enumeration shows the next earlier LSDA-bearing function:
- `38E14 -> LSDA 0x1142DC`.
- Identity: `sub_38E14`, parser for `/var/tmp/duodash_ab_keypane_hidegap`.

Normal behavior:
- read file as UTF-8 string;
- default result = `71.0`;
- if nonempty, obtain UTF8String;
- parse with `strtod`;
- accept parsed value only when:
  - <= 200.0;
  - >= 0.0;
  - parse consumed at least one character;
- otherwise return default `71.0`.

Decoded LSDA call-site table:

1. `0x38E14..0x38E34` -> no landing.
2. `0x38E34..0x38E50` -> `0x38ED4`, action 5.
3. `0x38E50..0x38E58` -> `0x38ED8`, action 5.
4. `0x38E58..0x38E6C` -> no landing.
5. `0x38E6C..0x38E70` -> `0x38ED8`, action 5.
6. `0x38E7C..0x38E88` -> `0x38ED0`, action 5.
7. `0x38E88..0x38EF8` -> no landing.

The landing aliases converge on common typed catch `0x38ED8`.

Expected type:
- begin catch;
- end catch;
- load default `71.0` into `d8`;
- branch to return epilogue `0x38EB4`.

Nonmatching type:
- resume unwind at `0x38EF4`.

### Range mapping

`0x38E34..0x38E50`:
- file read `stringWithContentsOfFile:encoding:error:`;
- retain-autoreleased string.
- Protected range ends before `mov x19,x0` at `0x38E50`.
- Expected catch returns 71.0.
- No established retained-string explicit-release bypass should be claimed here.

`0x38E50..0x38E58`:
- commit retained string into `x19`;
- `length`.
- Expected catch returns 71.0.
- Normal explicit release at `0x38EAC` is bypassed.

`0x38E58..0x38E6C` is unprotected:
- load default 71.0;
- nonempty branch;
- `objc_retainAutorelease(x19)` before UTF8String.
- An exception here propagates rather than taking the local default catch.

`0x38E6C..0x38E70`:
- `UTF8String`.
- Expected catch returns 71.0 and bypasses explicit x19 release.

`0x38E7C..0x38E88`:
- setup parse-end pointer;
- `strtod`.
- Expected catch returns 71.0 and bypasses explicit x19 release.

The validation and normal explicit release are unprotected.

R-136 should promote:
- per-site expected exception -> default 71.0;
- retained-string release-bypass only after x19 commit;
- unprotected retainAutorelease gap propagation;
- nonmatching type unwind.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
