# LOG/session-071.md
_Date: 2026-10-06. Objective: continue after phase-1 GitHub Actions build GREEN; promote evidence-safe prefs setters + notify fabric into executable runtime._

## Làm gì
1. Start protocol: đọc .catdesk/session, git status clean, branch `chore/reconstruction-build-ci` tracking origin.
2. Đọc trực tiếp decompile `746C.c`, `84D8.c`, `637E8.c`, `836C.c`, `29198.c`, `7E730.c`, sau đó thêm `7044.c`, `70FC.c`, `85B8.c`.
3. Promote compile-safe runtime:
   - `DDSetAppBridgeLayout`: exact gate 1..8 → SetAppValue + AppSynchronize + republish.
   - `DDSetCarPlayUI`: empty-main normalization + 7E730-equivalent filter (NSString/non-empty/exclude main/dedup/order) → persist both keys + republish.
   - `DDToggleAppBridgeAutostart`: 836C reads resolved plist (missing/non-bool→NO), flip → real CFBoolean → sync + republish.
   - `DDRawAutostartPreference`: encode exact 85CDC trap (missing→YES; only CFBoolean can be true; NSNumber/string do not coerce).
   - Darwin reload trio: settings.changed + appbridge.listchanged + com.sensetechlab.autostart.changed → same republish callback with DeliverImmediately, matching evidence-safe half of 29198.
4. Promote `DDEvictCarPlayUIBundle` from 85B8: resolved main/more read → remove target → call 84D8-equivalent setter. Explicitly prefs-only, no kill/view teardown.
5. Promote R-060 pure helpers from direct decompile:
   - 7044 resolved cache non-empty NSString reader.
   - 70FC CarPlay-more reader + 7E730 normalization.
   - 836C resolved autostart bool reader.
   - 8058 keypane prefs reader (missing/invalid-format => ON).
   - 7EA4 font-floor parser: override empty=>0; all-digits validated 8..96; non-digit override falls back prefs; prefs accepts CFNumber only.
6. Expand verifier contracts and docs/tracking (R-058/R-059/R-060 done).

## Evidence / quyết định
- Corrected phase-1 mismatch: settings.changed observer used Coalesce; original 27E20 uses Immediate.
- Did not implement 29198 downstream `792C4`: private side effect remains unresolved and is intentionally omitted.
- Did not implement DDz3 refreshSettingsRows/armSettingsWatchdog side effects after 637E8: private UI behavior, not required for prefs state transition.
- Logical evict 85B8 is safe to promote because FULL body contains only resolved-cache reads, collection ops and 84D8; no process/view APIs.

## Verification
- `python scripts/verify_reconstruction.py` → PASS.
- `python -m py_compile scripts/verify_reconstruction.py` → PASS.
- `git diff --check` → PASS (Windows LF/CRLF warnings only).
- `verify_project` → NOT_CONFIGURED (expected: no Cargo.toml/package.json/Python project manifest).
- Objective-C compiler gate for session-071 changes requires next GitHub Actions macOS run.

## Next
- Push session-071 changes and require GitHub Actions macOS compiler green.
- R-061: evaluate 7764C liveness probe for compile-safe promotion; add libproc only if snapshot/filter/pid-path contract remains private-framework-free.
