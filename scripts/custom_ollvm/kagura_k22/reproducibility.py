#!/usr/bin/env python3
"""K22 OFFLINE reproducibility of K21 code intervals across two builds.

Always replays both genuine K21->K20->K19->K16/K13/K14 sources.
Matching code interval hashes do NOT prove independent CI execution,
reproducible whole binaries, anti-tamper, CFG, runtime security, or PAC.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kagura_k21"))
import opcode_inventory as k21  # noqa: E402

NAME = "Kagura-K22-REPRODUCIBILITY.json"
SCOPE = "K22_TWO_BUILD_STATIC_CODE_INTERVAL_REPRODUCIBILITY_NO_RUNTIME_TRUST"
EXPECTED_COUNT = 4


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def regenerate(left: Path, right: Path) -> dict:
    if not left.is_dir() or not right.is_dir() or left.resolve() == right.resolve():
        raise AssertionError("K22 requires two distinct existing build directories")
    # Fail closed on each original, including unsigned K13 native / K14 IPA
    # and raw K16/K19/K20/K21 source byte replays.
    a = k21.verify(left)
    b = k21.verify(right)
    fingerprint_a = sha((left / k21.NAME).read_bytes())
    fingerprint_b = sha((right / k21.NAME).read_bytes())
    if a["scope"] != k21.SCOPE or b["scope"] != k21.SCOPE:
        raise AssertionError("K22 unexpected upstream K21 study scope")
    expected = set(k21.k20.k19.INPUTS)
    if set(a["specimens"]) != expected or set(b["specimens"]) != expected:
        raise AssertionError("K22 missing or extra K21 target specimens")
    matches = {}
    for key, (_, expected_symbols) in k21.k20.k19.INPUTS.items():
        al = a["specimens"][key]
        bl = b["specimens"][key]
        ar = al["targets"]
        br = bl["targets"]
        if set(ar) != set(expected_symbols) or set(br) != set(expected_symbols):
            raise AssertionError("K22 missing/extra ABI symbol on " + key)
        checked = {}
        for symbol in expected_symbols:
            x = ar[symbol]
            y = br[symbol]
            required_equal = ("size", "word_count", "bytes_sha256",
                              "first_word_le_hex", "last_word_le_hex",
                              "opcode_word_pattern_counts")
            if any(x[field] != y[field] for field in required_equal):
                raise AssertionError(
                    "K22 target linked code not reproducible: " + key + "/" + symbol)
            if (x["validated_instructions_or_cfg"] is not False or
                y["validated_instructions_or_cfg"] is not False or
                x["true_function_size_proven"] is not False or
                y["true_function_size_proven"] is not False):
                raise AssertionError("K22 illegal CFG/function length claims")
            checked[symbol] = {
                "byte_count": x["size"],
                "word_count": x["word_count"],
                "code_sha256": x["bytes_sha256"],
                "pattern_histogram": x["opcode_word_pattern_counts"],
                "source_a_binary_sha256": al["binary_sha256"],
                "source_b_binary_sha256": bl["binary_sha256"],
                "source_a_macho_uuid": al["macho_uuid"],
                "source_b_macho_uuid": bl["macho_uuid"],
                "whole_executable_sha256_same": (
                    al["binary_sha256"] == bl["binary_sha256"]),
                "macho_uuid_same": al["macho_uuid"] == bl["macho_uuid"],
                "matched_instruction_word_patterns_not_cfg": True,
            }
        matches[key] = checked
    if sum(map(len, matches.values())) != EXPECTED_COUNT:
        raise AssertionError("K22 wrong number of target code intervals")
    return {
        "schema": 1,
        "scope": SCOPE,
        "source_a_k21_manifest_sha256": fingerprint_a,
        "source_b_k21_manifest_sha256": fingerprint_b,
        "tested_code_intervals": EXPECTED_COUNT,
        "code_intervals_reproducible": True,
        "k18_dependency": "NONE_SKIPPED_BY_USER_NOT_TESTED",
        "authenticated_distinct_ci_runs": False,
        "unsigned_metadata_is_trust_anchor": False,
        "whole_macho_identical_required": False,
        "full_disassembly_or_cfg_proven": False,
        "runtime_integrity_verifier": False,
        "iphone_device_execution": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "targets": matches,
    }


def record(left: Path, right: Path, out: Path) -> dict:
    target = out / NAME
    if target.exists() or target.is_symlink():
        raise AssertionError("K22 refuses to overwrite existing result")
    report = regenerate(left, right)
    out.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8")
    return report


def verify(left: Path, right: Path, out: Path) -> dict:
    target = out / NAME
    if not target.is_file() or target.is_symlink() or target.stat().st_size > 512000:
        raise AssertionError("K22 record missing/malformed")
    saved = json.loads(target.read_text(encoding="utf-8"))
    current = regenerate(left, right)
    if type(saved) is not dict or saved != current:
        raise AssertionError("K22 K21 source-grounded two-build replay mismatch")
    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify(args.left, args.right, args.out)
        print("K22_TWO_BUILD_CODE_INTERVAL_REPLAY_PASS: no device/anti-tamper")
    else:
        record(args.left, args.right, args.out)
        print("K22_TWO_BUILD_CODE_INTERVAL_RECORDED: macOS CI NOT_TESTED")


if __name__ == "__main__":
    main()
