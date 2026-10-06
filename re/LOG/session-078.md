# LOG/session-078.md
_Date: 2026-10-06. Objective: continue after session-077 GitHub Actions build GREEN; promote exact evidence-safe landscape inter-process coordination and the pure/state half of landscape-aware slot resize._

## R-074 — full evidence-safe 3CC44 landscape coordination

Directly re-read `3CC44.c` and `372CC.c`.

### Reset and outer gates
For a valid effective split slot count (1..3), original 3CC44 first resets:
- landscape override orientation (`qword_163D58`) to 0;
- swap flag (`byte_163E80`) to 0;
- cswap flag (`byte_163D60`) to 0;
- rotation (`qword_163D68`) to 0.

Invalid effective slot counts return before any landscape file coordination.

Then:
- read `/var/tmp/duodash_ab_lscape` as UTF-8;
- if missing, fallback to 3DFC8 orientation;
- if `/var/tmp/duodash_ab_lscape.tripped` exists, skip inflight/parser work and fallback to 3DFC8.

### Inflight PID semantics
Read `/var/tmp/duodash_ab_lscape.inflight` as UTF-8 and use NSString `intValue` semantics.

If content is non-empty, intValue >= 1 and PID differs from current process:
1. stat `/var/mobile/Library/DuoDash/respring_planned`;
2. stat inflight;
3. only when both stats succeed and `respring_planned.st_mtimespec.tv_sec >= inflight.st_mtimespec.tv_sec`:
   - unlink inflight;
   - treat inflight as absent and continue parsing.
4. otherwise it remains a live foreign inflight.

If a live foreign inflight remains:
- write exactly `tripped\n` to `duodash_ab_lscape.tripped`, non-atomically;
- unlink inflight;
- do not parse/apply the landscape override;
- fallback orientation to 3DFC8.

Empty, invalid-int, zero/negative, missing, or current-PID inflight does not trip and proceeds to parse.

### Accepted override persistence
The strict parser from session-077 remains:
- first non-empty token: strict integer 3 or 4;
- later tokens only `swap`, `cswap`, or fully parsed finite `rot=<double>` with abs <= 360;
- unknown/invalid token rejects the whole override.

On accepted parse:
- persist orientation/swap/cswap/rotation in reconstruction host state;
- open inflight with `O_WRONLY | O_CREAT | O_TRUNC`, mode 0644;
- write current PID plus newline when open succeeds;
- accepted orientation becomes hosted orientation.

Original then calls `sub_372CC`. Direct read confirms it hooks private `_UIKeyboardLayerHostView` selectors setCenter:/setFrame:/didMoveToWindow. That private keyboard-layer hook is intentionally not promoted.

Promoted APIs/state:
- `DDResolveCoordinatedSplitHostOrientation()`.
- `DDPrepareSplitHostMirrorFromEnvironment(...)`, with the original invalid-slot-count-before-side-effects gate.
- landscape state fields exposed in `DDCurrentHostSlotMirror()`.

### Cleanup fidelity fixes
Direct comparison with `3B2D8` and `3AAF8` closed two session-077 gaps:
- single-host prepare unlinks inflight iff an accepted landscape override was active, then clears landscape state;
- resetHostingState mirror path does the same;
- reset does not increment host generation and leaves hosted orientation value intact, matching the raw-state subset already reconstructed.

## R-075 — 3F3F0 slot resize state/IPC half

Directly read `3F3F0.c`; cross-checked the same landscape size swap in `400D0.c`, `40C5C.c`, and `40DA8.c`.

Exact 3F3F0 state/IPC gate:
- slot index <= 2;
- main thread;
- host active;
- slot index < slotCount;
- hosted bid non-empty;
- slot not marked CarPlay UI;
- width >= 1 and height >= 1.

When gate passes:
- store raw width/height into that slot;
- publish `uiapp.state` with shouldBridge=YES, current hosted orientation, isSplit=YES, and the raw unswapped dimensions.

Original then mutates two private counters, probes the hosted scene, conditionally swaps dimensions, and calls private scene-layout helper `3F5C0`. Those private pieces remain outside the executable runtime.

Promoted:
- `DDUpdateHostSlotRenderSize(slot,size)` for the exact state/IPC half.
- `DDApplyLandscapeSwapToSize(size)`:
  - only active when an accepted landscape override exists;
  - only when `swap` is true;
  - only when both dimensions are positive;
  - returns height/width swapped;
  - otherwise returns input unchanged.

Important distinction preserved:
- raw host mirror size and uiapp.state payload are unswapped;
- swap applies only to downstream private scene-layout dimensions.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier = NOT_CONFIGURED, expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest.

Session-077 GitHub Actions build was GREEN per user. Session-078 Objective-C Darwin stat/open/write and resize-state changes require the next pushed macOS CI compiler run.

## Next
R-076 after CI green:
- inspect geometry consumers around `3F5C0`, `3257C`, and `400D0`;
- promote only pure geometry transform/decision helpers whose complete contracts are recoverable;
- recover cswap/rotation semantics only if direct evidence is complete;
- do not instantiate, probe, attach, or mutate private SpringBoard scene/view objects;
- keep 73E8/80D0 and full 7E908 unresolved until missing contracts are recovered.
