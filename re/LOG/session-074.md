# LOG/session-074.md
_Date: 2026-10-06. Objective: continue after session-073 GitHub Actions build GREEN; expand only evidence-complete AppBridge IPC and cached UI-state paths._

## R-065 — exact request/status IPC schemas
Directly re-read `8CC0.c`, `8DF8.c`, `91B4.c`, `986C.c`, then dependency `8F34.c` and representative callers.

Promoted:
- `DDPostUIAppRequest` matching 8CC0: `{bundleIdentifier: bid ?: ""}` → `com.sensetechlab.appbridge.uiapp.request`.
- `DDHostFrameMetrics` + `DDAppendHostFrameMetrics` matching 8F34 exact consumed offsets:
  frameX/Y/W/H, frameWinX/Y/W/H, frameWinValid, cpWinW/H.
- Static layout assertion: `sizeof(DDHostFrameMetrics) == 104`.
- `DDPostHostRequest` matching 8DF8: bundleIdentifier + activate + 8F34 frame fields → host.request.
- `DDPostSplitHostRequest` matching 91B4: bundleIdL/R/C, layout, activate, skipEvict, envOnly + frame fields → host.request.split.
- `DDPostCarPlayUIStatus` matching 986C: cpuiGen/cpuiBid/cpuiOk/cpuiWhy → cpui.status.

## R-066 — cached UI state + 89D8
Directly re-read `291F4.c`, `29400.c` and exact 27E20 notify registration lines.

Promoted cache semantics:
- `gDDBridgedFontFloor` and `gDDKeyPaneEnabled`.
- resolver path refreshes them in original `74C8` order: `7EA4` then `8058`.
- Immediate Darwin observers:
  - `com.sensetechlab.fontfloor.changed`
  - `com.sensetechlab.keypane.changed`
- `DDPostUIAppState` matches 89D8 eight-field payload and uses cached values, deliberately not fresh prefs reads.

## R-067 — runtime-resolved 29810/DDz2 broadcast path
Directly re-read `29810.c`.

Promoted without private framework linkage:
- runtime lookup `DDz2.shared`;
- active gate;
- exact hosted bundle source: `hostedSlotBids`, fallback to `hostedBundleId` + `hostedBundleId2`;
- matching `hostedSlotIsCarPlayUI` entries excluded; non-empty NSString phone-host entries retained in order, without dedup;
- exact per-bundle uiapp.fontfloor and uiapp.keypane payload/post helpers;
- 291F4/29400 callbacks now refresh cached state then broadcast to active non-CarPlay hosted bundles.

Explicit omission:
- `29400` calls private UI toast path `30960("Enable Unified Keyboard switched OFF")` when keypane becomes OFF. This is intentionally not promoted; cache and distributed-state behavior are preserved.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier: NOT_CONFIGURED, expected because this Theos repo has no Cargo.toml/package.json/Python project manifest.

Session-073 GitHub Actions build was GREEN per user. Session-074 Objective-C dynamic-selector/DDz2 edits require the next pushed macOS CI compiler run.

## Next
R-068 after CI green: inspect UIApp-side observers/receivers around 4CBDC and CNABHostUIAppResponder. Promote only runtime-resolvable consumer behavior that does not require private framework linkage. Keep 73E8/80D0 and full 7E908 unresolved until direct evidence recovers missing contracts.
