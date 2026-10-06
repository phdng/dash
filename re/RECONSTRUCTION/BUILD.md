# Building the reconstruction

The repository now has a real Theos build target named `DuoDashReconstruction`.

## What is compiled

The executable target intentionally includes only:

- `re/RECONSTRUCTION/Tweak.x`
- `re/RECONSTRUCTION/ReconstructionRuntime.m`

The other `RECONSTRUCTION/*.m` files remain static-evidence synthesis modules. They are not force-compiled with fake declarations because many still contain unresolved private symbols and explicit UNKNOWN/HYPOTHESIS branches.

The current runtime implements the evidence-backed, compile-safe surface:

1. AC5FC-style role detection by executable-path suffix.
2. SpringBoard-only startup.
3. The reconstructed clear-panes one-shot.
4. AppBridge settings snapshot generation.
5. Atomic cache write to `/var/tmp/com.sensetechlab.appbridge.plist`.
6. `com.sensetechlab.appbridge.resolved` notification.
7. Immediate republish observers for `settings.changed`, `appbridge.listchanged`, and `autostart.changed` (the evidence-safe half of `29198`).
8. Compile-safe prefs setters matching `746C` (layout 1..8), `84D8` (CarPlay UI normalize/dedup), and `637E8/836C` (resolved-plist autostart toggle).
9. Prefs-only logical CarPlay UI eviction matching `85B8` (no kill/view teardown).
10. Exact compile-safe cache readers matching `7044`, `70FC`, and `836C`.
11. Pure prefs readers matching `8058` (missing keypane => ON) and the `7EA4` font-floor override/parser (valid range 8..96); private per-host UI broadcasts remain excluded.
12. Read-only liveness probe matching `7764C`: SpringBoard bundle gate, `{pid,path,bid}` type checks, optional bundle-id filter, `proc_pidpath` + exact path compare, and the original non-SpringBoard sentinel. The target links `libproc`; no private SpringBoard classes are used by this helper.
13. Pure integer validation/self-healing helpers matching `7E63C/7EEDC`: exact status classes (missing/number/string/error), integer-only CFNumber acceptance, inclusive bounds, NSString coercion, and writes/fixes only for status 2/3. These helpers are not yet wired into full `7E908` because some decompiled call-site bounds remain unresolved.
14. Exact resolved-cache numeric wrappers where arguments survive decompilation: `8154` (`key`, range 0..99, default 0) and `81EC` (`appbridge_split_frac_layout`, range 0..8, default 0). `73E8` layout and `80D0` ratio remain intentionally unresolved because their `7E63C` arguments are elided in the available export.
15. Runtime-resolved distributed-notification IPC matching `8900/887C/8934/8C28/8D78`: dynamic `NSDistributedNotificationCenter` lookup, exact add/post selectors, and immediate delivery without linking a private framework. The executable runtime also includes exact payload builders for `97A0` host-refused state and `9424` host state (`activated`, bundle id, `sbPid`, conditional CarPlay UI rect/more/gen/killed fields).
16. Exact AppBridge request/status payload builders matching `8CC0/8DF8/8F34/91B4/986C`: UI-app request, single-host request, split-host request, the full 11-field frame metadata snapshot, and CarPlay-UI status. `DDHostFrameMetrics` is layout-asserted to 104 bytes so the fields used by `8F34` stay at the recovered offsets.
17. Cached UI-state model matching the `74C8 -> 7EA4 -> 8058` update order plus Immediate `fontfloor.changed` / `keypane.changed` callbacks. `89D8` is now represented with the cached values rather than fresh prefs reads.
18. Runtime-resolved DDz2 active-host enumeration matching `29810` and the per-bundle `291F4/29400` distributed broadcasts. The private `30960` toast emitted when keypane is switched OFF remains intentionally excluded.

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
