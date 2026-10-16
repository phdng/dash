# OLLVM build in GitHub Actions

The Reconstruction workflow keeps its Apple Clang/Xcode preflights and
always builds and uploads the standard Theos dylib first. On **push** and
**pull_request**, it then automatically builds the additional OLLVM variant
using LLVM 19 Clang and a version-matched third-party LLVM pass plugin.

## Trigger and artifacts

- Push/PR: OLLVM is **enabled automatically**, so a successful workflow
  uploads **both** `DuoDashReconstruction` and `DuoDashReconstruction-OLLVM`.
- Manual: open **Actions → Build Reconstruction → Run workflow**;
  the **ollvm** checkbox is on by default and may be unchecked to skip
  the extra OLLVM build.
- The standard artifact uploads **before** OLLVM begins. If the OLLVM
  compiler/plugin fails, the workflow correctly reports failure, but the
  standard artifact remains available for troubleshooting.

A successful normal tweak build alone is not proof that OLLVM was used:
`Verify OLLVM actually transforms iOS arm64 code` and `Build tweak (OLLVM)`
must both succeed, followed by `Upload OLLVM artifact`.

## Toolchain, reproducibility and verification

- LLVM: Homebrew `llvm@19` (Clang and CMake package must match the plugin).
- OLLVM source: [lich4/ollvm-pass](https://github.com/lich4/ollvm-pass),
  pinned to commit `592f215f852e3957da01b2b15024dc63713a462e`.
- The `obfuscator` project is built from source in the GitHub runner;
  no unverified prebuilt Clang binary is downloaded.
- `OLLVM=1` injects `-fpass-plugin=<plugin>` and `-O1` into the
  **tweak's** Objective-C compilation through the project's Makefile.
  Theos uses LLVM 19 for Objective-C compile and Apple Clang for linking.
- `policy.json` selects only `LicenseHelpers.m` and `PrefsResolver.m`
  for one round of substitution (`sub`); geometry, hostflow and startup
  code are intentionally excluded for the first rollout.
- `scripts/ollvm_probe.c` is compiled for iOS arm64 with the plugin.
  The build fails if its pass log doesn't show real substitution execution.
  The tweak build is also fail-closed if no OLLVM pass ran on selected files.
- Output is still a `DuoDashReconstruction.dylib`; OLLVM changes the
  internals of generated code, not the dylib's interface or signing model.

To increase obfuscation, change the *policy* gradually (e.g. selectively
enable flattening) and rerun CI **plus on-device tests**; stronger passes
can change runtime semantics, increase size, and hurt performance.
Using an obfuscated build does **not** replace licensing, code signing,
or server-side protections.

## Local test

`python3 scripts/test_ollvm_integration.py` verifies the policy allowlist
and Makefile switch without requiring a macOS compiler. A full OLLVM build
requires the macOS GitHub Actions runner (or a properly configured macOS
Theos + LLVM 19 environment).

If OLLVM is manually disabled, the Makefile and workflow do not require
LLVM 19 or the pass plugin. Push/PR builds always attempt both variants.
On-device testing is still required before distributing the obfuscated build.
