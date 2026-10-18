#!/usr/bin/env python3
"""Independently replay K13 source, IR, Mach-O and 4096-vector native proof.

No source filename or JSON PASS is itself a compiler/native proof.
No iPhone, PAC or production claims can be derived from this artifact.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from pilot import (PASS, PASS_CLASS, PIPELINE, PIN, REGISTRY_SHA, VECTORS, ROOT,
                   sha, ios_macho, native_macho, validate_trace, validate_native,
                   normalized_ir_sha, validate_registry, LLVM_SYMBOL)


def audit(out: Path) -> dict:
    p = out / "Kagura-K13-REPORT.json"
    if not p.is_file():
        raise AssertionError("K13 real report missing")
    report = json.loads(p.read_text(encoding="utf-8"))
    fixture = ROOT / "scripts/custom_ollvm/kagura_k8/fixture.c"
    runner = ROOT / "scripts/custom_ollvm/kagura_k8/runner.c"
    pin = out / "pinned-registry.def"
    license_file = out / "pinned-LICENSE"
    if any(not f.is_file() or f.stat().st_size == 0 for f in
           (fixture, runner, pin, license_file)):
        raise AssertionError("K13 missing original pinned source/license")
    entry = validate_registry(pin.read_text(encoding="utf-8"))
    if (report.get("schema") != 1 or
            report.get("scope") !=
            "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY" or
            report.get("pinned_commit") != PIN or
            report.get("pinned_registry_sha256") != sha(pin) or
            report.get("k12_verified_registry_sha256") != REGISTRY_SHA or
            sha(pin) != REGISTRY_SHA or
            report.get("upstream_license_sha256") != sha(license_file) or
            report.get("pass") != PASS or
            report.get("pass_kind") != entry["kind"] or
            report.get("pass_enable_flag") != entry["enable_flag"] or
            report.get("pass_class") != PASS_CLASS or
            report.get("pipeline") != PIPELINE or
            report.get("fixture_sha256") != sha(fixture) or
            report.get("runner_sha256") != sha(runner) or
            report.get("llvm_major") != 19 or
            report.get("iphone_runtime_executed") is not False or
            report.get("arm64e_pac_tested") is not False or
            report.get("crane_production_modified") is not False or
            report.get("security_strength_claim") is not False or
            set(report.get("targets", {})) != {"macos", "ios"}):
        raise AssertionError("K13 invalid pinned source/pass/scope/audit fields")

    for target in ("macos", "ios"):
        item = report["targets"][target]
        bc = out / f"{target}-baseline.bc"
        after_bc = out / f"{target}-cse-break.bc"
        before = out / f"{target}-baseline.ll"
        after = out / f"{target}-cse-break.ll"
        obj = out / f"{target}-baseline.o"
        post_obj = out / f"{target}-cse-break.o"
        trace = out / f"{target}-pass-manager.log"
        for path in (bc, after_bc, before, after, obj, post_obj, trace):
            if not path.is_file() or path.stat().st_size < 1:
                raise AssertionError("K13 raw pass/object evidence missing: " + str(path))
        for k, path in {
            "baseline_bitcode_sha256": bc,
            "protected_bitcode_sha256": after_bc,
            "baseline_ir_sha256": before,
            "protected_ir_sha256": after,
            "baseline_object_sha256": obj,
            "protected_object_sha256": post_obj,
            "pass_manager_log_sha256": trace,
        }.items():
            if item.get(k) != sha(path):
                raise AssertionError("K13 file SHA mismatch: " + k)
        if (item.get("normalized_baseline_ir_sha256") != normalized_ir_sha(before) or
                item.get("normalized_protected_ir_sha256") != normalized_ir_sha(after) or
                normalized_ir_sha(before) == normalized_ir_sha(after) or
                sha(obj) == sha(post_obj) or
                not LLVM_SYMBOL.search(before.read_text(encoding="utf-8")) or
                not LLVM_SYMBOL.search(after.read_text(encoding="utf-8")) or
                item.get("source_canary_abi") != "dd_k8_evaluate" or
                item.get("real_ir_and_object_delta") is not True or
                item.get("actual_pass_class") != PASS_CLASS or
                item.get("iphone_executed") is not False):
            raise AssertionError("K13 IR/object/ABI classification invalid")
        validate_trace(trace.read_text(encoding="utf-8"))
        if target == "ios":
            ios_macho(obj.read_bytes())
            ios_macho(post_obj.read_bytes())
            if (item.get("target") != "IOS_ARM64_OBJECT_BUILD_ONLY" or
                    item.get("macho") != "ARM64_SUBTYPE0_MH_OBJECT" or
                    item.get("native_parity") != "NOT_TESTED_ON_IOS_DEVICE"):
                raise AssertionError("K13 iOS arm64 was falsely promoted to device PASS")
            for variant in ("baseline", "cse-break"):
                defined = out / (target + "-" + variant + "-nm-defined.log")
                undefs = out / (target + "-" + variant + "-nm-undefined.log")
                if not defined.is_file() or not undefs.is_file():
                    raise AssertionError("K13 iOS object nm symbol evidence absent")
                if not re.search(
                        r"(?m)^\S+ [Tt] _dd_k8_evaluate$",
                        defined.read_text(encoding="utf-8")):
                    raise AssertionError("K13 iOS symbol not defined by real nlist")
                if any(x.startswith("_kagura_") for x in
                       undefs.read_text(encoding="utf-8").splitlines()):
                    raise AssertionError("K13 iOS source has unresolved Kagura runtime deps")
        else:
            native_macho(obj.read_bytes())
            native_macho(post_obj.read_bytes())
            if (item.get("target") != "MACOS_NATIVE_4096_VECTOR_PARITY" or
                    item.get("native_vectors") != VECTORS or
                    item.get("native_parity") != "PASS"):
                raise AssertionError("K13 macOS native parity claim invalid")
            native_logs = [
                out / (target + "-baseline-native.log"),
                out / (target + "-cse-break-native.log"),
            ]
            if any(not f.is_file() for f in native_logs):
                raise AssertionError("K13 missing real runner transcript")
            checks = [validate_native(f.read_text(encoding="utf-8"))
                      for f in native_logs]
            if checks[0] != checks[1] or (
                    checks[0] != item.get("baseline_checksum") or
                    checks[1] != item.get("protected_checksum")):
                raise AssertionError("K13 4096-vector original/protected checksum mismatch")
    print("K13_ARTIFACT_REPLAY_PASS: pinned CSEBreakPass actual"
          " normalized LLVM IR & Mach-O object deltas, native 4096"
          " parity, iOS arm64 OBJECT ONLY, no iPhone/PAC/Crane proof")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    audit(p.parse_args().out)


if __name__ == "__main__":
    main()
