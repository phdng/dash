#!/usr/bin/env python3
"""K17 fail-closed portable cryptographic gates with TEMPORARY test-only keys.

A generated fixture key is strictly for local negatives, never a K17 trust
anchor and never usable to claim a real K16 GitHub CI authenticated reference.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = pathlib.Path(__file__).resolve().parents[1]
K17 = ROOT / "scripts/custom_ollvm/kagura_k17"
sys.path.insert(0, str(K17))
import signature as sig


def rejects(fn, message):
    try:
        fn()
    except (AssertionError, ValueError, KeyError):
        return
    raise AssertionError("K17 invalid signature/reference was accepted: " + message)


def synthetic_macho(code: bytes) -> bytes:
    section_len = 80
    segment_len = 72 + section_len
    load_size = segment_len + 24
    text_offset = 32 + load_size
    header = struct.pack("<8I", 0xFEEDFACF, 0x0100000C, 0, 2,
                         2, load_size, 0, 0)
    segment = struct.pack(
        "<II16sQQQQIIII", 0x19, segment_len, b"__TEXT" + b"\0" * 10,
        0x100000000, 4096, 0, text_offset + len(code), 7, 5, 1, 0)
    section = struct.pack(
        "<16s16sQQIIIIIIII", b"__text" + b"\0" * 10, b"__TEXT" + b"\0" * 10,
        0x100000000 + text_offset, len(code), text_offset, 4,
        0, 0, 0x80000400, 0, 0, 0)
    lc_uuid = struct.pack("<II16s", 0x1B, 24,
                          uuid.UUID("7c0cb853-77aa-3ccb-9f20-560e5f40e587").bytes)
    return header + segment + section + lc_uuid + code


with tempfile.TemporaryDirectory(prefix="K17-only-test-keys-") as tmp:
    p = pathlib.Path(tmp)
    data = p / "specimens"
    data.mkdir()
    base = synthetic_macho(b"\x1f\x20\x03\xd5" * 20)
    protected = synthetic_macho(b"\xc0\x03\x5f\xd6" * 20)
    for rel, raw in (
        ("macos-baseline", base), ("macos-cse-break", protected),
        ("KaguraCSEBreakLab.app/KaguraCSEBreakLab", protected),
    ):
        dest = data / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    k13 = {
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pass": "kagura-cse-break", "pass_class": "kagura::CSEBreakPass",
        "targets": {"macos": {
            "native_parity": "PASS", "native_vectors": 4096,
            "baseline_checksum": "25a3318e3d7d6525",
            "protected_checksum": "25a3318e3d7d6525"}},
        "security_strength_claim": False,
    }
    i = sig.k16.inspect_macho(protected)
    k14 = {
        "scope": "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB",
        "signing": "UNSIGNED", "app_macho_uuid": i["uuid"],
        "ipa_sha256": "a" * 64, "binary_sha256": i["binary_sha256"],
    }
    evidence = {
        "k13_cse_break_ios_object_embedded": True,
        "ipa_sha256": k14["ipa_sha256"],
        "app_binary_sha256": k14["binary_sha256"],
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "security_attestation": False,
    }
    def update_json(name, value):
        (data / name).write_text(json.dumps(value, sort_keys=True) + "\n",
                                 encoding="utf-8")
    update_json("Kagura-K13-REPORT.json", k13)
    update_json("Kagura-K14-IPA-report.json", k14)
    update_json("Kagura-K14-IPA-EVIDENCE.json", evidence)
    manifest = sig.k16.measure(data)
    assert manifest["metadata_authenticated"] is False
    assert sig.k16.replay(data) == manifest

    key = Ed25519PrivateKey.generate()
    pub = key.public_key()
    private = p / "TEMP_TEST_PRIVATE.pem"
    trusted = p / "TEMP_TEST_TRUSTED_PUBLIC.pem"
    private.write_bytes(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()))
    trusted.write_bytes(pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    fingerprint = sig.digest(sig.spki_der(pub))

    signed = sig.sign(data, private, trusted, fingerprint)
    assert signed == sig.verified(data, trusted, fingerprint)
    assert signed["k16_offline_manifest_replayed"] is True
    assert signed["trusted_external_ed25519_spki_sha256"] == fingerprint
    assert signed["code_signature_or_device_attestation"] is False
    assert signed["runtime_verifier_implemented"] is False
    assert signed["anti_tamper_strength_proven"] is False
    assert signed["on_device_integrity_proven"] is False
    assert signed["k15_bbcheck_fixed"] is False
    assert signed["per_basic_block_integrity_proven"] is False
    assert signed["arm64e_pac_tested"] is False

    manifest_file = data / sig.k16.MANIFEST
    sig_file = data / sig.SIGNATURE_FILE
    receipt_file = data / sig.RECEIPT_FILE
    raw_manifest = manifest_file.read_bytes()
    raw_sig = sig_file.read_bytes()
    raw_receipt = receipt_file.read_bytes()

    rejects(lambda: sig.sign(data, private, trusted, fingerprint),
            "overwriting prior detached signature")
    bundled = data / "untrusted-bundled-key.pem"
    bundled.write_bytes(trusted.read_bytes())
    rejects(lambda: sig.verified(data, bundled, fingerprint),
            "self-contained artifact public key treated as independent trust")
    rejects(lambda: sig.verified(data, trusted, "0" * 64),
            "untrusted key with false SHA")
    rejects(lambda: sig.verified(data, trusted, "A" * 64),
            "noncanonical uppercase SHA")
    other_key = Ed25519PrivateKey.generate().public_key()
    other_pub = p / "OTHER_TEST_KEY.pem"
    other_pub.write_bytes(other_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    rejects(lambda: sig.verified(data, other_pub, sig.digest(sig.spki_der(other_key))),
            "wrong but self-consistent public trust key")

    fake_signed = copy.deepcopy(signed)
    fake_signed["runtime_verifier_implemented"] = True
    receipt_file.write_text(json.dumps(fake_signed), encoding="utf-8")
    rejects(lambda: sig.verified(data, trusted, fingerprint),
            "promoting offline receipt to runtime PASS")
    receipt_file.write_bytes(raw_receipt)
    sig_file.write_bytes(raw_sig[:-1] + bytes([raw_sig[-1] ^ 1]))
    rejects(lambda: sig.verified(data, trusted, fingerprint),
            "tampered signature")
    sig_file.write_bytes(raw_sig)

    manifest_file.write_bytes(raw_manifest[:-1] + b" ")
    rejects(lambda: sig.verified(data, trusted, fingerprint),
            "tampered raw K16 payload")
    manifest_file.write_bytes(raw_manifest)
    path = data / "macos-cse-break"
    path.write_bytes(protected[:-1] + bytes([protected[-1] ^ 1]))
    rejects(lambda: sig.verified(data, trusted, fingerprint),
            "tampered linked executable with old signature")
    path.write_bytes(protected)
    k13["targets"]["macos"]["baseline_checksum"] = "0" * 16
    update_json("Kagura-K13-REPORT.json", k13)
    rejects(lambda: sig.verified(data, trusted, fingerprint),
            "fake upstream native reference")
    k13["targets"]["macos"]["baseline_checksum"] = "25a3318e3d7d6525"
    update_json("Kagura-K13-REPORT.json", k13)
    assert sig.verified(data, trusted, fingerprint) == signed

    p2 = p / "unsigned-only"
    p2.mkdir()
    for name, obj in (("Kagura-K13-REPORT.json", k13),
                      ("Kagura-K14-IPA-report.json", k14),
                      ("Kagura-K14-IPA-EVIDENCE.json", evidence)):
        (p2 / name).write_bytes((data / name).read_bytes())
    for rel in sig.k16.FILE_NAMES.values():
        dest = p2 / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((data / rel).read_bytes())
    sig.k16.measure(p2)
    rejects(lambda: sig.verified(p2, trusted, fingerprint),
            "unsigned reference treated as authenticated")
    wrong_key = Ed25519PrivateKey.generate()
    wrong_private = p / "WRONG_TEST_PRIVATE.pem"
    wrong_private.write_bytes(wrong_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()))
    rejects(lambda: sig.sign(p2, wrong_private, trusted, fingerprint),
            "wrong signing key accepted")
    assert not (p2 / sig.SIGNATURE_FILE).exists()

    assert not any("PRIVATE KEY" in f.read_text(encoding="utf-8", errors="ignore")
                   for f in (data / sig.RECEIPT_FILE,))
    # This file is never a trusted key source for real CI: generated fixture only.
    assert sig.SCOPE == "K17_EXTERNAL_TRUST_ANCHOR_ED25519_K16_OFFLINE_MANIFEST_ONLY"
    assert sig.DOMAIN.endswith(b"\0")

workflow = (ROOT / ".github/workflows/kagura-k17-external-ed25519.yml").read_text(
    encoding="utf-8")
for token in (
    "workflow_dispatch:", "runs-on: macos-14", "cryptography==50.0.2",
    "K17_ED25519_PRIVATE_KEY_PEM", "K17_ED25519_PUBLIC_KEY_PEM",
    "K17_ED25519_PUBLIC_KEY_SPKI_SHA256",
    "scripts/test_kagura_k17_signature.py",
    "scripts/custom_ollvm/kagura_k16/macho_measure.py",
    "scripts/custom_ollvm/kagura_k17/signature.py",
    "DuoDash-Kagura-K17-EXTERNALLY-TRUSTED-ED25519-OFFLINE-EXPERIMENTAL",
    "if: always()",
):
    assert token in workflow, token
# K17 GitHub Actions accepts public/fingerprint from EITHER repository
# Variable or Secret (common user setup places all three as Secrets).
# Keep the private key Secret-only, fail closed for mismatched sources,
# and never print key material in diagnostics.
for required_source in (
    "secrets.K17_ED25519_PRIVATE_KEY_PEM",
    "vars.K17_ED25519_PUBLIC_KEY_PEM",
    "secrets.K17_ED25519_PUBLIC_KEY_PEM",
    "vars.K17_ED25519_PUBLIC_KEY_SPKI_SHA256",
    "secrets.K17_ED25519_PUBLIC_KEY_SPKI_SHA256",
    "K17_PUBLIC_PEM=\"${K17_PUBLIC_PEM_VAR:-$K17_PUBLIC_PEM_SECRET}\"",
    "K17_FINGERPRINT=\"${K17_FINGERPRINT_VAR:-$K17_FINGERPRINT_SECRET}\"",
    "private/public keys do not form a pair",
    "public SPKI fingerprint does not match",
    "public key differs between repository Variables and Secrets",
    "fingerprint differs between repository Variables and Secrets",
    "K17 external Ed25519 keypair + SHA256 SPKI fingerprint preflight PASS",
):
    assert required_source in workflow, required_source
for banned in ("git push", "codesign -s", "devicectl",
               "kagura-bbcheck", "ptrauth_strip",
               'echo "$K17_PRIVATE_PEM"',
               'echo "$K17_PUBLIC_PEM"',
               'print(os.environ["K17_PRIVATE_PEM"])'):
    assert banned not in workflow, banned
for p in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k17" not in (ROOT / p).read_text(encoding="utf-8")

print("KAGURA_K17_PORTABLE_ED25519_FAILCLOSED_PASS:"
      " independent key fingerprint, detached signature, raw K16 replay,"
      " tamper/forgery/false native security negatives; real CI SIGNING NOT_TESTED")
