#!/usr/bin/env python3
"""K21 OFFLINE AArch64 fixed-width word inventory on K20-correlated ranges.

This is a limited BIT-PATTERN inventory, not a disassembler, CFG analysis,
verified function extent, trust anchor, anti-tamper feature, or runtime probe.
K20 itself verifies the original K19/K16/K13/K14 sources before K21 runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kagura_k20"))
import function_starts as k20  # noqa: E402

NAME = "Kagura-K21-STATIC-OPCODE-INVENTORY.json"
SCOPE = "K21_OFFLINE_ARM64_WORD_PATTERN_COUNTS_NO_CFG_FUNCTION_SECURITY_OR_DEVICE"
MAX_INTERVAL_BYTES = 8 * 1024 * 1024
KINDS = ("bl_imm", "b_imm", "b_cond", "cbz_cbnz", "tbz_tbnz",
         "ret_reg", "br_reg", "blr_reg", "nop", "other")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def word_kind(word: int) -> str:
    """Recognize only explicit encoding bit-patterns; 'other' is NOT invalid."""
    if type(word) is not int or word < 0 or word > 0xFFFFFFFF:
        raise AssertionError("K21 invalid unsigned instruction word")
    if word & 0xFC000000 == 0x94000000:
        return "bl_imm"
    if word & 0xFC000000 == 0x14000000:
        return "b_imm"
    if word & 0xFF000010 == 0x54000000:
        return "b_cond"
    if word & 0x7E000000 == 0x34000000:
        return "cbz_cbnz"
    if word & 0x7E000000 == 0x36000000:
        return "tbz_tbnz"
    if word & 0xFFFFFC1F == 0xD65F0000:
        return "ret_reg"
    if word & 0xFFFFFC1F == 0xD61F0000:
        return "br_reg"
    if word & 0xFFFFFC1F == 0xD63F0000:
        return "blr_reg"
    if word == 0xD503201F:
        return "nop"
    return "other"


def inventory(raw: bytes) -> dict:
    """Inventory aligned LE words without guessing executable control flow."""
    if type(raw) is not bytes or not (4 <= len(raw) <= MAX_INTERVAL_BYTES) or len(raw) % 4:
        raise AssertionError("K21 requires bounded 4-byte aligned code interval")
    histogram = {kind: 0 for kind in KINDS}
    for (word,) in struct.iter_unpack("<I", raw):
        histogram[word_kind(word)] += 1
    count = len(raw) // 4
    if sum(histogram.values()) != count:
        raise AssertionError("K21 word inventory is not exhaustive")
    return {
        "size": len(raw),
        "word_count": count,
        "bytes_sha256": sha(raw),
        "first_word_le_hex": f"{struct.unpack_from('<I', raw)[0]:08x}",
        "last_word_le_hex": f"{struct.unpack_from('<I', raw, len(raw) - 4)[0]:08x}",
        "opcode_word_pattern_counts": histogram,
        "validated_instructions_or_cfg": False,
        "true_function_size_proven": False,
    }


def regenerate(out: Path) -> dict:
    # Verify entire K20 replay -> K19 -> K16 -> actual linked K13/K14.
    validated = k20.verify(out)
    raw20 = (out / k20.NAME).read_bytes()
    records = {}
    for key, (relpath, expected_symbols) in k20.k19.INPUTS.items():
        p = out / relpath
        if not p.is_file() or p.is_symlink():
            raise AssertionError("K21 required linked Mach-O missing or symlinked")
        data = p.read_bytes()
        saved = validated["specimens"][key]
        if sha(data) != saved["binary_sha256"]:
            raise AssertionError("K21 Mach-O digest not bound to K20")
        ranges = saved["symbol_intervals_corroborated"]
        if set(ranges) != set(expected_symbols):
            raise AssertionError("K21 missing/unexpected ABI interval")
        targets = {}
        for symbol in expected_symbols:
            region = ranges[symbol]
            off = region["file_offset"]
            size = region["length"]
            # Bounded arithmetic, no guessed file offsets/section lengths.
            if (type(off) is not int or type(size) is not int or off < 0 or
                    size < 4 or size > MAX_INTERVAL_BYTES or
                    off % 4 or size % 4 or off > len(data) - size):
                raise AssertionError("K21 target region invalid: " + symbol)
            sliced = data[off:off + size]
            if sha(sliced) != region["sha256"]:
                raise AssertionError("K21 K20 range digest not bound to source: " + symbol)
            measured = inventory(sliced)
            measured["symbol"] = symbol
            measured["file_offset"] = off
            measured["start_vmaddr"] = region["start_vmaddr"]
            measured["next_symbol_vmaddr_exclusive"] = region[
                "next_symbol_vmaddr_exclusive"]
            targets[symbol] = measured
        records[key] = {
            "macho_uuid": saved["macho_uuid"],
            "binary_sha256": saved["binary_sha256"],
            "targets": targets,
        }
    before = records["macos_baseline"]["targets"]["_dd_k8_evaluate"]
    after = records["macos_csebreak"]["targets"]["_dd_k8_evaluate"]
    if before["bytes_sha256"] == after["bytes_sha256"]:
        raise AssertionError("K21 required K13 protected code difference missing")
    return {
        "schema": 1,
        "scope": SCOPE,
        "source_k20_manifest_sha256": sha(raw20),
        "k18_dependency": "NONE_SKIPPED_BY_USER_NOT_TESTED",
        "source_authenticated": False,
        "word_patterns_are_full_disassembly": False,
        "cfg_or_precise_function_extent_proven": False,
        "per_basic_block_identity_proven": False,
        "runtime_integrity_verifier": False,
        "iphone_device_execution": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "macos_baseline_vs_csebreak_raw_code_different": True,
        "specimens": records,
    }


def record(out: Path) -> dict:
    target = out / NAME
    if target.exists() or target.is_symlink():
        raise AssertionError("K21 refuses to overwrite recorded result")
    measured = regenerate(out)
    target.write_text(json.dumps(measured, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8")
    return measured


def verify(out: Path) -> dict:
    target = out / NAME
    if not target.is_file() or target.is_symlink() or target.stat().st_size > 512000:
        raise AssertionError("K21 recorded result missing, symlinked or too large")
    recorded = json.loads(target.read_text(encoding="utf-8"))
    expected = regenerate(out)
    if type(recorded) is not dict or recorded != expected:
        raise AssertionError("K21 source-grounded opcode word replay mismatch")
    return recorded


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify(args.out)
        print("K21_AARCH64_STATIC_OPCODE_WORD_INVENTORY_REPLAY_PASS: no CFG/device/security")
    else:
        record(args.out)
        print("K21_STATIC_OPCODE_INVENTORY_CREATED: macOS K21 CI NOT_TESTED")


if __name__ == "__main__":
    main()
