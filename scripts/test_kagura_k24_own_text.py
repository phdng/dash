#!/usr/bin/env python3
"""K24 standalone own executable text + externally signed reference gates.

All Mach-O and app executions in this Python test are SYNTHETIC fixtures.
Swift compilation and physical iPhone measurement are NOT tested here.
"""
from __future__ import annotations

import base64
import hashlib
import json
import pathlib
import plistlib
import sys
import tempfile
import zipfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k24"))
import test_kagura_k22_reproducibility as fixtures
import package as k24
import external_sign as signer
import device_log_audit as device
import key_preflight as preflight


def rejects(fn, what: str) -> None:
    try:
        fn()
    except (AssertionError, ValueError, KeyError, OSError, RuntimeError):
        return
    raise AssertionError("K24 accepted " + what)


with tempfile.TemporaryDirectory(prefix="K24-EXTERNAL-KEY-ONLY-") as tmp:
    root = pathlib.Path(tmp)
    artifact = root / "artifact"
    artifact.mkdir()
    private = ed25519.Ed25519PrivateKey.generate()
    pub = private.public_key()
    raw_pub = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw)
    der = pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    fingerprint = hashlib.sha256(der).hexdigest()
    trusted = root / "trusted.pem"
    secret = root / "private.pem"
    trusted.write_bytes(pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    secret.write_bytes(private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()))
    pub64 = base64.b64encode(raw_pub).decode("ascii")
    assert preflight.validate("false", "", "") .startswith("K24_MODE_A_")
    assert preflight.validate("false", pub64, "").startswith("K24_MODE_A_")
    assert preflight.validate("true", pub64, fingerprint).startswith("K24_MODE_B_")
    for args in (("true", "", fingerprint), ("true", pub64, ""),
                 ("true", pub64, "0" * 64), ("true", "!" * 44, fingerprint),
                 ("false", pub64, fingerprint), ("maybe", pub64, fingerprint),
                 ("true", pub64, fingerprint.upper())):
        rejects(lambda args=args: preflight.validate(*args),
                "invalid manually requested public key / fingerprint")
    k24.prepare(artifact, pub64)
    rejects(lambda: k24.prepare(artifact, pub64), "overwritten app")
    assert "keyConfigured = true" in (artifact / k24.EXPECTED_SWIFT).read_text()
    (artifact / (k24.APP + ".app") / k24.APP).write_bytes(
        fixtures.fixtures.baseline)
    report = k24.package(artifact)
    assert report["public_key_pinned_into_compiled_app"] is True
    assert report["external_signature_created_by_ci"] is False
    assert report["device_runtime_text_matches_file"] == "NOT_TESTED"
    assert report["anti_tamper_proven"] is False
    assert report["runtime_self_integrity_security_proven"] is False
    assert report["crane_production_modified"] is False
    assert report["k15_bbcheck_dependency"] is False
    assert report["k18_dependency"] is False
    assert report["signing"] == "UNSIGNED"
    assert k24.collect(artifact)[0]["self_text_sha256"] == report["self_text_sha256"]
    with zipfile.ZipFile(artifact / k24.IPA) as z:
        assert {m.filename for m in z.infolist()} == {
            k24.PREFIX + k24.APP, k24.PREFIX + "Info.plist"}
        assert z.testzip() is None
        info = plistlib.loads(z.read(k24.PREFIX + "Info.plist"))
        assert info["CFBundleIdentifier"] == k24.BUNDLE
    rejects(lambda: k24.package(artifact), "overwritten IPA")
    ref = json.loads((artifact / k24.REQUEST).read_text())
    statement = base64.b64decode(ref["payload_b64"])
    assert statement.startswith(b"DD_K24_SCHEMA=1\n")
    assert report["self_text_sha256"].encode() in statement
    assert k24.DOMAIN.endswith(b"\x00")
    envelope = root / "signed-statement.json"
    reviewed = signer.sign(artifact, secret, trusted, fingerprint, envelope)
    assert reviewed["external_signature_valid_offline"] is True
    assert reviewed["device_runtime_verified"] is False
    assert reviewed["runtime_self_security_proven"] is False
    assert signer.verify(artifact, envelope, trusted, fingerprint) == reviewed
    measured_text = (
        "DD_K24_SCHEMA=1\n"
        "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY\n"
        f"DD_K24_MAIN_UUID={report['app_executable_uuid']}\n"
        f"DD_K24_RUNTIME_TEXT_BYTES={report['self_text_size']}\n"
        f"DD_K24_RUNTIME_TEXT_SHA256={report['self_text_sha256']}\n"
        "DD_K24_EXTERNAL_KEY=PINNED_AT_BUILD\n"
        "DD_K24_EXTERNAL_SIGNATURE=NOT_IMPORTED\n"
        "DD_K24_COMPLETE=MEASUREMENT_ONLY\n"
    )
    signed_text = (
        "DD_K24_SCHEMA=1\n"
        "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY\n"
        f"DD_K24_MAIN_UUID={report['app_executable_uuid']}\n"
        f"DD_K24_RUNTIME_TEXT_SHA256={report['self_text_sha256']}\n"
        "DD_K24_EXTERNAL_ED25519=PASS\n"
        "DD_K24_SIGNED_EXPECTED_MATCH=PASS\n"
        "DD_K24_MUTATED_COPY=REJECTED\n"
        "DD_K24_TRUNCATED_COPY=REJECTED\n"
        "DD_K24_FORGED_STATEMENT=REJECTED\n"
        "DD_K24_SELF_SECURITY=NOT_PROVEN\n"
        "DD_K24_COMPLETE=PASS_LAB_ONLY\n"
    )
    log = root / "synthetic-user-report.log"
    log.write_text(measured_text, encoding="ascii")
    meta = device.validate(log, artifact / k24.REPORT, "measurement")
    assert meta["user_shared_text_matches_artifact"] is True
    assert meta["actual_iPhone_runtime_independently_verified"] is False
    assert meta["signed_reference_verified_offline"] is False
    log.write_text(signed_text, encoding="ascii")
    meta = device.validate(log, artifact / k24.REPORT, "signed", artifact,
                           envelope, trusted, fingerprint)
    assert meta["signed_reference_verified_offline"] is True
    assert meta["runtime_security_or_anti_tamper_proven"] is False
    rejects(lambda: device.validate(log, artifact / k24.REPORT, "signed"),
            "signed PASS log without an independently verified signature")
    log.write_text(signed_text.replace("PASS_LAB_ONLY", "PASS_SECURITY"), encoding="ascii")
    rejects(lambda: device.validate(log, artifact / k24.REPORT, "signed",
                                    artifact, envelope, trusted, fingerprint),
            "forged signed security PASS claim")
    log.write_text(signed_text, encoding="ascii")

    baseline = envelope.read_bytes()
    wrapped = json.loads(baseline)
    tampered_payload = bytearray(base64.b64decode(wrapped["payload_b64"]))
    tampered_payload[-2] ^= 1
    wrapped["payload_b64"] = base64.b64encode(tampered_payload).decode("ascii")
    envelope.write_text(json.dumps(wrapped, separators=(",", ":"), sort_keys=True) + "\n")
    rejects(lambda: signer.verify(artifact, envelope, trusted, fingerprint),
            "unsigned payload mutation")
    envelope.write_bytes(baseline)
    wrapped = json.loads(baseline)
    sig = bytearray(base64.b64decode(wrapped["signature_b64"]))
    sig[0] ^= 1
    wrapped["signature_b64"] = base64.b64encode(sig).decode("ascii")
    envelope.write_text(json.dumps(wrapped, separators=(",", ":"), sort_keys=True) + "\n")
    rejects(lambda: signer.verify(artifact, envelope, trusted, fingerprint),
            "tampered Ed25519 signature")
    envelope.write_bytes(baseline)
    rejects(lambda: signer.verify(artifact, envelope, trusted, "0" * 64),
            "forged separately approved SPKI fingerprint")
    rejects(lambda: signer.sign(artifact, secret, trusted, fingerprint, envelope),
            "signature overwrite")
    rejects(lambda: signer.sign(artifact, secret, trusted, fingerprint,
                                artifact / "hidden-signed.json"),
            "sign into artifact directory")
    badreq = artifact / k24.REQUEST
    original = badreq.read_bytes()
    badreq.write_bytes(original.replace(report["self_text_sha256"].encode(), b"0" * 64))
    rejects(lambda: signer.verify(artifact, envelope, trusted, fingerprint),
            "forged signing request")
    badreq.write_bytes(original)
    cfgpath = artifact / k24.KEY_CONFIG
    savedcfg = cfgpath.read_bytes()
    cfg = json.loads(savedcfg)
    cfg["public_key_b64"] = base64.b64encode(b"\x00" * 32).decode()
    cfgpath.write_text(json.dumps(cfg))
    rejects(lambda: k24.collect(artifact), "different pinned public key")
    cfgpath.write_bytes(savedcfg)
    binary = artifact / (k24.APP + ".app") / k24.APP
    orig_exe = binary.read_bytes()
    binary.write_bytes(orig_exe[:-1] + bytes([orig_exe[-1] ^ 1]))
    rejects(lambda: signer.verify(artifact, envelope, trusted, fingerprint),
            "modified post-link executable")
    binary.write_bytes(orig_exe)
    assert signer.verify(artifact, envelope, trusted, fingerprint) == reviewed

    empty = root / "measurement-only"
    empty.mkdir()
    k24.prepare(empty, "")
    assert "keyConfigured = false" in (empty / k24.EXPECTED_SWIFT).read_text()
    (empty / (k24.APP + ".app") / k24.APP).write_bytes(orig_exe)
    u = k24.package(empty)
    assert u["public_key_pinned_into_compiled_app"] is False
    rejects(lambda: signer.sign(empty, secret, trusted, fingerprint,
                                root / "other-signed.json"),
            "signing a measurement-only build")

swift = (ROOT / "scripts/custom_ollvm/kagura_k24/K24SelfTextLab.swift").read_text()
for token in (
    "_dyld_get_image_header(0)", "_dyld_get_image_vmaddr_slide(0)",
    "mach_header_64", "segment_command_64", "section_64",
    '"__text"', '"__TEXT"', "Data(bytes: ptr",
    "Curve25519.Signing.PublicKey", "isValidSignature",
    "K24Pinned.keyConfigured", "NO_EXTERNALLY_CONFIGURED_KEY",
    "RUNTIME_SELF_TEXT_DIFFERS_FROM_SIGNED_EXPECTED",
    "EXTERNAL_ED25519_SIGNATURE_INVALID", "DD_K24_MUTATED_COPY=REJECTED",
    "DD_K24_TRUNCATED_COPY=REJECTED", "DD_K24_FORGED_STATEMENT=REJECTED",
    "DD_K24_COMPLETE=MEASUREMENT_ONLY", "DD_K24_COMPLETE=PASS_LAB_ONLY",
    "DD_K24_SELF_SECURITY=NOT_PROVEN", "#if targetEnvironment(simulator)",
    "UIDocumentPickerViewController", "UTType.json"
):
    assert token in swift, token
workflow = (ROOT / ".github/workflows/kagura-k24-self-text-external-signature.yml").read_text()
for token in (
    "workflow_dispatch:", "runs-on: macos-14", "K24_TRUSTED_ED25519_PUBLIC_KEY_B64",
    "scripts/test_kagura_k24_own_text.py",
    "scripts/custom_ollvm/kagura_k24/package.py prepare",
    "scripts/custom_ollvm/kagura_k24/package.py package",
    "require_signed_mode", "approved_public_spki_sha256",
    "scripts/custom_ollvm/kagura_k24/key_preflight.py",
    "K24_REQUIRE_SIGNED_MODE", "K24_EXPECTED_SPKI_SHA256",
    "K24Pinned.swift", "xcrun swiftc -parse-as-library",
    "DuoDash-Kagura-K24-OWN-TEXT-EXTERNAL-SIGNATURE-LAB-EXPERIMENTAL"
):
    assert token in workflow, token
for banned in ("kagura_k18/", "codesign -s", "K24_PRIVATE_KEY", "git push",
               "kagura-bbcheck", "devicectl", "Crane.xm"):
    assert banned not in workflow, banned
for name in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k24" not in (ROOT / name).read_text(encoding="utf-8")
print("K24_PORTABLE_SELF_TEXT_EXTERNAL_KEY_LAB_PASS:"
      " signed/forged/changed executable/unsigned-only negatives rejected;"
      " macOS Swift iPhone self measurements NOT TESTED")
