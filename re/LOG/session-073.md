# LOG/session-073.md
_Date: 2026-10-06. Objective: continue after session-072 GitHub Actions build GREEN; promote only numeric/cache and IPC contracts recoverable without guessing._

## R-063 — numeric resolved-cache wrappers
Directly re-read `73E8.c`, `80D0.c`, `8154.c`, `81EC.c`, `17410.c`, prior hosting evidence and attempted per-function disassembly lookup.

Promoted:
- `DDCachedFractionValue(key)` = sub_8154: resolved plist lookup → `7E63C(value, 0, 99, 0, NULL)`.
- `DDCachedFractionLayoutValue()` = sub_81EC: fixed `appbridge_split_frac_layout` → `7E63C(value, 0, 8, 0, NULL)`.

Did NOT promote:
- `73E8` layout reader: available decompile elides all `7E63C` arguments.
- `80D0` ratio reader: same loss.
- Export has a disassembly directory, but there are no per-function `73E8.asm/80D0.asm/8154.asm/81EC.asm` files. Hosting evidence strongly constrains downstream layout/ratio behavior, but that is not sufficient to claim the exact wrapper arguments.

## R-064 — NSDistributed IPC + host-state publishers
Directly re-read `8900.c`, `887C.c`, `8934.c`, `8C28.c`, `8D78.c`, `97A0.c`, `9424.c`.

Promoted:
- runtime lookup of `NSDistributedNotificationCenter` + `defaultCenter` (8900), using `objc_msgSend` and no private-framework link;
- generic immediate post helper covering 8C28 (explicit object) and 8D78 (nil object);
- generic add-observer helper covering 887C/8934;
- `DDPostHostRefusedState` exact 97A0 payload: `{hostRefused:YES, refuseReason: reason ?: "?"}`;
- `DDPostHostState` exact 9424 schema:
  base `activated,bundleIdentifier,sbPid`;
  conditional cpuiBid + rect fields;
  cpuiMore when non-empty;
  cpuiGen iff main or more exists;
  cpuiKilled iff non-empty and main/more exists;
  post name `com.sensetechlab.appbridge.host.state`.

Not promoted:
- receiver-specific methods/selectors and their private class bodies.
- 89D8 uiapp.state builder: schema is known, but it reads cached globals `qword_163448/byte_162DDC`; replacing those with fresh prefs reads could change timing semantics, so defer.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- Session-072 GitHub Actions build GREEN per user. Session-073 Objective-C runtime-message/IPC edits require next pushed macOS CI run.

## Next
R-065 after CI green: inspect `8CC0/8DF8/91B4/986C` and promote only payload schemas whose full behavior is recoverable. Keep `89D8` separate until cached font-floor/keypane state semantics are represented without silently changing timing.
