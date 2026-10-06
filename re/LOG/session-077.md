# LOG/session-077.md
_Date: 2026-10-06. Objective: continue after session-076 GitHub Actions build GREEN; promote exact pre-private host preparation and evidence-safe dismiss state/IPC without linking private SpringBoard scene/view classes._

## R-072 — pre-private host preparation

### 3B2D8 single-host state boundary
Directly re-read `3B2D8.c`.

Before private scene construction, after the original private-class availability gate, the function:
- activates hosting;
- copies the requested bundle into slot 0;
- sets split=false and slotCount=1;
- clears slots 1/2 and all three CarPlay-UI flags;
- increments host generation;
- computes the slot-0 mirror/render size;
- resets landscape-override state;
- resolves host orientation via `3DFC8`.

Recovered size rules exactly:
- read `/var/tmp/duodash_ab_rscale` with NSString `doubleValue`;
- read/trim `/var/tmp/duodash_ab_canvas`;
- when canvas is exactly `portrait`, ignore rscale and store portrait-normalized screen bounds:
  - width = min(screen width, screen height)
  - height = max(screen width, screen height)
- otherwise rscale is accepted only when 1.0 <= scale <= 3.0;
- out-of-range/missing scale defaults to 2.0;
- stored size = input render size * scale.

Promoted:
- `DDResolveSingleHostMirrorSize(renderSize, screenBoundsSize)`.
- `DDPrepareSingleHostMirror(bundleIdentifier, renderSize, screenBoundsSize)`.

The helper takes screen-bounds size explicitly instead of linking UIKit/UIScreen. It represents the exact state boundary after the original private-class gate. It deliberately does not schedule the app-side handshake, because original `3B738` is called only after private scene-host creation succeeds.

### 3CC44 split state boundary
Directly re-read `3CC44.c`, `3DD4C.c`, and `3CAA4.c`.

Confirmed:
- effective slot count is min(bundle count, native-size count), valid only for 1..3;
- `3DD4C(..., validateApps=0, ...)` converts non-NSString entries to empty string and replaces duplicate non-empty bids with empty string while preserving order;
- per-slot CarPlay flags default false when absent;
- split mode stores each original native per-slot size unchanged; any later CarPlay placeholder fallback size is view-only and does not replace `xmmword_163D90[slot]`;
- split generation increments when state is installed;
- orientation is already resolved before slot creation.

Promoted:
- `DDPrepareSplitHostMirror(..., resolvedOrientation)`, which feeds the exact post-normalization state into the existing mirror.
- No SBApplicationController/SBDeviceApplicationSceneEntity/SBAppViewController construction.

### 3CC44 pure landscape parser
Recovered the parser inside the lscape path:
- first non-empty token: strict decimal integer 3 or 4;
- later non-empty tokens:
  - `swap`
  - `cswap`
  - `rot=<double>`
- `rot` must parse fully, be finite, and satisfy abs(rotation) <= 360;
- unknown/non-fully-parsed tokens invalidate the override;
- empty tokens are ignored;
- if parsing fails or no orientation is present, orientation falls back to `3DFC8`.

Promoted:
- `DDParseLandscapeOverride`.
- `DDResolveSplitHostOrientationFromAcceptedOverride`.

Important boundary:
- `3CC44` first performs inter-process coordination using `duodash_ab_lscape.tripped`, `duodash_ab_lscape.inflight`, current PID, and `respring_planned` mtimes.
- That acceptance/coordination is not silently approximated here. Callers pass nil when coordination rejects the file.
- Full coordination is queued as R-074.

## R-073 — dismiss state/IPC half
Directly read:
- `3D8A8.c` — marshal dismiss block to main synchronously if already on main, otherwise `dispatch_async` to main.
- `3D990.c` — private hosted view/controller teardown, then per-slot bridge-off broadcasts, then resetHostingState.
- `3AAF8.c` — reset details.

Recovered evidence-safe behavior:
- slot 0: if bid non-empty and CarPlay flag OFF, publish `uiapp.state` with shouldBridge=NO, isSplit=NO, width=height=0;
- slots 1 and 2: same but isSplit=YES;
- use current hosted orientation;
- skip CarPlay-UI slots;
- after broadcasts, reset host state;
- reset does not increment host generation and does not clear orientation;
- reset clears active, split, slot count, all bids, sizes and CarPlay flags.

Promoted:
- `DDDismissHostMirror()` with exact main-thread marshaling and bridge-off/reset ordering.
- Existing `DDResetHostSlotMirror` already matches the recovered state subset of 3AAF8.

Explicit omissions:
- `3D990` removeFromSuperview/invalidate for private hosted controllers.
- `3AAF8` teardownAuxScene and private host-reset toast.
- These objects are not owned by the reconstruction mirror and remain private UI scope.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier = NOT_CONFIGURED, expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest.

Session-076 GitHub Actions build was GREEN per user. Session-077 Objective-C size/parser/dismiss changes require the next pushed macOS CI compiler run.

## Next
R-074 after CI green:
- recover/promote the full evidence-safe lscape coordination around:
  - `/var/tmp/duodash_ab_lscape`
  - `/var/tmp/duodash_ab_lscape.tripped`
  - `/var/tmp/duodash_ab_lscape.inflight`
  - `/var/mobile/Library/DuoDash/respring_planned`
- preserve exact PID and mtime rules;
- feed only accepted lscape text into the already-exact parser;
- keep `sub_372CC` display/private side effects outside unless independently recovered.
