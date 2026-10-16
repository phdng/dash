#!/usr/bin/env python3
"""Cross-platform checks for baseline coverage and scoped OLLVM strong profile."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))
assert set(policy) == {"policy_map", "policies"}
assert policy["policy_map"]["existing_coverage"] == {
    "enable_split": True,
    "split_n": 2,
    "enable_bcf": True,
    "bcf_prob": 30,
    "bcf_times": 1,
    "enable_fla": True,
    "enable_sub": True,
    "sub_times": 1,
}
assert policy["policy_map"]["full_strength_eval"] == {
    "enable_split": True,
    "split_n": 4,
    "enable_bcf": True,
    "bcf_prob": 100,
    "bcf_times": 2,
    "enable_fla": True,
    "enable_sub": True,
    "sub_times": 3,
}
rules = policy["policies"]
assert len(rules) == 6
assert all(rule["policy"] in policy["policy_map"] for rule in rules)


def policy_for(source: str, function: str):
    """Later matching rules override earlier matching rules (OLLVM semantics)."""
    found = None
    for rule in rules:
        if (re.fullmatch(rule["module"], source)
                and re.fullmatch(rule["func"], function)):
            found = rule["policy"]
    return found


strong_targets = {
    "re/RECONSTRUCTION/LicenseHelpers.m": (
        "DDLicenseIsPrintableASCIIString",
        "DDLicenseKeyPrefixIndex",
    ),
    "re/RECONSTRUCTION/PrefsResolver.m": (
        "DDAppBridgeBaseClassification",
    ),
    "re/RECONSTRUCTION/VersionDeviceHelpers.m": (
        "DDVersionTupleAtLeast",
        "DDVersionDeviceSanitizeMachineModel",
    ),
    "re/RECONSTRUCTION/ToggleValueHelpers.m": (
        "DDFontFloorOverrideValue",
    ),
    "scripts/ollvm_probe.c": (
        "dd_ollvm_probe",
        "dd_ollvm_probe_branch",
        "dd_ollvm_probe_check",
    ),
}
for source, funcs in strong_targets.items():
    content = (ROOT / source).read_text(encoding="utf-8")
    for func in funcs:
        assert policy_for(source, func) == "full_strength_eval", (source, func)
        assert re.search(r"\b" + re.escape(func) + r"\s*\(", content), func

for source, function in (
    ("re/RECONSTRUCTION/LicenseHelpers.m", "DDLicenseDecodeHex"),
    ("re/RECONSTRUCTION/LicenseHelpers.m", "DDLicenseVerdictText"),
    ("re/RECONSTRUCTION/PrefsResolver.m", "DDRepublishAppBridgeResolvedSnapshot"),
    ("re/RECONSTRUCTION/PrefsResolver.m", "DDRepairAppBridgeConfigIfNeeded"),
):
    assert policy_for(source, function) == "existing_coverage", (source, function)

for source, function in (
    ("re/RECONSTRUCTION/VersionDeviceHelpers.m", "DDVersionDeviceFormatClientVersion"),
    ("re/RECONSTRUCTION/ToggleValueHelpers.m", "DDSimulatedSpeedOverrideValue"),
    ("re/RECONSTRUCTION/HostFlowAdapter.m", "DDHostDockHostingPlanForObservedBounds"),
    ("re/RECONSTRUCTION/ReconstructionRuntime.m", "DDNormalizeIntegerSetting"),
    ("scripts/ollvm_probe.c", "main"),
):
    assert policy_for(source, function) is None, (source, function)

makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
assert "ifeq ($(OLLVM),1)" in makefile
assert "-fpass-plugin=$(OLLVM_PLUGIN)" in makefile
workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
assert "default: true" in workflow
assert (
    "OLLVM_ENABLED: ${{ github.event_name != 'workflow_dispatch' || inputs.ollvm == true }}"
    in workflow
)
assert "if: ${{ inputs.ollvm == true }}" not in workflow
assert workflow.count("if: ${{ env.OLLVM_ENABLED == 'true' }}") == 6
steps = (
    "name: Build tweak (standard)",
    "name: Upload standard artifact",
    "name: Install LLVM 19 and compile pinned OLLVM plugin",
    "name: Verify OLLVM actually transforms iOS arm64 code",
    "name: Compare native OLLVM probe with unmodified Clang output",
    "name: Build tweak (OLLVM)",
    "name: Collect OLLVM dylib",
    "name: Upload OLLVM artifact",
)
positions = [workflow.index(step) for step in steps]
assert positions == sorted(positions)
assert "name: DuoDashReconstruction-OLLVM" in workflow
assert "name: DuoDashReconstruction\n" in workflow
assert workflow.count("python3 scripts/verify_ollvm_log.py probe") == 2
assert "python3 scripts/verify_ollvm_log.py tweak" in workflow
assert "cmp \"$RUNNER_TEMP/probe_plain.txt\" \"$RUNNER_TEMP/probe_obfuscated.txt\"" in workflow

spec = importlib.util.spec_from_file_location(
    "verify_ollvm_log", ROOT / "scripts/verify_ollvm_log.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
expected = {
    "probe": set(strong_targets["scripts/ollvm_probe.c"]),
    "tweak": {
        name
        for source, functions in strong_targets.items()
        if source != "scripts/ollvm_probe.c"
        for name in functions
    },
}
for kind, functions in module.TARGETS.items():
    assert set(functions) == expected[kind]
    good = "\n".join(
        f">>>> run {pass_name} on {func}"
        for func in functions for pass_name in module.PASSES
    )
    module.verify(good, kind)
    try:
        module.verify(good.rsplit("\n", 1)[0], kind)
    except AssertionError:
        pass
    else:
        raise AssertionError("Missing pass log must fail the build")

print("OLLVM existing coverage + six strong tweak functions + CI guards: PASS")
