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
7. Re-publish on `com.sensetechlab.settings.changed`.

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
