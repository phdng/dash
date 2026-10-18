#!/usr/bin/env python3
"""K13 portable fail-closed canary proof tests. Synthetic data is NOT native."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_k13"
sys.path.insert(0, str(LAB))
import pilot
# pilot imports the K12 inventory helper, so importing an unqualified
# 'audit' may incorrectly resolve kagura_k12/audit.py from sys.path.
spec = importlib.util.spec_from_file_location(
    'kagura_k13_independent_audit', LAB / 'audit.py')
assert spec and spec.loader
verify_k13 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_k13)

PASS = "kagura-cse-break"


def reject(fn, what):
    try:
        fn()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("K13 negative gate admitted " + what)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def macho(cpu=0x0100000C, subtype=0, filetype=1):
    return struct.pack("<IIIIIIII", 0xFEEDFACF, cpu, subtype, filetype,
                       1, 0, 0, 0)


def source_registry():
    from inventory import COVERED, K8_KINDS
    items = []
    for name in COVERED:
        kind = K8_KINDS.get(name[7:], "FN")
        if name == "kagura-vm":
            items.append('KAGURA_INFRA_PASS("kagura-vm", VmPass())')
        else:
            items.append(f'KAGURA_{kind}_PASS(EnableX, "{name}", "x", X())')
    items.append('KAGURA_FN_PASS(CSEBreak, "kagura-cse-break", "x", kagura::CSEBreakPass())')
    return "\n".join(items) + "\n"


assert pilot.PASS == PASS
assert pilot.PASS_CLASS == "kagura::CSEBreakPass"
assert pilot.PIPELINE == "function(kagura-cse-break),verify"
assert pilot.VECTORS == 4096
assert pilot.REGISTRY_SHA == (
    "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa")
assert pilot.validate_registry(source_registry())["kind"] == "FN"
reject(lambda: pilot.validate_registry(source_registry().replace(
    "KAGURA_FN_PASS(CSEBreak,", "KAGURA_MOD_PASS(CSEBreak,")),
    "module-for-function kind")
reject(lambda: pilot.validate_registry(source_registry().replace(
    "KAGURA_FN_PASS(CSEBreak,", "KAGURA_FN_PASS(EnableX,")),
    "wrong pinned switch")
reject(lambda: pilot.validate_registry(source_registry().replace(
    '"kagura-cse-break"', '"kagura-cse-break-spoof"')),
    "renamed pass")
pilot.validate_trace(
    "Running pass: kagura::CSEBreakPass on dd_k8_evaluate (73 instructions)\n"
    "Running pass: VerifierPass on [module]\n"
    "Running pass: BitcodeWriterPass on [module]\n")
reject(lambda: pilot.validate_trace(
    "Running pass: kagura::BBCheckPass on dd_k8_evaluate (73 instructions)\n"
    "Running pass: VerifierPass on [module]\n"
    "Running pass: BitcodeWriterPass on [module]\n"), "wrong actual class")
log = ("DD_K8_SCHEMA=1\nDD_K8_VECTORS=4096\n"
       "DD_K8_CHECKSUM=25a3318e3d7d6525\nDD_K8_COMPLETE=PASS\n")
assert pilot.validate_native(log) == "25a3318e3d7d6525"
reject(lambda: pilot.validate_native(log.replace(
    "DD_K8_VECTORS=4096", "DD_K8_VECTORS=4095")), "runner vector tamper")
reject(lambda: pilot.validate_native(log + "EXTRA=FORGED\n"), "log extra")
pilot.ios_macho(macho())
pilot.native_macho(macho(cpu=0x01000007))
reject(lambda: pilot.ios_macho(macho(subtype=2)), "arm64e masquerading arm64")
reject(lambda: pilot.ios_macho(macho(cpu=0x01000007)), "x86 masquerading ios")
reject(lambda: pilot.ios_macho(macho(filetype=2)), "MH_EXECUTE not MH_OBJECT")
reject(lambda: pilot.native_macho(b"FAKE"), "nonMachO native object")

with tempfile.TemporaryDirectory(prefix="K13-artifact-fixture-") as temp:
    out = pathlib.Path(temp)
    registry_text = source_registry().encode()
    write(out / "pinned-registry.def", registry_text)
    write(out / "pinned-LICENSE", b"synthetic LICENSE")
    report = {
        "schema": 1,
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pinned_commit": pilot.PIN,
        "pinned_registry_sha256": sha(registry_text),
        "k12_verified_registry_sha256": pilot.REGISTRY_SHA,
        "upstream_license_sha256": sha(b"synthetic LICENSE"),
        "pass": PASS, "pass_kind": "FN", "pass_enable_flag": "CSEBreak",
        "pass_class": pilot.PASS_CLASS, "pipeline": pilot.PIPELINE,
        "fixture_sha256": pilot.sha(pilot.ROOT / "scripts/custom_ollvm/kagura_k8/fixture.c"),
        "runner_sha256": pilot.sha(pilot.ROOT / "scripts/custom_ollvm/kagura_k8/runner.c"),
        "llvm_major": 19, "targets": {},
        "iphone_runtime_executed": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "security_strength_claim": False,
    }
    for target in ("macos", "ios"):
        baseline_ir = (
            b"; ModuleID = 'baseline.bc'\n"
            b"source_filename = \"fixture.c\"\n"
            b"define i64 @dd_k8_evaluate(i64 %n) { ret i64 %n }\n")
        changed_ir = baseline_ir.replace(
            b"baseline.bc", b"cse-break.bc").replace(
            b"ret i64 %n", b"ret i64 %n\n; synthetic canary delta")
        prefix = target + "-"
        before_bc = b"BC\xc0\xde" + target.encode()
        after_bc = before_bc + b"post"
        before_obj = macho(cpu=0x01000007 if target == "macos" else 0x0100000C)
        after_obj = before_obj + b"synthetic"
        trace = (b"Running pass: kagura::CSEBreakPass on dd_k8_evaluate (73 instructions)\n"
                 b"Running pass: VerifierPass on [module]\n"
                 b"Running pass: BitcodeWriterPass on [module]\n")
        for n, data in {
            "baseline.bc": before_bc,
            "cse-break.bc": after_bc,
            "baseline.ll": baseline_ir,
            "cse-break.ll": changed_ir,
            "baseline.o": before_obj,
            "cse-break.o": after_obj,
            "pass-manager.log": trace,
        }.items():
            write(out / (prefix + n), data)
        def norm(name):
            return pilot.normalized_ir_sha(out / (prefix + name))
        record = {
            "target": "MACOS_NATIVE_4096_VECTOR_PARITY" if target == "macos"
                      else "IOS_ARM64_OBJECT_BUILD_ONLY",
            "baseline_bitcode_sha256": sha(before_bc),
            "protected_bitcode_sha256": sha(after_bc),
            "baseline_ir_sha256": sha(baseline_ir),
            "protected_ir_sha256": sha(changed_ir),
            "normalized_baseline_ir_sha256": norm("baseline.ll"),
            "normalized_protected_ir_sha256": norm("cse-break.ll"),
            "baseline_object_sha256": sha(before_obj),
            "protected_object_sha256": sha(after_obj),
            "pass_manager_log_sha256": sha(trace),
            "actual_pass_class": pilot.PASS_CLASS,
            "source_canary_abi": "dd_k8_evaluate",
            "real_ir_and_object_delta": True,
            "iphone_executed": False,
        }
        if target == "macos":
            record.update({
                "native_vectors": 4096,
                "native_parity": "PASS",
                "baseline_checksum": "25a3318e3d7d6525",
                "protected_checksum": "25a3318e3d7d6525",
            })
            write(out / "macos-baseline-native.log", log.encode())
            write(out / "macos-cse-break-native.log", log.encode())
        else:
            record.update({
                "native_parity": "NOT_TESTED_ON_IOS_DEVICE",
                "macho": "ARM64_SUBTYPE0_MH_OBJECT",
            })
            for mode in ("baseline", "cse-break"):
                write(out / ("ios-" + mode + "-nm-defined.log"),
                      b"0000000000000000 T _dd_k8_evaluate\n")
                write(out / ("ios-" + mode + "-nm-undefined.log"), b"_strlen\n")
        report["targets"][target] = record
    def save():
        (out / "Kagura-K13-REPORT.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8")
    # Only synthetic fixture SHA can differ from real pinned source, patch
    # test module binding; production K13 pins the actual K12 digest.
    original = verify_k13.REGISTRY_SHA
    verify_k13.REGISTRY_SHA = sha(registry_text)
    report['k12_verified_registry_sha256'] = sha(registry_text)
    try:
        save()
        assert verify_k13.audit(out) == report
        report["targets"]["macos"]["protected_checksum"] = "0" * 16
        save()
        reject(lambda: verify_k13.audit(out), "forged native parity checksum")
        report["targets"]["macos"]["protected_checksum"] = "25a3318e3d7d6525"
        report["targets"]["ios"]["iphone_executed"] = True
        save()
        reject(lambda: verify_k13.audit(out), "forged iPhone PASS")
        report["targets"]["ios"]["iphone_executed"] = False
        report["targets"]["ios"]["baseline_object_sha256"] = "0" * 64
        save()
        reject(lambda: verify_k13.audit(out), "forged object SHA")
        report["targets"]["ios"]["baseline_object_sha256"] = (
            sha((out / "ios-baseline.o").read_bytes()))
        report["crane_production_modified"] = True
        save()
        reject(lambda: verify_k13.audit(out), "forged production integration")
        report["crane_production_modified"] = False
        save()
        assert verify_k13.audit(out) == report
    finally:
        verify_k13.REGISTRY_SHA = original

workflow = (ROOT / ".github/workflows/kagura-k13-cse-break-native.yml").read_text(
    encoding="utf-8")
for required in ("workflow_dispatch:", "runs-on: macos-14",
                 pilot.PIN, pilot.REGISTRY_SHA,
                 "scripts/test_kagura_k13_native.py",
                 "scripts/custom_ollvm/kagura_k13/pilot.py",
                 "scripts/custom_ollvm/kagura_k13/audit.py",
                 "DuoDash-Kagura-K13-CSEBREAK-NATIVE-IOS-ARM64-OBJECT-EXPERIMENTAL",
                 "if: always()"):
    assert required in workflow, required
assert "devicectl" not in workflow
assert "git push" not in workflow
for path in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k13" not in (
        ROOT / path).read_text(encoding="utf-8")
print("KAGURA_K13_PORTABLE_GATES_PASS: pinned FN class, native 4096 canary"
      " log/ABI parity, iOS arm64 subtype0 MH_OBJECT, SHA and no device/Crane.")
