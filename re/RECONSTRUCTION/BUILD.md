# Building the reconstruction

The repository now has a real Theos build target named `DuoDashReconstruction`.

## What is compiled

The executable target intentionally includes only:

- `re/RECONSTRUCTION/Tweak.x`
- `re/RECONSTRUCTION/ReconstructionRuntime.m`

The other `RECONSTRUCTION/*.m` files remain static-evidence synthesis modules. They are not force-compiled with fake declarations because many still contain unresolved private symbols and explicit UNKNOWN/HYPOTHESIS branches.

The current runtime implements the evidence-backed, compile-safe surface:

1. AC5FC-style role detection by executable-path suffix.
2. Role-gated startup: SpringBoard prefs/host-side safe runtime plus the UIApp IPC/state consumer; Preferences/CarPlay/mediaserverd/kbd private-hook branches remain inactive.
3. The reconstructed clear-panes one-shot.
4. AppBridge settings snapshot generation.
5. Atomic cache write to `/var/tmp/com.sensetechlab.appbridge.plist`.
6. `com.sensetechlab.appbridge.resolved` notification.
7. Immediate republish observers for `settings.changed`, `appbridge.listchanged`, and `autostart.changed` (the evidence-safe half of `29198`).
8. Compile-safe prefs setters matching `746C` (layout 1..8), `84D8` (CarPlay UI normalize/dedup), and `637E8/836C` (resolved-plist autostart toggle).
9. Prefs-only logical CarPlay UI eviction matching `85B8` (no kill/view teardown).
10. Exact compile-safe cache readers matching `7044`, `70FC`, and `836C`.
11. Pure prefs readers matching `8058` (missing keypane => ON) and the `7EA4` font-floor override/parser (valid range 8..96); their later per-host broadcast wiring is covered by items 17-18.
12. Read-only liveness probe matching `7764C`: SpringBoard bundle gate, `{pid,path,bid}` type checks, optional bundle-id filter, `proc_pidpath` + exact path compare, and the original non-SpringBoard sentinel. The target links `libproc`; no private SpringBoard classes are used by this helper.
13. Pure integer validation/self-healing helpers matching `7E63C/7EEDC`: exact status classes (missing/number/string/error), integer-only CFNumber acceptance, inclusive bounds, NSString coercion, and writes/fixes only for status 2/3. These helpers are not yet wired into full `7E908` because some decompiled call-site bounds remain unresolved.
14. Exact resolved-cache numeric wrappers where arguments survive decompilation: `8154` (`key`, range 0..99, default 0) and `81EC` (`appbridge_split_frac_layout`, range 0..8, default 0). `73E8` layout and `80D0` ratio remain intentionally unresolved because their `7E63C` arguments are elided in the available export.
15. Runtime-resolved distributed-notification IPC matching `8900/887C/8934/8C28/8D78`: dynamic `NSDistributedNotificationCenter` lookup, exact add/post selectors, and immediate delivery without linking a private framework. The executable runtime also includes exact payload builders for `97A0` host-refused state and `9424` host state (`activated`, bundle id, `sbPid`, conditional CarPlay UI rect/more/gen/killed fields).
16. Exact AppBridge request/status payload builders matching `8CC0/8DF8/8F34/91B4/986C`: UI-app request, single-host request, split-host request, the full 11-field frame metadata snapshot, and CarPlay-UI status. `DDHostFrameMetrics` is layout-asserted to 104 bytes so the fields used by `8F34` stay at the recovered offsets.
17. Cached UI-state model matching the `74C8 -> 7EA4 -> 8058` update order plus Immediate `fontfloor.changed` / `keypane.changed` callbacks. `89D8` is now represented with the cached values rather than fresh prefs reads.
18. Runtime-resolved DDz2 active-host enumeration matching `29810` and the per-bundle `291F4/29400` distributed broadcasts. The private `30960` toast emitted when keypane is switched OFF remains intentionally excluded.
19. UIApp-side IPC consumer matching the evidence-safe portion of `4CBDC` plus `4407C/443FC/444C4/445F8/446E4/42F10`: bundle-scoped distributed observers, initial/foreground state request, exact parsing/defaults into a compile-safe bridge-state cache, 3-second stale-state timeout, and background teardown knob semantics. `422D0` UIKit relayout/font mutation and the key-probe half of `4CBDC` remain excluded.
20. SpringBoard host-slot mirror for the raw DDz2 state consumed by `3F224/3B738/3D4FC`: 1..3 slots, ordered NSString canonicalization/dedup, per-slot size and CarPlay-UI flags, split/orientation state, and a monotonic host generation. `3F224` UIApp request handling is wired to this mirror, eliminating the previous slot-0-size substitution risk without reading private globals.
21. Exact retry timing/state gates for `3B738/3ED88` and `3D4FC/3DC38`. The recovered `off_154160` delay table is `{0.0, 0.4, 0.9, 1.8, 3.5}` seconds; retries require the same generation plus active host state, and geometry pushes re-match the bundle then prefer the current slot size when both dimensions are at least 1.
22. Compile-safe DDz2 slot-state helpers matching `3D6EC` and the state/IPC half of `3D704`: direct CarPlay-UI flag writes, main-thread/slot-count conversion gate, `uiapp.state` bridge-off push with `isSplit=YES`, retained bid, and final CarPlay flag. Private hosted-view removal/invalidation remains excluded.
23. Pure pre-private host preparation from `3B2D8/3CC44`: single-host mirror size honors `duodash_ab_canvas=portrait` via portrait-normalized screen bounds, otherwise `duodash_ab_rscale` accepts only 1..3 and defaults to 2; single-host prep clears to one non-CarPlay slot and resolves orientation through `3DFC8`. Split prep preserves native per-slot sizes and uses the already-resolved split orientation. The pure landscape parser accepts only orientation 3/4 plus `swap`, `cswap`, and finite `rot=` within ±360; inflight/tripped inter-process acceptance remains separate.
24. Evidence-safe dismiss state/IPC matching `3D8A8/3D990/3AAF8`: marshal to the main queue, send bridge-off state for every non-CarPlay hosted bid (slot0 non-split, slots1/2 split), then clear host mirror state without incrementing generation or clearing orientation. Private aux-scene/view removal and controller invalidation remain excluded.
25. Exact evidence-safe `3CC44` landscape coordination: reset lscape state, ignore override when `.tripped` exists, read `.inflight` PID with NSString `intValue`, clear stale foreign inflight only when `respring_planned` and inflight stats both exist and planned mtime-seconds is newer/equal, otherwise write `tripped\n` and remove inflight for a live foreign PID. Accepted parser state stores orientation/swap/cswap/rotation and rewrites inflight as the current PID with `O_WRONLY|O_CREAT|O_TRUNC` mode 0644. Invalid slot-count requests still return before any file side effects. Private `sub_372CC` keyboard-layer hooks remain excluded.
26. Landscape-aware slot resize state/IPC from `3F3F0`: exact main-thread/active/slot/bid/non-CarPlay/min-size gates, raw per-slot size update, and `uiapp.state` publish with `isSplit=YES`. The repeated lscape `swap` transform is represented separately and only swaps positive width/height for downstream private scene layout; raw mirror/IPC dimensions remain unswapped.
27. Pure landscape geometry plan extracted from `3257C`: valid only for accepted lscape state + slot 0..2 + non-empty hosted bid + positive native/slot dimensions; scale is `min(slotW/nativeW, slotH/nativeH)` using unswapped native dimensions, `cswap` swaps bounds width/height only, rotation is converted from degrees to radians and concatenated after scale, and center is the midpoint of the slot rectangle. The plan is data-only and does not instantiate UIView/CGAffineTransform. `3E9A8`'s `duodash_ab_noscenegeom` inverse gate is also reconstructed with first-read memoization.
28. Pure pane-orientation decision from `41C24/3E534/3F75C/3FAF8`: generation-scoped `duodash_ab_nopaneorient` cache, runtime capability probe for `UIApplicationSceneSettings._interfaceOrientation`, landscape-active suppression, aux-or-host orientation selection supplied by the caller, and final 1..4 range gate. Private settings mutation via `updateSettingsWithBlock:` remains excluded.
29. Aux-scene pre/private state boundary from `3C368/3E4A8/3E590/3E428/3C808`: exact empty/size/hosted-non-CarPlay/aux-controller preconditions, runtime capability probe for FBScene block settings + UIMutableApplicationSceneSettings integer orientation setter, portrait normalization only when requested orientation is 3/4 and neither direct-ivar nor mutation capability exists, explicit post-`applicationWithBundleIdentifier:` commit gate, aux generation + `auxnoswap/noauxsid/noapplydiff` state, and teardown mirror clear. No SBApplicationController/SBDeviceApplicationSceneEntity/SBAppViewController instance is created.
30. Pure aux desired-settings plan from `3E670`: valid only with aux bid + orientation 3/4 + positive native size + no direct `_interfaceOrientation` ivar; `duodash_kp_auxnoswap` controls whether desired frame swaps native width/height. The extracted early-out decision matches the original applied-state behavior: before first apply => update, applied-without-current-settings => no update, otherwise suppress when width/height are each within ±0.5 and current orientation is zero or already equal. Private method/reentrancy/attempt-budget executor remains excluded.
31. Aux retry/settings state machine from `3C368/3E604/3E670/3EA0C`: exact create-kick delays `{0.1, 0.5, 1.5}` seconds, schedule gate (`auxOrient != 0` and no direct `_interfaceOrientation` ivar), generation+not-applied kick gate, `3E428` reset state (`generation++`, in-flight/applied/attempts reset, budget=10, `auxnoswap` refresh), 8-attempt cap, budget decrement/zero semantics, and explicit two-phase apply transition. Reserving an attempt sets in-flight and captures generation; entering the external executor clears in-flight and acquires the reentrancy guard; only an explicit completion after the private invocation returned marks applied and decrements budget. `auxSceneObject` and `updateSettingsWithBlock:` are never invoked by the reconstruction runtime.
32. Pure post-identity scene routing from `400D0/4138C/41CBC/41E08/3FB54/3FFC0`: the caller must supply an already-resolved bundle identifier, so private `3FBC8` client/scene traversal is not reproduced. `fbsUpdate` routing accepts only non-CarPlay hosted slots before falling back to aux; `avc sceneHandle` routing checks any configured hosted slot, including CarPlay-flagged slots, before aux. Aux matching preserves the exact 3FFC0 non-empty/equality rule. Returned descriptors are data-only (`None/HostSlot/Aux`) and do not call private settings/layout executors.
33. Pure identity size/orientation/settings decisions from `41D80/41E94/3FAF8/40514`, cross-checked against raw ARM64 because the decompiler mis-typed `41E94` as `void`. Native-size selection prefers a matching non-CarPlay host slot, then aux, else zero. `41E94` aux output portrait-normalizes only when aux orientation is 3/4 and width exceeds height; non-aux output reuses the accepted-landscape positive-dimension swap gate. Raw settings orientation chooses nonzero aux orientation only for aux identity, otherwise host orientation. The `40514` pre-private decisions are exposed as data-only helpers for direct-orientation-repair eligibility, snapshot equivalence (orientation/foreground exact + frame width/height within ±0.5), and settings-diff-clear eligibility honoring `duodash_kp_noapplydiff`. No `FBSSceneSettingsDiff`, private ivar write, `setSettingsDiff:`, or settings executor is invoked.

Where the original calls unresolved helpers (for example app filtering and normalized split geometry), the runtime preserves typed raw values instead of inventing behavior.

## Local verification

On any platform with Python 3:

```sh
python3 scripts/verify_reconstruction.py
```

This verifies the reconstruction inventory, build inputs, Makefile wiring, and the Substrate filter copied from the original artifact.

## Build on macOS

With Xcode and Theos installed:

```sh
export THEOS=~/theos
make clean all
```

The GitHub Actions workflow performs the same compiler build on macOS and uploads the resulting dylib plus filter plist.

## CI

Workflow: `.github/workflows/build.yml`.

It runs on pushes and pull requests that change the build inputs or reconstruction tree, and can also be started manually with `workflow_dispatch`.

A green CI run means the compile-safe reconstruction target builds. It does **not** mean the remaining evidence-only private-hook modules have been runtime-verified on a jailbroken device.
