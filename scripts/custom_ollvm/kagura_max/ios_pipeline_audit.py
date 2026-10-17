#!/usr/bin/env python3
"""Evidence for seven *actual* LLVM19 Kagura passes used in KaguraLab IPA.

Audit per-pass opt -debug-pass-manager traces and two different iOS arm64
Mach-O objects, plus final app LC_UUID and cross-check against IPA ZIP.
Passing means compiler/packaging evidence, not iPhone runtime attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/protection_lab"))
import device_audit
import device_evidence
import package_ipa

MARKER = b"DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1"
PASS_NAMES = (
    ("str", "StringEncryptionPass"),
    ("fla", "ControlFlowFlatteningPass"),
    ("bcf", "BogusControlFlowPass"),
    ("sub", "SubstitutionPass"),
    ("co", "ConstantObfuscationPass"),
    ("bbr", "BasicBlockReorderingPass"),
    ("bbs", "BasicBlockSplittingPass"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_object(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 32:
        raise AssertionError("Incomplete native Kagura Mach-O object")
    magic, cpu, subtype, kind = struct.unpack_from("<IIII", data)
    if (magic != device_audit.MAGIC or
        cpu != device_audit.ARM64_CPUTYPE or subtype != 0 or kind != 1):
        raise AssertionError("Expected real arm64 MH_OBJECT, never host/arm64e")


def audit(*, plain: Path, protected: Path, app: Path, ipa: Path,
          logs: Path, output: Path) -> dict:
    inspect_object(plain)
    inspect_object(protected)
    baseline = plain.read_bytes()
    candidate = protected.read_bytes()
    if baseline == candidate:
        raise AssertionError("Kagura native object identical to baseline")
    if MARKER not in baseline or MARKER in candidate:
        raise AssertionError("Public string marker not removed from protected object")
    if not logs.is_dir():
        raise AssertionError("Kagura pass-manager trace directory missing")
    pass_evidence: list[dict] = []
    for name, llvm_class in PASS_NAMES:
        file = logs / f"pass-{name}.log"
        raw = file.read_bytes()
        if len(raw) < 32 or len(raw) > 512_000:
            raise AssertionError("Empty/oversized Kagura pass execution trace")
        trace = raw.decode("utf-8", errors="strict")
        if "Running pass:" not in trace or llvm_class not in trace:
            raise AssertionError(f"{name}: actual Kagura LLVM pass not observed")
        if name != "str" and "dd_kagura_protected" not in trace:
            raise AssertionError(f"{name}: pass not observed on protected entrypoint")
        pass_evidence.append({
            "pass": name,
            "expected_llvm_pass": llvm_class,
            "debug_trace_sha256": sha(file),
            "pass_manager_invocation_observed": True,
        })
    binary = device_audit.inspect_executable(app, "arm64")
    uuid = device_evidence.macho_uuid(app)
    packed = package_ipa.verify_ipa(ipa)
    if binary["sha256"] != packed["binary_sha256"] or (
        uuid != packed["macho_uuid"]
    ):
        raise AssertionError("Kagura IPA does not contain the audited executable")
    result = {
        "schema": 1,
        "scope": "STANDALONE_KAGURA_LAB_APP_ONLY",
        "architecture": "arm64",
        "plain_symbol": "dd_kagura_plain",
        "protected_symbol": "dd_kagura_protected",
        "passes": pass_evidence,
        "passes_observed_count": 7,
        "plain_object_sha256": sha(plain),
        "protected_object_sha256": sha(protected),
        "plain_marker_present": True,
        "protected_marker_absent": True,
        "app_macho_uuid": uuid,
        "app_sha256": binary["sha256"],
        "ipa_sha256": packed["ipa_sha256"],
        "actual_device_execution": "NOT_TESTED_BY_CI",
        "security_attestation": False,
        "crane_production_modified": False,
        "arm64e_runtime": "DEFERRED_NO_A12_DEVICE",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("KAGURA_IPA_SEVEN_PASS_EVIDENCE_PASS: arm64 dual native objects, "
          "seven opt debug traces, exact IPA LC_UUID/SHA, runtime NOT TESTED")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("plain", "protected", "app", "ipa", "logs", "out"):
        p.add_argument("--" + name, type=Path, required=True)
    x = p.parse_args()
    audit(plain=x.plain, protected=x.protected, app=x.app, ipa=x.ipa,
          logs=x.logs, output=x.out)


if __name__ == "__main__":
    main()
