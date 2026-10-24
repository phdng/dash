#!/usr/bin/env python3
"""K18 portable negative gates: synthetic temporary keys are never CI roots."""
from __future__ import annotations
import json
import pathlib
import plistlib
import struct
import sys
import tempfile
import uuid
import zipfile

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "scripts/custom_ollvm/kagura_k18"
sys.path.insert(0, str(HERE))
import package as lab


def reject(fn, reason):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, InvalidSignature):
        return
    raise AssertionError("K18 rejected gate wrongly accepted: " + reason)


def executable(code: bytes) -> bytes:
    seg_len, cmd_len = 72 + 80, 72 + 80 + 24
    offset = 32 + cmd_len
    return (
        struct.pack("<8I", 0xfeedfacf, 0x0100000c, 0, 2, 2, cmd_len, 0, 0)
        + struct.pack("<II16sQQQQIIII", 0x19, seg_len,
                      b"__TEXT" + b"\0" * 10, 0x100000000, 4096,
                      0, offset + len(code), 7, 5, 1, 0)
        + struct.pack("<16s16sQQIIIIIIII",
                      b"__text" + b"\0" * 10, b"__TEXT" + b"\0" * 10,
                      0x100000000 + offset, len(code), offset,
                      4, 0, 0, 0x80000400, 0, 0, 0)
        + struct.pack("<II16s", 0x1b, 24,
                      uuid.UUID("df05a8b7-2aac-4528-b87f-9d76ed37b200").bytes)
        + code
    )


with tempfile.TemporaryDirectory(prefix="K18-SYNTHETIC-ONLY-") as tmp:
    root = pathlib.Path(tmp)
    out = root / "data"
    out.mkdir()
    macbase = executable(b"\x1f\x20\x03\xd5" * 20)
    macprotected = executable(b"\xc0\x03\x5f\xd6" * 20)
    for rel, raw in (
        ("macos-baseline", macbase),
        ("macos-cse-break", macprotected),
        ("KaguraCSEBreakLab.app/KaguraCSEBreakLab", macprotected)
    ):
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    k13 = {
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pass": "kagura-cse-break", "pass_class": "kagura::CSEBreakPass",
        "targets": {"macos": {"native_parity": "PASS", "native_vectors": 4096,
                               "baseline_checksum": "25a3318e3d7d6525",
                               "protected_checksum": "25a3318e3d7d6525"}},
        "security_strength_claim": False,
    }
    k14binary = lab.k16.inspect_macho(macprotected)
    k14 = {"scope": "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB",
           "signing": "UNSIGNED", "app_macho_uuid": k14binary["uuid"],
           "ipa_sha256": "a" * 64, "binary_sha256": k14binary["binary_sha256"]}
    k14ev = {"k13_cse_break_ios_object_embedded": True,
             "ipa_sha256": k14["ipa_sha256"],
             "app_binary_sha256": k14["binary_sha256"],
             "ios_device_execution": "NOT_TESTED_BY_CI", "security_attestation": False}
    for name, obj in (
        ("Kagura-K13-REPORT.json", k13),
        ("Kagura-K14-IPA-report.json", k14),
        ("Kagura-K14-IPA-EVIDENCE.json", k14ev),
    ):
        (out / name).write_text(json.dumps(obj, sort_keys=True) + "\n", encoding="utf-8")
    lab.k16.measure(out)

    key = Ed25519PrivateKey.generate()
    private = root / "synthetic-private.pem"
    public = root / "synthetic-public.pem"
    private.write_bytes(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()))
    public.write_bytes(key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    fingerprint = lab.sha(lab.k17.spki_der(key.public_key()))
    assert fingerprint != lab.KNOWN_EXPOSED_TEST_KEY

    lab.k17.sign(out, private, public, fingerprint)
    reject(lambda: lab.validate_external(out, public, lab.KNOWN_EXPOSED_TEST_KEY),
           "previously exposed test fingerprint")
    reject(lambda: lab.validate_external(out, public, "0" * 64),
           "wrong public anchor")
    assert lab.prepare(out, public, fingerprint)["reference_uuid"] == k14binary["uuid"]
    app = out / (lab.NAME + ".app")
    (app / lab.NAME).write_bytes(executable(b"\x1f\x20\x03\xd5" * 64))
    package = lab.package(out)
    assert package["runtime_self_integrity"] == "NOT_IMPLEMENTED"
    assert package["device_execution"] == "NOT_TESTED_BY_CI"
    assert package["embedded_public_key_is_immutable_trust_anchor"] is False
    assert package["public_spki_sha256"] == fingerprint
    assert package["reference_uuid"] == k14binary["uuid"]
    assert package["reference_sha256"] == lab.sha(macprotected)
    with zipfile.ZipFile(out / lab.IPA) as z:
        assert len(z.infolist()) == len(lab.EXPECTED) == 6
        assert z.testzip() is None
        for name in lab.EXPECTED:
            assert z.read(lab.PREFIX + name) == (app / name).read_bytes()
    reject(lambda: lab.package(out), "existing IPA overwrite")
    reference = app / "KaguraCSEBreakLab.reference"
    original = reference.read_bytes()
    reference.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    reject(lambda: lab.collect(app), "modified reference with original detached signature")
    reference.write_bytes(original)
    sigfile = app / lab.k17.SIGNATURE_FILE
    sig = sigfile.read_bytes()
    sigfile.write_bytes(sig[:-1] + bytes([sig[-1] ^ 1]))
    reject(lambda: lab.collect(app), "tampered Ed25519 signature")
    sigfile.write_bytes(sig)
    trustfile = app / "KaguraK18Trust.plist"
    trust = trustfile.read_bytes()
    payload = plistlib.loads(trust)
    payload["ExpectedSPKISHA256"] = lab.KNOWN_EXPOSED_TEST_KEY
    trustfile.write_bytes(plistlib.dumps(payload))
    reject(lambda: lab.collect(app), "exposed test key accepted")
    trustfile.write_bytes(trust)
    infofile = app / "Info.plist"
    info = infofile.read_bytes()
    infodict = plistlib.loads(info)
    infodict["CFBundleIdentifier"] = "com.duodash.research.kaguracsebreaklab"
    infofile.write_bytes(plistlib.dumps(infodict))
    reject(lambda: lab.collect(app), "K14 namespace collision")
    infofile.write_bytes(info)
    assert lab.collect(app)["reference_sha256"] == lab.sha(macprotected)
    import device_log_audit as device
    approved_log = (
        "DD_K18_SCHEMA=1\n"
        "DD_K18_CONTEXT=IOS_DEVICE_USER_INITIATED\n"
        "DD_K18_SCOPE=BUNDLED_REFERENCE_ONLY\n"
        "DD_K18_ARCH=arm64:0x00000000\n"
        f"DD_K18_REFERENCE_UUID={package['reference_uuid']}\n"
        f"DD_K18_TRUST_SPKI_SHA256={fingerprint}\n"
        "DD_K18_SIGNATURE=PASS\n"
        "DD_K18_REFERENCE_MACHO_TEXT=PASS\n"
        "DD_K18_SELF_INTEGRITY=NOT_IMPLEMENTED\n"
        "DD_K18_COMPLETE=PASS\n"
    )
    device_log = root / "K18-SYNTHETIC-DEVICE-LOG.txt"
    device_log.write_bytes(approved_log.encode("ascii"))
    approved = device.validate(device_log, out / lab.REPORT, fingerprint)
    assert approved["strict_ten_lines_matched"] is True
    assert approved["on_device_execution_cryptographically_attested"] is False
    for why, mutation in (
        ("malformed UUID", approved_log.replace(package['reference_uuid'],
                                                "00000000-0000-0000-0000-000000000000")),
        ("wrong fingerprint", approved_log.replace(fingerprint, "0" * 64)),
        ("false self integrity", approved_log.replace("NOT_IMPLEMENTED", "PASS")),
        ("wrong context", approved_log.replace("IOS_DEVICE_USER_INITIATED",
                                              "IOS_SIMULATOR")),
        ("tampered signature", approved_log.replace("DD_K18_SIGNATURE=PASS",
                                                   "DD_K18_SIGNATURE=FAIL")),
        ("extra line", approved_log + "DD_K18_FAKE=PASS\n"),
        ("missing final newline", approved_log[:-1]),
    ):
        device_log.write_bytes(mutation.encode("ascii"))
        reject(lambda: device.validate(device_log, out / lab.REPORT, fingerprint), why)
    device_log.write_bytes(approved_log.encode("ascii"))
    reject(lambda: device.validate(device_log, out / lab.REPORT, lab.KNOWN_EXPOSED_TEST_KEY),
           "previously leaked test public key")

swift = (HERE / "K18ReferenceLab.swift").read_text(encoding="utf-8")
for must in (
    "import CryptoKit", "Curve25519.Signing.PublicKey",
    "isValidSignature(signature, for: domain + manifest)",
    "KaguraCSEBreakLab", "BUNDLED_REFERENCE_ONLY",
    "DD_K18_REFERENCE_MACHO_TEXT=PASS",
    "DD_K18_SELF_INTEGRITY=NOT_IMPLEMENTED",
    "DD_K18_COMPLETE=PASS", "DD_K18_COMPLETE=FAIL",
    "BLOCKED_K15_WEAK_ALWAYS_PASS_STUB",
    "2e91a1403ffc97eb66c2c1717205eb054ce3c341898b6978b007cb5c56241f40",
    "#if targetEnvironment(simulator)",
    "MACHO_UUID_OR_TEXT_SHA_MISMATCH",
):
    assert must in swift, must
workflow = (ROOT / ".github/workflows/kagura-k18-rotated-reference-ipa.yml").read_text(
    encoding="utf-8")
for must in (
    "workflow_dispatch:", "runs-on: macos-14",
    "K18_ED25519_PRIVATE_KEY_PEM",
    "K18_ED25519_PUBLIC_KEY_PEM",
    "K18_ED25519_PUBLIC_KEY_SPKI_SHA256",
    lab.KNOWN_EXPOSED_TEST_KEY,
    "scripts/test_kagura_k18_reference_lab.py",
    "scripts/custom_ollvm/kagura_k17/signature.py sign",
    "scripts/custom_ollvm/kagura_k18/package.py prepare",
    "scripts/custom_ollvm/kagura_k18/package.py package",
    "xcrun swiftc -parse-as-library",
    "DuoDash-Kagura-K18-ROTATED-ED25519-IOS-REFERENCE-IPA-EXPERIMENTAL",
    "if: always()",
):
    assert must in workflow, must
for bad in ("devicectl device install", "kagura-bbcheck", "codesign -s",
            "git push", "K17_ED25519_PRIVATE_KEY_PEM"):
    assert bad not in workflow
for name in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k18" not in (ROOT / name).read_text(encoding="utf-8")
print("K18_PORTABLE_ROTATED_SIGNATURE_REFERENCE_IPA_PASS:"
      " new signer required, real Ed25519+MachO reference gates,"
      " mutated signature/binary/key/bundle rejected; iPhone CI NOT_TESTED")
