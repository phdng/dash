#!/usr/bin/env python3
"""Independently replay K12 opt-only results from retained artifact files.

A successful 'opt' exit or bitcode binary delta is not native validation.
Validate every claimed LLVM19 IR text hash and classify all candidate
screens as UNVERIFIED. May run on Linux/Windows without Apple LLVM SDK.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path

from inventory import PIN, sha, verify, normalized_ir_sha

STATUS_DELTA = "OPT_EXECUTED_IR_DELTA_UNVERIFIED"
STATUS_NO_DELTA = "OPT_EXECUTED_NO_IR_DELTA_UNVERIFIED"
STATUS_FAILED = "OPT_FAILED_UNVERIFIED"
STATUS_INVALID = "OPT_INVALID_BITCODE_UNVERIFIED"
BITCODE_MAGIC = b"BC\xc0\xde"
BITCODE_WRAPPER_MAGIC = b"\xde\xc0\x17\x0b"
WRAPPER_HEADER_SIZE = 20  # magic, version, bitcode-offset, bitcode-size, cpu-type
TARGET_LABELS = ("macos", "ios-arm64-build-only")


def ensure_file(path: Path, *, expected_sha: str | None = None) -> None:
    if not path.is_file() or path.is_symlink() or path.stat().st_size <= 0:
        raise AssertionError("K12 missing/nonregular/unusable evidence: " + str(path))
    if expected_sha is not None and sha(path) != expected_sha:
        raise AssertionError("K12 SHA mismatch: " + str(path))


def bitcode_container(data: bytes) -> str:
    """Verify raw or LLVM's specified little-endian wrapper container.

    Apple-target clang may produce a legitimate wrapped bitcode file.
    Never accept an arbitrary magic-prefix shim: the wrapper must be
    complete, versioned, in bounds, and point to real raw BC magic.
    LLVM19 llvm-dis has already parsed these files in smoke.py; this
    independent portable check is a structural/serialization gate.
    """
    if len(data) >= 4 and data[:4] == BITCODE_MAGIC:
        return "RAW_LLVM_BITCODE"
    if len(data) >= 4 and data[:4] == BITCODE_WRAPPER_MAGIC:
        if len(data) < WRAPPER_HEADER_SIZE:
            raise AssertionError("K12 truncated LLVM bitcode wrapper header")
        magic, version, offset, size, _cpu = struct.unpack_from(
            "<IIIII", data)
        if magic != 0x0B17C0DE or version != 0:
            raise AssertionError("K12 malformed LLVM bitcode wrapper magic/version")
        if (offset < WRAPPER_HEADER_SIZE or size < 4 or
                offset > len(data) or size > len(data) - offset):
            raise AssertionError("K12 LLVM bitcode wrapper offset/size outside file")
        if data[offset:offset + 4] != BITCODE_MAGIC:
            raise AssertionError("K12 LLVM wrapper points to non-bitcode bytes")
        return "WRAPPED_LLVM_BITCODE"
    raise AssertionError(
        "K12 file is not raw or LLVM-wrapped bitcode, prefix=" +
        data[:4].hex())


def ensure_llvm_bc(path: Path, expected_sha: str) -> str:
    ensure_file(path, expected_sha=expected_sha)
    if not isinstance(expected_sha, str) or not re.fullmatch(
            r"[a-f0-9]{64}", expected_sha):
        raise AssertionError("K12 missing genuine bitcode SHA-256 reference")
    try:
        return bitcode_container(path.read_bytes())
    except AssertionError as e:
        raise AssertionError(str(e) + ": " + str(path)) from e


def audit(out: Path, fixture: Path) -> dict:
    inv = verify(out)
    report_file = out / "Kagura-K12-REMAINING-OPT-SCREEN.json"
    ensure_file(report_file)
    rep = json.loads(report_file.read_text(encoding="utf-8"))
    candidates = inv["remaining_registered_unverified"]
    if (rep.get("schema") != 1 or
            rep.get("scope") !=
            "K12_OPT_DIAGNOSTIC_ONLY_NOT_NATIVE_PASS_VALIDATION" or
            rep.get("pinned_commit") != PIN or
            rep.get("source_inventory_sha256") !=
            sha(out / "Kagura-K12-REMAINING-PASS-INVENTORY.json") or
            not fixture.is_file() or
            rep.get("fixture_sha256") != sha(fixture) or
            rep.get("clang19_ir_disassembly_comparison") is not True or
            rep.get("ir_delta_ignores_llvm_dis_moduleid_comment") is not True or
            rep.get("candidate_count") != len(candidates) or
            not isinstance(rep.get("results"), list) or
            len(rep["results"]) != len(candidates) or
            rep.get("native_parity_proven") is not False or
            rep.get("ios_device_runtime_proven") is not False or
            rep.get("arm64e_pac_proven") is not False or
            rep.get("crane_production_modified") is not False):
        raise AssertionError("K12 opt report provenance/status invalid")
    screened = 0
    for idx, (item, expected) in enumerate(
            zip(rep["results"], candidates), 1):
        if any(item.get(k) != v for k, v in expected.items()):
            raise AssertionError("K12 candidate changed pinned name/kind/flag/coverage")
        stage = out / f"probe-{idx:02d}-{expected['name']}"
        if expected["kind"] == "INFRA":
            if (item.get("screening") != "SKIPPED_INFRA_NOT_AUTO_RUN" or
                    item.get("targets") != {} or
                    item.get("native_parity") != "NOT_TESTED" or
                    item.get("ios_device") != "NOT_TESTED"):
                raise AssertionError("K12 INFRA pass falsely screened or elevated")
            continue
        if expected["kind"] not in ("FN", "MOD"):
            raise AssertionError("K12 unknown kind")
        pipeline = ("function(" + expected["name"] + "),verify"
                    if expected["kind"] == "FN" else
                    expected["name"] + ",verify")
        if (item.get("screening") != "LLVM19_OPT_ONLY_NOT_PASS_VALIDATION" or
                item.get("opt_pipeline") != pipeline or
                item.get("native_parity") != "NOT_TESTED" or
                item.get("ios_device") != "NOT_TESTED" or
                not isinstance(item.get("targets"), dict) or
                set(item["targets"]) != set(TARGET_LABELS)):
            raise AssertionError("K12 pass accepted/elevated without expected stage")
        for label, detail in item["targets"].items():
            bc = out / f"{label}-baseline.bc"
            baseline_ir = out / f"{label}-baseline.ll"
            log = stage / f"{label}-opt.log"
            check = detail.get("screening")
            if (check not in (STATUS_DELTA, STATUS_NO_DELTA,
                              STATUS_FAILED, STATUS_INVALID) or
                    detail.get("native_parity") != "NOT_TESTED" or
                    detail.get("iphone_runtime") != "NOT_TESTED" or
                    detail.get("bitcode_byte_delta_only") not in (True, False)):
                raise AssertionError("K12 candidate native/device status falsely upgraded")
            ensure_llvm_bc(bc, detail.get("input_sha256"))
            ensure_file(baseline_ir, expected_sha=detail.get("input_ir_sha256"))
            if normalized_ir_sha(baseline_ir) != detail.get(
                    "normalized_input_ir_sha256"):
                raise AssertionError("K12 baseline normalized IR hash mismatch")
            text = baseline_ir.read_text(encoding="utf-8")
            if "dd_k8_evaluate(" not in text or (
                    label.startswith("ios") and
                    not re.search(r'target triple = "arm64-apple-ios', text)):
                raise AssertionError("K12 wrong original C LLVM IR target/ABI")
            if not log.is_file() or sha(log) != detail.get("opt_log_sha256"):
                raise AssertionError("K12 opt command log SHA missing/changed")
            output = stage / f"{label}-post-opt.bc"
            after_ir = stage / f"{label}-post-opt.ll"
            dis_log = stage / f"{label}-llvm-dis.log"
            if check == STATUS_FAILED:
                if (detail.get("output_sha256") is not None or
                        detail.get("output_ir_sha256") is not None or
                        detail.get("normalized_output_ir_sha256") is not None or
                        detail.get("llvm_dis_log_sha256") is not None or
                        detail.get("bitcode_byte_delta_only") is not False or
                        output.exists() or after_ir.exists()):
                    raise AssertionError("K12 failed opt recorded unexpected success")
                continue
            ensure_llvm_bc(output, detail.get("output_sha256"))
            if (not dis_log.is_file() or
                    sha(dis_log) != detail.get("llvm_dis_log_sha256")):
                raise AssertionError("K12 missing corrupted llvm-dis status log")
            actual_byte_delta = sha(output) != sha(bc)
            if actual_byte_delta is not detail["bitcode_byte_delta_only"]:
                raise AssertionError("K12 false byte-delta indicator")
            if check == STATUS_INVALID:
                if (detail.get("output_ir_sha256") is not None or
                        detail.get("normalized_output_ir_sha256") is not None or
                        after_ir.exists()):
                    raise AssertionError("K12 invalid llvm-dis has a claimed IR digest")
                continue
            ensure_file(after_ir, expected_sha=detail.get("output_ir_sha256"))
            new_text = after_ir.read_text(encoding="utf-8")
            if "dd_k8_evaluate(" not in new_text:
                raise AssertionError("K12 opt removed canary ABI symbol")
            if normalized_ir_sha(after_ir) != detail.get(
                    "normalized_output_ir_sha256"):
                raise AssertionError("K12 normalized candidate LLVM IR SHA mismatch")
            changed = normalized_ir_sha(after_ir) != normalized_ir_sha(baseline_ir)
            if check != (STATUS_DELTA if changed else STATUS_NO_DELTA):
                raise AssertionError("K12 IR delta claim not reflected by real IR files")
            screened += 1
    print("K12_OPT_DIAGNOSTIC_ARTIFACT_AUDIT_PASS: candidates=" +
          str(len(candidates)) + "; valid IR screens=" + str(screened) +
          "; new native/device pass verified=0")
    return rep


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--fixture", type=Path, default=(
        Path(__file__).resolve().parents[1] / "kagura_k8/fixture.c"))
    a = p.parse_args()
    audit(a.out, a.fixture)


if __name__ == "__main__":
    main()
