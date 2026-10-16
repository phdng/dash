# DuoDash OLLVM — full-strength scoped evaluation

The GitHub Actions workflow builds the unmodified Theos variant first and
uploads `DuoDashReconstruction`. On push/PR (or manual runs with the **ollvm**
checkbox checked), it then attempts the pinned standalone OLLVM pass plugin
with Homebrew LLVM 19, producing `DuoDashReconstruction-OLLVM`.

**This is LLVM control-flow/instruction obfuscation, not literal encryption
of the dylib or its functions.** It does not encrypt string constants.
The four passes below are all supported by this pinned `obfuscator` plugin;
"full-strength" here means an aggressive evaluation profile for these four
passes, **not** that every function is obfuscated or that reverse engineering
is impossible.

## Strong evaluation profile

The `policy.json` profile `full_strength_eval` enables:

| Pass | Option | Setting |
| --- | --- | --- |
| Split basic blocks | `enable_split`, `split_n` | true, 4 |
| Bogus control flow | `enable_bcf`, `bcf_prob`, `bcf_times` | true, 100%, 2 |
| Flattening | `enable_fla` | true |
| Instruction substitution | `enable_sub`, `sub_times` | true, 3 |

The earlier full-file coverage of `LicenseHelpers.m` and
`PrefsResolver.m` is retained using the `existing_coverage` profile
(all four passes, with the previous default-equivalent 30% BCF probability,
one BCF iteration, two-way splitting and one substitution iteration).
Later rules **override** selected functions with the stronger profile:

- `LicenseHelpers.m`: `DDLicenseIsPrintableASCIIString` and
  `DDLicenseKeyPrefixIndex`.
- `PrefsResolver.m`: `DDAppBridgeBaseClassification`.
- **New coverage:** `VersionDeviceHelpers.m`:
  `DDVersionTupleAtLeast` and `DDVersionDeviceSanitizeMachineModel`.
- **New coverage:** `ToggleValueHelpers.m`: `DDFontFloorOverrideValue`.
- Build-only `scripts/ollvm_probe.c`: `dd_ollvm_probe`,
  `dd_ollvm_probe_branch`, and `dd_ollvm_probe_check`.

These six selected production functions are input validation/classification
helpers. CarPlay hosting, geometry, preferences repair/publishing and
startup code are excluded from the **strong** profile. Changing
`policy.json` is sufficient to expand or reduce this experiment; no
obfuscation annotations are inserted into runtime source code.

The aggressive settings can increase CPU use, object size, compiler time,
and crash risk. It is **not recommended to apply this profile to all source
functions** without profiling and real-device regression testing.

## CI evaluation and artifacts

1. The normal Apple Clang/Xcode preflight and Theos build run first.
2. LLVM 19 and `lich4/ollvm-pass` at
   `592f215f852e3957da01b2b15024dc63713a462e` are used to build
   the `Obfuscator` plugin from source (no downloaded compiler binary).
3. The `ollvm_probe.c` fixture is compiled for iOS arm64 with the plugin.
   `scripts/verify_ollvm_log.py` fails CI unless **all four** pass
   invocations appear for **all three** target fixture functions.
4. On the macOS runner, both Apple Clang (baseline) and OLLVM Clang build
   a native executable from the same fixture. The output of all three
   functions for **513** input values is compared byte-for-byte.
   This checks semantic equivalence on the fixture, not on the real
   iPhone tweak.
5. The iOS tweak is then rebuilt with `OLLVM=1`. The log is checked
   for every pass on each of the **six selected production functions**;
   a missing event fails the workflow.
6. The workflow uploads the OLLVM dylib separately and adds a comparison
   of the baseline versus obfuscated **dylib file sizes and SHA-256 values**
   to the GitHub Actions job summary.

Only if those steps succeed is `DuoDashReconstruction-OLLVM` uploaded.
The baseline `DuoDashReconstruction` is uploaded before OLLVM work starts
and is still accessible if the OLLVM path fails.

Source-obfuscation events in the logs show that the plugin executed.
They do not by themselves prove the resulting binary is resistant to
analysis. A binary disassembly review and on-device functional testing
are required to judge actual protection and compatibility.

## Local checks

```sh
python3 scripts/test_ollvm_integration.py
python3 scripts/verify_reconstruction.py
python3 scripts/test_dock_geometry_vectors.py
```

The full compile and native comparison require macOS with the correct
LLVM/Clang, Theos and Apple SDK. On a non-macOS workspace, the policy
tests can pass while the new full-strength build remains unverified.

To restore a basic CI run manually, uncheck **ollvm** at
**Actions → Build Reconstruction → Run workflow**. To tune strength,
adjust the named profile in `policy.json`, then rerun CI. Avoid adding
runtime-sensitive modules until on-device testing passes.

Upstream: https://github.com/lich4/ollvm-pass
