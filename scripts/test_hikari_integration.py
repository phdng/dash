#!/usr/bin/env python3
"""Static Hikari integration guards and fail-closed audit self-tests."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "scripts" / "hikari_eval"
policy = json.loads((TRIAL / "policy.json").read_text(encoding="utf-8"))
assert set(policy) == {"policy_map", "policies"}
assert policy["policy_map"] == {
    "hikari_probe_string": {"enable-strcry": True, "strcry_prob": 100},
    "hikari_probe_const": {
        "enable-constenc": True,
        "constenc_subxor": True,
        "constenc_subxor_prob": 100,
        "constenc_togv": False,
        "constenc_togv_prob": 50,
        "constenc_times": 1,
    },
}
assert len(policy["policies"]) == 2
for rule, func, pol in (
    (policy["policies"][0], "dd_hikari_probe_string", "hikari_probe_string"),
    (policy["policies"][1], "dd_hikari_probe_const", "hikari_probe_const"),
):
    assert re.fullmatch(rule["module"], "probe.c")
    assert re.fullmatch(rule["func"], func)
    assert rule["policy"] == pol
    assert not re.fullmatch(rule["func"], "dd_hikari_probe_other")

source = (TRIAL / "probe.c").read_text(encoding="utf-8")
runner = (TRIAL / "runner.c").read_text(encoding="utf-8")
assert "DUODASH_HIKARI_CANARY_ONLY_7F29D1B3" in source
assert "DUODASH_HIKARI_CANARY_ONLY_7F29D1B3" not in runner
for func in ("dd_hikari_probe_string", "dd_hikari_probe_const"):
    assert re.search(r"\b" + func + r"\s*\(", source)
assert "for (int value = -256; value <= 256; ++value)" in runner

workflow = (ROOT / ".github/workflows/hikari-evaluation.yml").read_text(
    encoding="utf-8"
)
assert "workflow_dispatch:" in workflow
assert not re.search(r"^  (?:push|pull_request):", workflow, re.MULTILINE)
assert "runs-on: macos-latest" in workflow
assert "working-directory: scripts/hikari_eval" in workflow
assert "git -C \"$source_dir\" checkout -q --detach FETCH_HEAD" in workflow
assert "592f215f852e3957da01b2b15024dc63713a462e" in workflow
assert '-S "$source_dir/hikari"' in workflow
assert "-DLLVM_DIR=" in workflow and "llvm@19" in workflow
assert "fpass-plugin=\"$HIKARI_PLUGIN\"" in workflow
assert "python3 audit.py native" in workflow
assert "--protected-executable out/probe-native-hikari" in workflow
assert "python3 audit.py ios" in workflow
assert "arm64-apple-ios14.0" in workflow
assert "DuoDash-Hikari-Evaluation-Diagnostics" in workflow
assert "DuoDashReconstruction-OLLVM" not in workflow
assert "make clean all" not in workflow
assert "DuoDashReconstruction_FILES" not in workflow

existing_policy = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))
assert "full_strength_eval" in existing_policy["policy_map"]
assert all("enable-strcry" not in item for item in existing_policy["policy_map"].values())
assert all("enable-constenc" not in item for item in existing_policy["policy_map"].values())

spec = importlib.util.spec_from_file_location("hikari_audit", TRIAL / "audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
log = "\n".join(audit.PASS_LINES)
plain_bytes = b"prefix" + audit.MARKER + b"suffix"
protected_bytes = b"transformed non-plaintext object"
audit.audit_object(plain_bytes, protected_bytes, log)


def expect_failure(callback, *args):
    try:
        callback(*args)
    except AssertionError:
        return
    raise AssertionError("Expected the fail-closed audit to reject bad data")


expect_failure(audit.audit_object, plain_bytes, protected_bytes, "")
expect_failure(audit.audit_object, plain_bytes, plain_bytes, log)
expect_failure(audit.audit_object, b"missing", protected_bytes, log)
expect_failure(audit.audit_object, plain_bytes, protected_bytes,
               audit.PASS_LINES[0])

vectors = "\n".join(f"{index}:{index & 0xffffffff:08x}:00000000"
                    for index in range(-256, 257)) + "\n"
audit.audit_output(vectors, vectors)
expect_failure(audit.audit_output, vectors, vectors.replace("00000000", "11111111", 1))
expect_failure(audit.audit_output, vectors, "not enough")
expect_failure(audit.audit_output, vectors, "")


# Gated real-source Objective-C pilot, isolated from the production tweak.
pilot_policy = json.loads((TRIAL / "pilot_policy.json").read_text(encoding="utf-8"))
assert set(pilot_policy["policy_map"]) == {"objc_pilot_string", "objc_pilot_const"}
assert pilot_policy["policy_map"]["objc_pilot_string"] == {
    "enable-strcry": True, "strcry_prob": 100,
}
assert pilot_policy["policy_map"]["objc_pilot_const"] == {
    "enable-constenc": True, "constenc_subxor": True,
    "constenc_subxor_prob": 100, "constenc_togv": False,
    "constenc_togv_prob": 50, "constenc_times": 1,
}
assert len(pilot_policy["policies"]) == 2
for rule, func, profile in (
    (pilot_policy["policies"][0], "DDVersionDeviceSanitizeMachineModel", "objc_pilot_string"),
    (pilot_policy["policies"][1], "DDVersionDeviceFormatClientVersion", "objc_pilot_const"),
):
    assert re.fullmatch(rule["module"], "pilot.m")
    assert re.fullmatch(rule["func"], func)
    assert rule["policy"] == profile
    assert not re.fullmatch(rule["func"], "DDRepublishAppBridgeResolvedSnapshot")

extract_spec = importlib.util.spec_from_file_location("extract_pilot", TRIAL / "extract_pilot.py")
extract = importlib.util.module_from_spec(extract_spec)
extract_spec.loader.exec_module(extract)
original = (ROOT / "re/RECONSTRUCTION/VersionDeviceHelpers.m").read_text(encoding="utf-8")
pilot_source = extract.render(original)
assert "#import <Foundation/Foundation.h>" in pilot_source
assert "DuoDashShared.h" not in pilot_source
assert "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,_-" in pilot_source
for func in extract.FUNCTIONS:
    assert pilot_source.count(func + "(") == 1
assert "DDVersionDeviceFormatOSVersion" not in pilot_source
assert "DDVersionTupleAtLeast" not in pilot_source
try:
    extract.extract_function(original, "DDDoesNotExist")
except ValueError:
    pass
else:
    raise AssertionError("Source extraction must reject unknown symbols")

pilot_runner = (TRIAL / "pilot_runner.m").read_text(encoding="utf-8")
assert 'assert_equals(DDVersionDeviceSanitizeMachineModel' in pilot_runner
assert 'assert_equals(DDVersionDeviceFormatClientVersion' in pilot_runner
samples_block = pilot_runner.split("NSString *samples[] = {", 1)[1].split("};", 1)[0]
assert len(re.findall(r'@"(?:[^"\\]|\\.)*"', samples_block)) == 22
assert "code = 32; code <= 126;" in pilot_runner
assert "-fobjc-arc" in workflow
assert workflow.count("audit_pilot.py") == 2
assert "python3 extract_pilot.py --output" in workflow
assert "cp pilot_policy.json" in workflow
assert "HIKARI_PILOT_DIR" in workflow
assert "pilot-ios-hikari.o" in workflow
assert "xcrun nm -g pilot-ios-hikari.o" in workflow
assert "_DDVersionDeviceSanitizeMachineModel" in workflow
assert "_DDVersionDeviceFormatClientVersion" in workflow
assert "hikari-objc-native.log" in workflow
assert "hikari-objc-ios.log" in workflow
assert workflow.index("name: Prepare real DuoDash Objective-C helper pilot") < workflow.index("name: Compare real Objective-C helpers on macOS")
assert workflow.index("name: Compare real Objective-C helpers on macOS") < workflow.index("name: Cross-compile real Objective-C helpers for iOS arm64")

pilot_spec = importlib.util.spec_from_file_location("audit_pilot", TRIAL / "audit_pilot.py")
pilot_audit = importlib.util.module_from_spec(pilot_spec)
pilot_spec.loader.exec_module(pilot_audit)
log = "\n".join(pilot_audit.REQUIRED_LOGS)
plain_obj = b"baseline_" + pilot_audit.ALLOWED_MODEL_ALPHABET + b"_end"
protected_obj = b"hikari_object_without_plaintext"
pilot_audit.check_objects(plain_obj, protected_obj, log)
expect_failure(pilot_audit.check_objects, plain_obj, protected_obj, "")
expect_failure(pilot_audit.check_objects, plain_obj, plain_obj, log)
expect_failure(pilot_audit.check_objects, b"no expected string", protected_obj, log)
pilot_lines = "\n".join(f"{i:03d}:xyz:abc" for i in range(213)) + "\n"
pilot_audit.check_outputs(pilot_lines, pilot_lines)
expect_failure(pilot_audit.check_outputs, pilot_lines, pilot_lines.replace("xyz", "zzz", 1))
expect_failure(pilot_audit.check_outputs, pilot_lines, "")
assert "hikari-evaluation.yml" not in (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")

print("Hikari C fixture and DuoDash real-source Objective-C pilot: PASS")
