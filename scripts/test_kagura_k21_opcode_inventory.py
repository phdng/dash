#!/usr/bin/env python3
"""Portable K21 bit-pattern classification and K20-chain replay negative gates."""
from __future__ import annotations

import copy
import json
import pathlib
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k21"))
import test_kagura_k20_function_starts as fixtures  # K20 gates also execute
import opcode_inventory as k21


def rejects(fn, label: str) -> None:
    try:
        fn()
    except (AssertionError, KeyError, ValueError, struct.error):
        return
    raise AssertionError("K21 unexpectedly accepted " + label)


known = {
    "bl_imm": 0x94000000,
    "b_imm": 0x14000000,
    "b_cond": 0x54000000,
    "cbz_cbnz": 0x34000000,
    "tbz_tbnz": 0x36000000,
    "ret_reg": 0xD65F03C0,
    "br_reg": 0xD61F0000,
    "blr_reg": 0xD63F0000,
    "nop": 0xD503201F,
    "other": 0x00000000,
}
for kind, word in known.items():
    assert k21.word_kind(word) == kind, (kind, word)
assert k21.word_kind(0xB5000020) == "cbz_cbnz"
assert k21.word_kind(0xB7000020) == "tbz_tbnz"
assert k21.word_kind(0xD65F0020) == "ret_reg"
rejects(lambda: k21.word_kind(-1), "negative word")
rejects(lambda: k21.word_kind(1 << 32), "overflow word")
rejects(lambda: k21.inventory(b""), "zero bytes")
rejects(lambda: k21.inventory(b"abc"), "unaligned bytes")
rejects(lambda: k21.inventory("fake"), "non-bytes")
raw = b"".join(struct.pack("<I", x) for x in known.values())
hist = k21.inventory(raw)
assert hist["word_count"] == len(known)
assert all(hist["opcode_word_pattern_counts"][name] == 1 for name in known)
assert hist["validated_instructions_or_cfg"] is False

with tempfile.TemporaryDirectory(prefix="K21-synthetic-offline-only-") as tmp:
    out = pathlib.Path(tmp)
    for name, data in (
        ("macos-baseline", fixtures.baseline),
        ("macos-cse-break", fixtures.protected),
        ("KaguraCSEBreakLab.app/KaguraCSEBreakLab", fixtures.ios),
    ):
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    ios_meta = k21.k20.k19.k16.inspect_macho(fixtures.ios)
    k13 = {
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pass": "kagura-cse-break", "pass_class": "kagura::CSEBreakPass",
        "targets": {"macos": {"native_parity": "PASS", "native_vectors": 4096,
                              "baseline_checksum": "25a3318e3d7d6525",
                              "protected_checksum": "25a3318e3d7d6525"}},
        "security_strength_claim": False,
    }
    k14 = {
        "scope": "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB",
        "signing": "UNSIGNED", "app_macho_uuid": ios_meta["uuid"],
        "ipa_sha256": "a" * 64,
        "binary_sha256": ios_meta["binary_sha256"],
    }
    evidence = {
        "k13_cse_break_ios_object_embedded": True,
        "ipa_sha256": k14["ipa_sha256"],
        "app_binary_sha256": ios_meta["binary_sha256"],
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "security_attestation": False,
    }
    for name, payload in (
        ("Kagura-K13-REPORT.json", k13),
        ("Kagura-K14-IPA-report.json", k14),
        ("Kagura-K14-IPA-EVIDENCE.json", evidence),
    ):
        (out / name).write_text(json.dumps(payload, sort_keys=True) + "\n",
                                encoding="utf-8")

    k21.k20.k19.k16.measure(out)
    k21.k20.k19.record(out)
    k21.k20.record(out)
    saved = k21.record(out)
    assert saved["source_authenticated"] is False
    assert saved["cfg_or_precise_function_extent_proven"] is False
    assert saved["macos_baseline_vs_csebreak_raw_code_different"] is True
    assert set(saved["specimens"]) == set(k21.k20.k19.INPUTS)
    assert saved["specimens"]["macos_baseline"]["targets"][
        "_dd_k8_evaluate"]["opcode_word_pattern_counts"]["nop"] == 8
    assert saved["specimens"]["macos_csebreak"]["targets"][
        "_dd_k8_evaluate"]["opcode_word_pattern_counts"]["ret_reg"] == 8
    assert k21.verify(out) == saved
    rejects(lambda: k21.record(out), "overwrite report")
    p = out / k21.NAME
    original = p.read_bytes()
    fake = copy.deepcopy(saved)
    fake["runtime_integrity_verifier"] = True
    p.write_text(json.dumps(fake), encoding="utf-8")
    rejects(lambda: k21.verify(out), "forged runtime verifier")
    fake = copy.deepcopy(saved)
    fake["specimens"]["ios_csebreak_lab"]["targets"][
        "_dd_k14_ios_parity"]["opcode_word_pattern_counts"]["other"] = 999
    p.write_text(json.dumps(fake), encoding="utf-8")
    rejects(lambda: k21.verify(out), "forged opcode histogram")
    p.write_bytes(original)
    source = out / "macos-cse-break"
    binary = source.read_bytes()
    source.write_bytes(binary[:280] + bytes([binary[280] ^ 1]) + binary[281:])
    rejects(lambda: k21.verify(out), "modified Mach-O raw bytes")
    source.write_bytes(binary)
    assert k21.verify(out) == saved
    k20report = out / k21.k20.NAME
    k20raw = k20report.read_bytes()
    k20report.write_bytes(k20raw + b" ")
    rejects(lambda: k21.verify(out), "changed K20 source manifest")
    k20report.write_bytes(k20raw)
    assert k21.verify(out) == saved

workflow = (ROOT / ".github/workflows/kagura-k21-static-opcodes.yml").read_text(
    encoding="utf-8")
for needle in ("workflow_dispatch:", "runs-on: macos-14",
               "scripts/test_kagura_k21_opcode_inventory.py",
               "scripts/custom_ollvm/kagura_k20/function_starts.py",
               "scripts/custom_ollvm/kagura_k21/opcode_inventory.py",
               "DuoDash-Kagura-K21-STATIC-OPCODE-INVENTORY-OFFLINE-EXPERIMENTAL",
               "if: always()"):
    assert needle in workflow, needle
for forbidden in ("kagura_k18/", "K18_ED25519_PRIVATE_KEY_PEM",
                  "kagura-bbcheck", "devicectl", "codesign -s", "git push"):
    assert forbidden not in workflow, forbidden

print("K21_STATIC_AARCH64_OPCODE_WORD_INVENTORY_PORTABLE_PASS:"
      " 10 categories, source replay, forged report, changed Mach-O,"
      " K18 skipped; real macOS K21 NOT_TESTED")
