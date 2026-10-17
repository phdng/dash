#!/usr/bin/env python3
"""Correlate the K6 actual VM proof with K7 stand-alone iOS arm64 IPA bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from audit import body, checksums, sha
from package_ipa import verify_ipa

def inspect(*, ipa: Path, ipa_report: Path, k6_report: Path,
            ios_plain_ir: Path, ios_vm_ir: Path, ios_vm_trace: Path,
            symbols: Path, ios_vm_obj: Path, ios_plain_obj: Path,
            vm_interpreter_obj: Path, output: Path) -> dict:
    k6 = json.loads(k6_report.read_text(encoding="utf-8"))
    package = json.loads(ipa_report.read_text(encoding="utf-8"))
    packed = verify_ipa(ipa)
    if package != packed:
        raise AssertionError("K7 IPA report differs from embedded IPA bytes")
    if (k6.get("schema") != 1 or k6.get("profile") !=
        "K6_VM_SELECTIVE_EXPERIMENTAL" or
        k6.get("upstream_commit") !=
        "ac2136ee0408677cf7cdee55307e9b16edd5f4d5" or
        k6.get("true_vm_trampoline_observed") is not True or
        k6.get("vm_bytecode_blob_observed") is not True or
        k6.get("native_guard_body_unchanged") is not True or
        k6.get("macos", {}).get("parity_vectors") != 4096 or
        k6.get("macos", {}).get("baseline_parity_checksum") !=
        checksums()[0] or
        k6.get("macos", {}).get("unprotected_guard_checksum") !=
        checksums()[1] or
        k6.get("ios_arm64_build_only", {}).get("device_execution") !=
        "NOT_TESTED" or
        k6.get("security_attestation") is not False or
        k6.get("production_crane_modified") is not False):
        raise AssertionError("Missing exact actual native VM K6 evidence")
    plain = ios_plain_ir.read_text(encoding="utf-8")
    protected = ios_vm_ir.read_text(encoding="utf-8")
    trace = ios_vm_trace.read_text(encoding="utf-8")
    if (body(plain, "dd_vm_guard_plain") !=
        body(protected, "dd_vm_guard_protected") or
        "@kagura_vm_execute" in plain or
        not re.search(r"call\s+i64\s+@kagura_vm_execute\(",
                      body(protected, "dd_vm_protected")) or
        "kagura_vm_bc_" not in protected or
        "kagura_vm_key_" not in protected or
        "kagura_vm_execute" in body(protected, "dd_vm_guard_protected") or
        "Running pass: kagura::VMObfuscationPass on dd_vm_protected" not in trace or
        k6.get("inputs_sha256", {}).get("ios_vm_ir") != sha(ios_vm_ir) or
        k6.get("inputs_sha256", {}).get("ios_vm_trace") != sha(ios_vm_trace)):
        raise AssertionError("K7 VM iOS bytecode/guard/CI hash proof mismatch")
    exports = set(symbols.read_text(encoding="utf-8").splitlines())
    expected = ("_dd_vm_plain", "_dd_vm_protected",
                "_dd_vm_guard_plain", "_dd_vm_guard_protected",
                "_kagura_vm_execute")
    for item in expected:
        if sum(line.endswith(" " + item) for line in exports) != 1:
            raise AssertionError(f"K7 executable missing/duplicated {item}")
    result = {
        "schema": 1,
        "scope": "STANDALONE_K7_VM_TROLLSTORE_IPA",
        "upstream_commit": k6["upstream_commit"],
        "llvm_major": 19,
        "vm_pipeline": "function(kagura-vm)",
        "strict_vm_target": "dd_vm_protected",
        "non_vm_guard": "dd_vm_guard_protected",
        "virtualization_ir_confirmed": True,
        "guard_ir_equal_to_baseline": True,
        "macos_k6_real_vm_parity_verified_from_ci_report": True,
        "macos_k6_native_evidence_sha256": sha(k6_report),
        "ios_vm_pass_trace_sha256": sha(ios_vm_trace),
        "ios_vm_ir_sha256": sha(ios_vm_ir),
        "ios_plain_ir_sha256": sha(ios_plain_ir),
        "ios_plain_object_sha256": sha(ios_plain_obj),
        "ios_vm_object_sha256": sha(ios_vm_obj),
        "ios_vm_interpreter_object_sha256": sha(vm_interpreter_obj),
        "executable_exported_symbols": list(expected),
        "app_macho_uuid": packed["macho_uuid"],
        "app_binary_sha256": packed["binary_sha256"],
        "ipa_sha256": packed["ipa_sha256"],
        "expected_device_parity_checksum": checksums()[0],
        "expected_device_guard_checksum": checksums()[1],
        "actual_ios_device_execution": "NOT_TESTED_BY_CI",
        "app_is_signed": False,
        "crane_production_modified": False,
        "k5_ipa_modified": False,
        "security_attestation": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("K7_REAL_VM_IPA_EVIDENCE_PASS: K6 native VM proof, iOS bytecode, "
          "arm64 executable and embedded IPA exact UUID/SHA; device NOT TESTED")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("ipa", "ipa_report", "k6_report", "ios_plain_ir",
                 "ios_vm_ir", "ios_vm_trace", "symbols", "ios_vm_obj",
                 "ios_plain_obj", "vm_interpreter_obj", "output"):
        p.add_argument("--" + name.replace("_", "-"), required=True, type=Path)
    x = p.parse_args()
    inspect(**vars(x))


if __name__ == "__main__":
    main()
