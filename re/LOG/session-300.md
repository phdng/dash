# LOG/session-300.md
_Date: 2026-10-09. Objective: switch away from saturated DataRouter/NavProvider and promote one genuinely new exact pure helper from the 218D8 toggle slice._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `c16f651`.
- Working tree clean; branch ahead 115.

## Candidate filtering
- DataRouter/NavProvider offsets `83250/83FDC/84258/83EB4` are already canonical and must not be re-promoted.
- Crash telemetry helper `A2720` is read-only, but retained evidence only states a `sysctlbyname` wrapper with failure `?`; exact buffer/string-conversion details are not persisted, so it remains excluded rather than guessed.
- HUD/BLE scan/pair/brightness/correction bodies remain UNKNOWN or stateful.
- `218D8` panefracs has a direct OBSERVED function record with an independently pure nonempty-file parser and no unresolved constants in that branch.

## Exact panefracs semantics
From `RECONSTRUCTION/functions/218D8.md` B09 / `EVIDENCE/hosting_engine.md`:
- branch on original NSString `length`;
- zero/nil length does not parse and instead belongs to caller fallback `81EC()` + `8154(frac_a/frac_b)`;
- nonempty original text is trimmed with `whitespaceAndNewlineCharacterSet`;
- split trimmed text on comma;
- component 0 uses NSString `integerValue`;
- component 1 uses `integerValue` only when present, otherwise Objective-C nil-message semantics yield 0;
- components after index 1 are ignored;
- no numeric clamp is applied in this override branch;
- because the gate uses original length, a whitespace-only nonempty string enters the parser and resolves to `0,0`.

## R-299 executable promotion
Added `DDPaneFractionsOverrideValue(value,outFractionA,outFractionB)` to compiled `ToggleValueHelpers.m`, exported through `DuoDashShared.h`, and covered by the structural verifier/docs.

## Boundary
No `/var/tmp/duodash_ab_panefracs` file acquisition, no `81EC/8154` prefs fallback, no layout propagation, no writes to 163AF8/163B00/163B08/163AF3, and no host/UI/private state is enabled.

## Verification
- PASS: `python scripts/verify_reconstruction.py`.
- PASS: `python -m py_compile scripts/verify_reconstruction.py`.
- PASS: `git diff --check` (LF/CRLF warnings only).
- CatDesk standard verifier: `NOT_CONFIGURED` for this Theos-only repo; established project override applies.

## Next
Do not promote `paneratio` yet: its invalid-value fallback still references unresolved `&stru_20+18`. Continue only with another exact non-duplicative helper whose constants and branch boundaries are fully recovered. Do not push.
