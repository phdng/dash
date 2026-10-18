#!/usr/bin/env python3
"""K16 offline Mach-O post-link measurement gates; synthetic tests != CI proof."""
from __future__ import annotations
import copy
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "scripts/custom_ollvm/kagura_k16"
sys.path.insert(0, str(HERE))
import macho_measure as k16


def reject(fn, why):
    try:
        fn()
    except (AssertionError, ValueError, UnicodeError, struct.error):
        return
    raise AssertionError("K16 fail-closed negative accepted: " + why)


def synthetic_macho(code: bytes, *, filetype=2, cpu=0x0100000C,
                    subtype=0, secname=b"__text", sectseg=b"__TEXT",
                    offset_delta=0, nsect=1, uuid_bytes=None):
    if uuid_bytes is None:
        uuid_bytes = uuid.UUID("7c0cb853-77aa-3ccb-9f20-560e5f40e587").bytes
    count = nsect
    seg_size = 72 + 80 * nsect
    cmd_size = seg_size + 24
    text_off = 32 + cmd_size + offset_delta
    if text_off < 0:
        raise AssertionError("bad fixture offset")
    full_length = 32 + cmd_size + len(code)
    header = struct.pack("<8I", 0xFEEDFACF, cpu, subtype, filetype,
                         2, cmd_size, 0, 0)
    segments = struct.pack(
        "<II16sQQQQIIII", 0x19, seg_size,
        b"__TEXT".ljust(16, b"\0"), 0x100000000, 4096,
        0, full_length, 7, 5, count, 0)
    for i in range(nsect):
        segments += struct.pack(
            "<16s16sQQIIIIIIII", secname.ljust(16, b"\0"),
            sectseg.ljust(16, b"\0"), 0x100000000 + 32 + cmd_size,
            len(code), text_off, 4, 0, 0, 0x80000400, 0, 0, 0)
    uuids = struct.pack("<II16s", 0x1B, 24, uuid_bytes)
    blob = header + segments + uuids + code
    assert len(blob) == full_length
    return blob


base = synthetic_macho(b"\x1f\x20\x03\xd5" * 20)
changed = synthetic_macho(b"\x1f\x20\x03\xd5" * 10 + b"\xc0\x03\x5f\xd6" * 10)
assert k16.inspect_macho(base)["text_size"] == 80
assert k16.inspect_macho(changed)["text_sha256"] != k16.inspect_macho(base)["text_sha256"]
assert k16.inspect_macho(base)["uuid"] == "7c0cb853-77aa-3ccb-9f20-560e5f40e587"
reject(lambda: k16.inspect_macho(synthetic_macho(base[-80:], subtype=2)),
       "arm64e subtype accepted")
reject(lambda: k16.inspect_macho(synthetic_macho(base[-80:], filetype=1)),
       "MH_OBJECT passed as MH_EXECUTE")
reject(lambda: k16.inspect_macho(synthetic_macho(base[-80:], cpu=7)),
       "x86 disguised arm64")
reject(lambda: k16.inspect_macho(synthetic_macho(base[-80:], secname=b"__data")),
       "non-code section misnamed")
reject(lambda: k16.inspect_macho(synthetic_macho(base[-80:], sectseg=b"__DATA")),
       "fake text in DATA segment")
reject(lambda: k16.inspect_macho(synthetic_macho(base[-80:], nsect=2)),
       "duplicate text sections")
reject(lambda: k16.inspect_macho(synthetic_macho(base[-80:], offset_delta=99999)),
       "out-of-bounds text section")
reject(lambda: k16.inspect_macho(base[:-20]), "truncated executable")
reject(lambda: k16.inspect_macho(b"BC\xc0\xde" + base), "bitcode mistaken for Mach-O")
reject(lambda: k16.inspect_macho(base[:32]), "header-only fake")

with tempfile.TemporaryDirectory(prefix="K16-synthetic-text-") as tmp:
    p = pathlib.Path(tmp)
    for name, data in (
        ("macos-baseline", base),
        ("macos-cse-break", changed),
        ("KaguraCSEBreakLab.app/KaguraCSEBreakLab", changed),
    ):
        f = p / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    k13 = {
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pass": "kagura-cse-break",
        "pass_class": "kagura::CSEBreakPass",
        "targets": {"macos": {"native_parity": "PASS",
                              "native_vectors": 4096,
                              "baseline_checksum": "25a3318e3d7d6525",
                              "protected_checksum": "25a3318e3d7d6525"}},
        "security_strength_claim": False,
    }
    i = k16.inspect_macho(changed)
    k14 = {"scope": "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB",
           "signing": "UNSIGNED", "app_macho_uuid": i["uuid"],
           "ipa_sha256": "a" * 64, "binary_sha256": i["binary_sha256"]}
    ev = {"k13_cse_break_ios_object_embedded": True,
          "ipa_sha256": k14["ipa_sha256"],
          "app_binary_sha256": k14["binary_sha256"],
          "ios_device_execution": "NOT_TESTED_BY_CI",
          "security_attestation": False}
    def save():
        for name, obj in (
            ("Kagura-K13-REPORT.json", k13),
            ("Kagura-K14-IPA-report.json", k14),
            ("Kagura-K14-IPA-EVIDENCE.json", ev),
        ):
            (p / name).write_text(json.dumps(obj), encoding="utf-8")
    save()
    original = k16.measure(p)
    assert k16.replay(p) == original
    assert all(v["text_size"] == 80 for v in original["linked_binaries"].values())
    assert original["runtime_verifier_implemented"] is False
    assert original["per_basic_block_identity_and_hashing"] is False
    assert original["metadata_authenticated"] is False
    assert original["adversarial_tamper_protection_proven"] is False
    assert original["bbcheck_security_integrity"] == "BLOCKED_K15_WEAK_ALWAYS_PASS_STUB"

    manifest = p / k16.MANIFEST
    initial_bytes = manifest.read_bytes()
    malformed = copy.deepcopy(original)
    malformed["adversarial_tamper_protection_proven"] = True
    manifest.write_text(json.dumps(malformed), encoding="utf-8")
    reject(lambda: k16.replay(p), "false security PASS")
    manifest.write_bytes(initial_bytes)
    malformed = copy.deepcopy(original)
    malformed["linked_binaries"]["macos_baseline"]["text_sha256"] = "0" * 64
    manifest.write_text(json.dumps(malformed), encoding="utf-8")
    reject(lambda: k16.replay(p), "forged text SHA")
    manifest.write_bytes(initial_bytes)
    path = p / "macos-cse-break"
    path.write_bytes(changed[:-1] + bytes([changed[-1] ^ 1]))
    reject(lambda: k16.replay(p), "genuine text mutation missed")
    path.write_bytes(changed)
    k13["targets"]["macos"]["native_parity"] = "NOT_TESTED"
    save()
    reject(lambda: k16.replay(p), "native K13 baseline failed but K16 green")
    k13["targets"]["macos"]["native_parity"] = "PASS"
    save()
    assert k16.replay(p) == original

workflow = (ROOT / ".github/workflows/kagura-k16-offline-macho-text.yml").read_text(
    encoding="utf-8")
for required in (
    "workflow_dispatch:", "runs-on: macos-14",
    "scripts/test_kagura_k16_offline_text.py",
    "scripts/custom_ollvm/kagura_k13/pilot.py",
    "scripts/custom_ollvm/kagura_k13/audit.py",
    "scripts/custom_ollvm/kagura_k14/build_ipa.sh",
    "scripts/custom_ollvm/kagura_k16/macho_measure.py",
    "DuoDash-Kagura-K16-OFFLINE-MACHO-TEXT-FEASIBILITY-EXPERIMENTAL",
    "if: always()",
):
    assert required in workflow, required
for forbidden in (
    "kagura_k15/pilot.py", "kagura-bbcheck", "ios device install",
    "devicectl", "codesign -s", "git push",
):
    assert forbidden not in workflow, forbidden
for path in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k16" not in (ROOT / path).read_text(encoding="utf-8")
print("KAGURA_K16_OFFLINE_TEXT_PORTABLE_PASS: __TEXT,__text SHA detects"
      " changed post-link code, unsigned manifest rejected when altered,"
      " BBCheck runtime execution/security/device not claimed")
