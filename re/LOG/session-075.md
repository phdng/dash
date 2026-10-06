# LOG/session-075.md
_Date: 2026-10-06. Objective: continue after session-074 GitHub Actions build GREEN; promote only the evidence-safe UIApp-side AppBridge consumer path._

## R-068 — UIApp-side IPC/state consumer
Directly re-read:
- `4CBDC` UIApp ctor/wiring;
- `4407C` onState;
- `443FC` onKeyPaneSwitch;
- `444C4` onFontFloor;
- `445F8` onActive + `447C0` stale-state timeout;
- `446E4` onBackground;
- `42F10` temp/legacy marker lookup;
- `422D0` bridge-state mutation boundary.

Promoted:
- `DDReconstructionUIAppObserver` registered only in DDRoleUIApp.
- Exact bundle-scoped NSDistributed subscriptions:
  - com.sensetechlab.appbridge.uiapp.state
  - com.sensetechlab.appbridge.uiapp.fontfloor
  - com.sensetechlab.appbridge.uiapp.keypane
- Local active/background observers using the UIKit notification names as strings, avoiding a hard UIKit framework link.
- Initial UIApp state request during startup and re-request on foreground.
- Exact onState parsing/defaults into a compile-safe cache:
  shouldBridge boolValue, width/height doubleValue, orientation default 1, isSplit boolValue,
  bridged_font_floor NSNumber-only and negative clamp to 0,
  keypane_enabled NSNumber-only else default YES.
- State signature format from 4407C: `%d|%.1fx%.1f|%ld|%d`.
- Bridge-state orientation clamp from 422D0: only 1..4, otherwise 1.
- `DDCurrentUIAppBridgeState()` exposes reconstructed cache state for tests/debugging.
- 445F8/447C0 3-second stale state timeout keyed to the onState generation counter.
- 446E4 background semantics: clear state when not bridging, or when duodash_ab_bg_teardown exists.
- Exact 42F10 marker lookup semantics, including legacy carnav_* alias for duodash_* names.
- Startup env guard `DUODASH_AB_UIAPP_IPC_HOOKED`.

Explicit boundary:
- `422D0` relayoutAllWindows and raised-font apply/restore are UIKit/private UI mutation and are not approximated.
- `443FC/4407C` keypane path only updates the compile-safe cache; 448B4 teardown/UI effects remain out.
- Second half of 4CBDC (CNABKeyProbeObserver + keyboard Darwin/local notifications) remains out. Direct reads show onApply mutates UITextField/UITextView/UIKeyInput state; card/fallback blocks also enter private keypane functions.

## R-069 investigation — SpringBoard onUIAppRequest
Directly re-read `3F224` and searched DDz2 accessors/global writers.

Recovered via DDz2 selectors:
- active
- hostedSlotBids
- hostedSlotIsCarPlayUI
- hostedOrientation
- isSplitHosting
- renderSize (slot 0 only)

Blocker:
- 3F224 must match up to three slot bundle IDs and use each matching slot's own width/height from xmmword_163D90[index].
- No safe recovered multi-slot render-size accessor was found. Using DDz2.renderSize for slots 1/2 would silently substitute slot-0 geometry.
- Therefore the SpringBoard request→uiapp.state responder remains deferred.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier = NOT_CONFIGURED, expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest.

Session-074 GitHub Actions build was GREEN per user. Session-075 Objective-C observer/block/state-cache changes require the next pushed macOS CI compiler run.

## Next
After CI green:
1. Revisit R-069 only if a direct per-slot render-size accessor/safe bridge is recovered.
2. Otherwise move to the next evidence-safe subsystem; do not fake per-slot geometry.
3. Key-probe/input mutation remains private-UIKit scope until promoted with exact contracts.
