# Optional OLLVM build in GitHub Actions

The regular Reconstruction workflow keeps its existing Apple Clang/Xcode
preflights and default Theos build. A separate, manual **OLLVM** mode builds
the iOS tweak with a LLVM 19 Clang and a version-matched third-party OLLVM
pass plugin (not Apple's system Clang).

## Trigger

1. Open **Actions → Build Reconstruction → Run workflow**.
2. Set **ollvm = true**.
3. Download artifact **DuoDashReconstruction-OLLVM** if the job succeeds.

Without this option, push/PR/manual runs retain the standard artifact
`DuoDashReconstruction`. The mode is not silently enabled on push/PR
because this is a separate compiler and needs real-device validation.

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

When OLLVM mode is off, the Makefile and workflow do not require LLVM 19,
the plugin, or `policy.json`.
