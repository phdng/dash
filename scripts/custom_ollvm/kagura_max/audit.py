#!/usr/bin/env python3
"""Experimental Kagura LLVM19 *real IR* pass evidence, not a security score.

User-reported separate ProtectionLab parity does not constitute Kagura compiler
runtime evidence. This tool only accepts independently built native outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/protection_lab"))
import audit as macho_audit

MARKER = b"DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1"
PROFILE = HERE / "profile.json"
MAGIC = 0xFEEDFACF


def read_profile(path: Path = PROFILE) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    keys = {"schema", "profile", "origin", "upstream_commit", "license",
            "llvm_major", "selector", "pass_pipeline", "stages", "baseline",
            "host_vectors", "targets", "not_enabled", "goals", "claim"}
    if set(data) != keys or data["schema"] != 1 or data["profile"] != "MAX_CANDIDATE":
        raise AssertionError("Unrecognized Kagura experimental manifest")
    if (data["origin"] != "qusamulab/kagura" or
        not re.fullmatch(r"[0-9a-f]{40}", data["upstream_commit"]) or
        data["llvm_major"] != 19 or data["license"] != "MIT"):
        raise AssertionError("Kagura source/LLVM19 pin or license drift")
    if data["selector"] != {
        "translation_unit": "critical.c",
        "symbol": "dd_kagura_critical",
        "critical_only": True,
        "production_allowlist_modified": False,
    }:
        raise AssertionError("Must be isolated single-function fixture only")
    if data["pass_pipeline"] != (
        "kagura-str,function(kagura-fla,kagura-bcf,kagura-sub,kagura-co)"
    ) or data["stages"] != [
        "kagura-str", "kagura-fla", "kagura-bcf", "kagura-sub", "kagura-co"
    ]:
        raise AssertionError("Unreviewed pass or unsafe pass order")
    if data["host_vectors"] != 8192:
        raise AssertionError("Native 8192 vectors mandatory")
    if set(data["targets"]) != {"macos_host", "ios_arm64", "ios_arm64e"}:
        raise AssertionError("arm64e build-only architecture gate missing")
    if data["targets"]["ios_arm64e"] != (
        "Apple Clang Mach-O MH_DYLIB build+strict ABI audit only"
    ):
        raise AssertionError("No LLVM19 arm64e PAC compatibility claim")
    if not set(("kagura-vm", "kagura-pac", "kagura-ci",
                "kagura-anti-debug", "kagura-objc", "kagura-tamper")).issubset(
        data["not_enabled"]
    ):
        raise AssertionError("Runtime-sensitive transforms must stay off")
    return data


def inspect_candidate(plain_object: Path, protected_object: Path,
                      plain_ir: Path, protected_ir: Path) -> dict:
    p = plain_object.read_bytes()
    o = protected_object.read_bytes()
    if p == o or plain_ir.read_bytes() == protected_ir.read_bytes():
        raise AssertionError("No genuine candidate/LLVM IR transformation")
    if MARKER not in p:
        raise AssertionError("Baseline object lacks test-only public marker")
    if MARKER in o:
        raise AssertionError("Kagura candidate still contains public marker")
    return {
        "plain_sha256": hashlib.sha256(p).hexdigest(),
        "protected_sha256": hashlib.sha256(o).hexdigest(),
        "native_byte_difference": True,
        "public_plaintext_absent_candidate": True,
        "compiler_pass_level": "LLVM_IR_OPT_PASS_EXPERIMENTAL",
    }


def verify_host(plain_output: Path, protected_output: Path) -> dict:
    a, b = plain_output.read_bytes(), protected_output.read_bytes()
    if a != b:
        raise AssertionError("LLVM19 Kagura candidate changed native function output")
    lines = a.decode("utf-8", errors="strict").splitlines()
    if len(lines) != 8193 or lines[-1] != "DD_KAGURA_HOST_PASS=8192":
        raise AssertionError("Missing/incorrect 8192 differential host vectors")
    for idx, line in enumerate(lines[:-1]):
        if not re.fullmatch(rf"{idx:04d}:[0-9a-f]{{16}}", line):
            raise AssertionError(f"Invalid host vector line {idx}")
    return {
        "macos_host": "NATIVE_8192_VALUES_EQUAL",
        "native_host_output_sha256": hashlib.sha256(a).hexdigest(),
        "ios_runtime": "NOT_TESTED_BY_CI",
    }


def inspect_ios(plain: Path, protected: Path, apple_arm64e: Path) -> dict:
    ios_plain = macho_audit.inspect(plain, "arm64")
    ios_candidate = macho_audit.inspect(protected, "arm64")
    ios_apple = macho_audit.inspect(apple_arm64e, "arm64e")
    if ios_plain["sha256"] == ios_candidate["sha256"]:
        raise AssertionError("iOS arm64 Kagura candidate unchanged")
    if MARKER not in plain.read_bytes() or MARKER in protected.read_bytes():
        raise AssertionError("iOS arm64 public marker not obfuscated")
    if ios_apple["cpu_subtype_raw"] != "0x80000002":
        raise AssertionError("arm64e versioned PAC ABI must be EXACT")
    return {
        "ios_arm64": "LLVM19_KAGURA_MH_DYLIB_BUILD_ONLY",
        "ios_arm64_plain": ios_plain,
        "ios_arm64_kagura": ios_candidate,
        "ios_arm64e": "APPLE_CLANG_BUILD_ABI_ONLY_NOT_KAGURA_PROTECTED",
        "ios_arm64e_apple_clang": ios_apple,
        "arm64e_a12plus_pac_runtime": "DEFERRED_NO_DEVICE",
    }


def build_report(args: argparse.Namespace) -> dict:
    cfg = read_profile(args.profile)
    candidate = inspect_candidate(
        args.native_plain_object, args.native_protected_object,
        args.native_plain_ir, args.native_protected_ir
    )
    host = verify_host(args.native_plain_log, args.native_protected_log)
    ios = inspect_ios(args.ios_plain, args.ios_protected, args.ios_arm64e)
    result = {
        "schema": 1,
        "profile": cfg["profile"],
        "kagura_upstream_commit": cfg["upstream_commit"],
        "passes_attempted_in_order": cfg["stages"],
        "kagura_experimental_cpp_llvm_passes": True,
        "compiler_native_parity": host,
        "candidate_changes": candidate,
        "target_artifacts": ios,
        "vm_pass_implemented_in_this_pilot": False,
        "ollvm_obfuscator_merged": False,
        "crane_production_changed": False,
        "static_analysis_impossibility_claim": False,
        "security_score": None,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("KAGURA_MAX_CANDIDATE_PASS: LLVM19 native 8192 parity, test marker "
          "absence and iOS arm64/arm64e ABI build-only; NOT production")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", type=Path, default=PROFILE)
    for name in (
        "native-plain-object", "native-protected-object", "native-plain-ir",
        "native-protected-ir", "native-plain-log", "native-protected-log",
        "ios-plain", "ios-protected", "ios-arm64e", "out"
    ):
        p.add_argument("--" + name, type=Path, required=True)
    build_report(p.parse_args())


if __name__ == "__main__":
    main()
