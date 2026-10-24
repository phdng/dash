#!/usr/bin/env python3
"""K18 isolated unsigned reference-verifier iOS IPA, never running-code integrity.

Build-time owner-provided rotated Ed25519 public key is packaged to
facilitate a CryptoKit DEVICE FUNCTIONALITY test. This embedded key is not
an independently immutable trust anchor against a repackaging attacker.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import plistlib
import shutil
import stat
import sys
import zipfile
from pathlib import Path
from cryptography.hazmat.primitives import serialization

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "kagura_k17"))
import signature as k17  # noqa: E402
sys.path.insert(0, str(HERE.parent / "kagura_k16"))
import macho_measure as k16  # noqa: E402

NAME = "KaguraK18ReferenceLab"
BUNDLE = "com.duodash.research.kagurak18referencelab"
PREFIX = "Payload/" + NAME + ".app/"
KNOWN_EXPOSED_TEST_KEY = "2e91a1403ffc97eb66c2c1717205eb054ce3c341898b6978b007cb5c56241f40"
SCOPE = "K18_READ_ONLY_ROTATED_ED25519_SIGNED_K14_SPECIMEN_IOS_LAB_NOT_SELF_INTEGRITY"
IPA = "KaguraK18ReferenceLab-TrollStore-arm64.ipa"
REPORT = "Kagura-K18-IPA-REPORT.json"
RESOURCES = {
    "Kagura-K16-OFFLINE-TEXT-MANIFEST.json": k16.MANIFEST,
    "Kagura-K17-K16-MANIFEST.ed25519": k17.SIGNATURE_FILE,
    "KaguraCSEBreakLab.reference": k16.FILE_NAMES["ios_csebreak_lab"],
}
EXPECTED = {NAME, "Info.plist", "KaguraK18Trust.plist", *RESOURCES}
MAX_MEMBER = 32 * 1024 * 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_external(out: Path, trusted: Path, expected: str) -> tuple[bytes, dict]:
    if expected == KNOWN_EXPOSED_TEST_KEY:
        raise AssertionError("K18 explicitly rejects previously exposed K17 TEST private-key fingerprint")
    key, fingerprint = k17.load_trusted(trusted, expected)
    if fingerprint == KNOWN_EXPOSED_TEST_KEY:
        raise AssertionError("K18 exposed signer key forbidden")
    receipt = k17.verified(out, trusted, expected)
    raw = key.public_bytes(encoding=serialization.Encoding.Raw,
                           format=serialization.PublicFormat.Raw)
    if len(raw) != 32:
        raise AssertionError("K18 expects Ed25519 raw public key 32 bytes")
    return raw, receipt


def prepare(out: Path, trusted: Path, expected: str) -> dict:
    raw, receipt = validate_external(out, trusted, expected)
    app = out / (NAME + ".app")
    if app.exists() or app.is_symlink():
        raise AssertionError("K18 app output folder must be fresh")
    app.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(HERE / "Info.plist", app / "Info.plist")
    trust = {"Ed25519PublicKeyRawBase64": base64.b64encode(raw).decode("ascii"),
             "ExpectedSPKISHA256": expected}
    (app / "KaguraK18Trust.plist").write_bytes(plistlib.dumps(trust, sort_keys=True))
    for dst, source in RESOURCES.items():
        source_file = out / source
        if not source_file.is_file() or source_file.is_symlink():
            raise AssertionError("K18 missing signed reference resource: " + source)
        shutil.copyfile(source_file, app / dst)
    manifest = json.loads((app / k16.MANIFEST).read_text(encoding="utf-8"))
    ios = manifest["linked_binaries"]["ios_csebreak_lab"]
    specimen = (app / "KaguraCSEBreakLab.reference").read_bytes()
    if k16.inspect_macho(specimen) != ios:
        raise AssertionError("K18 stored K14 exemplar mismatches K16 signed manifest")
    return {"external_public_spki_sha256": expected,
            "signed_k16_manifest_sha256": receipt["payload_sha256"],
            "signature_sha256": receipt["signature_sha256"],
            "reference_uuid": ios["uuid"],
            "reference_binary_sha256": ios["binary_sha256"],
            "reference_text_sha256": ios["text_sha256"]}


def info_check(data: bytes) -> None:
    info = plistlib.loads(data)
    for key, value in {
        "CFBundleExecutable": NAME,
        "CFBundleIdentifier": BUNDLE,
        "CFBundlePackageType": "APPL",
        "MinimumOSVersion": "15.0",
        "CFBundleSupportedPlatforms": ["iPhoneOS"],
        "UIDeviceFamily": [1],
        "LSRequiresIPhoneOS": True,
    }.items():
        if info.get(key) != value:
            raise AssertionError("K18 incorrect app Info.plist: " + key)


def collect(app: Path) -> dict:
    if not app.is_dir() or app.is_symlink() or app.name != NAME + ".app":
        raise AssertionError("K18 app path invalid")
    entries = list(app.iterdir())
    if len(entries) != len(EXPECTED) or {x.name for x in entries} != EXPECTED:
        raise AssertionError("K18 app contains unsigned unknown member or missing resource")
    if any(x.is_symlink() or not x.is_file() or
           x.stat().st_size == 0 or x.stat().st_size > MAX_MEMBER for x in entries):
        raise AssertionError("K18 app member invalid")
    info_check((app / "Info.plist").read_bytes())
    program = k16.inspect_macho((app / NAME).read_bytes())
    trust = plistlib.loads((app / "KaguraK18Trust.plist").read_bytes())
    raw = base64.b64decode(trust["Ed25519PublicKeyRawBase64"], validate=True)
    if len(raw) != 32:
        raise AssertionError("K18 embedded public key invalid")
    spki = bytes.fromhex("302a300506032b6570032100") + raw
    fingerprint = sha(spki)
    if fingerprint != trust["ExpectedSPKISHA256"] or fingerprint == KNOWN_EXPOSED_TEST_KEY:
        raise AssertionError("K18 unapproved/mismatched/previously exposed trust fingerprint")
    manifest = (app / k16.MANIFEST).read_bytes()
    signed = k17.DOMAIN + manifest
    from cryptography.hazmat.primitives.asymmetric import ed25519
    key = ed25519.Ed25519PublicKey.from_public_bytes(raw)
    key.verify((app / k17.SIGNATURE_FILE).read_bytes(), signed)
    source = json.loads(manifest)
    if (source.get("scope") != k16.SCOPE or
        source.get("runtime_verifier_implemented") is not False or
        source.get("adversarial_tamper_protection_proven") is not False or
        source.get("bbcheck_security_integrity") != "BLOCKED_K15_WEAK_ALWAYS_PASS_STUB"):
        raise AssertionError("K18 bundled reference is not original no-security K16 scope")
    binary = (app / "KaguraCSEBreakLab.reference").read_bytes()
    exemplar = k16.inspect_macho(binary)
    if exemplar != source["linked_binaries"]["ios_csebreak_lab"]:
        raise AssertionError("K18 read-only K14 specimen no longer matches signed manifest")
    return {
        "schema": 1, "scope": SCOPE, "app_bundle": BUNDLE,
        "app_macho_uuid": program["uuid"],
        "app_macho_sha256": program["binary_sha256"],
        "reference_uuid": exemplar["uuid"],
        "reference_sha256": exemplar["binary_sha256"],
        "reference_text_sha256": exemplar["text_sha256"],
        "signed_k16_manifest_sha256": sha(manifest),
        "signature_sha256": sha((app / k17.SIGNATURE_FILE).read_bytes()),
        "public_spki_sha256": fingerprint,
        "embedded_public_key_is_immutable_trust_anchor": False,
        "device_execution": "NOT_TESTED_BY_CI",
        "runtime_self_integrity": "NOT_IMPLEMENTED",
        "iphone_attestation": False,
        "original_bbcheck_fixed": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
    }


def zipinfo(path: str, executable: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, (2020, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    return info


def package(out: Path) -> dict:
    app = out / (NAME + ".app")
    valid = collect(app)
    dest = out / IPA
    if dest.exists():
        raise AssertionError("K18 refuses to overwrite previous lab IPA")
    with zipfile.ZipFile(dest, "w") as zf:
        for name in sorted(EXPECTED):
            zf.writestr(zipinfo(PREFIX + name, name == NAME), (app / name).read_bytes())
    with zipfile.ZipFile(dest, "r") as zf:
        members = zf.infolist()
        if len(members) != len(EXPECTED) or zf.testzip() is not None or (
                {m.filename for m in members} != {PREFIX + x for x in EXPECTED}):
            raise AssertionError("K18 ZIP structural/CRC check failed")
        for member in members:
            permissions = member.external_attr >> 16
            if (stat.S_IFMT(permissions) != stat.S_IFREG or
                    member.file_size > MAX_MEMBER or
                    (member.filename == PREFIX + NAME and not permissions & stat.S_IXUSR)):
                raise AssertionError("K18 IPA file type/permission invalid")
        for name in EXPECTED:
            if zf.read(PREFIX + name) != (app / name).read_bytes():
                raise AssertionError("K18 packed IPA resource byte mismatch")
    valid["ipa_sha256"] = sha(dest.read_bytes())
    (out / REPORT).write_text(json.dumps(valid, sort_keys=True, indent=2) + "\n",
                              encoding="utf-8")
    print("K18_READ_ONLY_BUNDLED_REFERENCE_UNSIGNED_IPA_STRUCTURE_PASS:"
          " rotated signed reference verified offline; device NOT_TESTED")
    return valid


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("prepare", "package"))
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--trusted-public-key", type=Path)
    p.add_argument("--expected-spki-sha256")
    args = p.parse_args()
    if args.mode == "prepare":
        if args.trusted_public_key is None or args.expected_spki_sha256 is None:
            p.error("prepare requires approved EXTERNAL Ed25519 public PEM + SPKI SHA")
        prepare(args.out, args.trusted_public_key, args.expected_spki_sha256)
    else:
        package(args.out)


if __name__ == "__main__":
    main()
