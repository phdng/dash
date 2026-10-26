#!/usr/bin/env python3
"""K24 isolated iOS self __TEXT,__text measurement/unsigned IPA packager.

K24 measures its OWN running executable's __text (rather than K23's
bundled K14 specimen) and optionally verifies a separately imported
Ed25519-signed offline expected measurement. The public key is pinned
at build time from an externally chosen key; CI NEVER signs anything.
No self-defence, immutable root, device attestation or Crane integration.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import plistlib
import re
import stat
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kagura_k16"))
import macho_measure as k16

APP = "KaguraK24SelfTextLab"
BUNDLE = "com.duodash.research.kagurak24selftextlab"
IPA = APP + "-TrollStore-arm64.ipa"
PREFIX = "Payload/" + APP + ".app/"
REQUEST = "Kagura-K24-SELF-TEXT-SIGNING-REQUEST.json"
REPORT = "Kagura-K24-SELF-TEXT-IPA-REPORT.json"
KEY_CONFIG = "K24KeyConfig.json"
EXPECTED_SWIFT = "K24Pinned.swift"
DOMAIN = b"DuoDash/K24/OnDeviceSelfText/v1\0"
SCOPE = "K24_STANDALONE_OWN_RUNNING_TEXT_MEASUREMENT_EXTERNAL_SIGNED_REFERENCE_LAB_ONLY"
MAX_FILE = 32 * 1024 * 1024
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
UUID = re.compile(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\Z")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def public_key(raw_b64: str) -> bytes:
    if raw_b64 == "":
        return b""
    try:
        decoded = base64.b64decode(raw_b64, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise AssertionError("K24 public key needs canonical base64") from exc
    if len(decoded) != 32 or base64.b64encode(decoded).decode("ascii") != raw_b64:
        raise AssertionError("K24 public key must be 32-byte Ed25519 raw canonical base64")
    return decoded


def pinned_source(raw: bytes) -> str:
    # An absent key deliberately disables signature PASS. Never generate a
    # known test key in CI or silently accept untrusted envelope signatures.
    values = ", ".join(str(x) for x in raw)
    return (
        "// Generated K24 public key, configured externally; no private key in CI.\n"
        "enum K24Pinned {\n"
        f"    static let keyConfigured = {'true' if len(raw) == 32 else 'false'}\n"
        f"    static let publicKey: [UInt8] = [{values}]\n"
        "}\n"
    )


def prepare(out: Path, raw_b64: str) -> None:
    if not out.is_dir() or out.is_symlink():
        raise AssertionError("K24 requires existing build output directory")
    if any((out / n).exists() for n in (EXPECTED_SWIFT, KEY_CONFIG, APP + ".app")):
        raise AssertionError("K24 refuses overwrite prepare targets")
    key = public_key(raw_b64)
    app = out / (APP + ".app")
    app.mkdir()
    (app / "Info.plist").write_bytes((HERE / "Info.plist").read_bytes())
    (out / EXPECTED_SWIFT).write_text(pinned_source(key), encoding="utf-8")
    (out / KEY_CONFIG).write_text(json.dumps({
        "schema": 1,
        "scope": SCOPE,
        "public_key_b64": raw_b64,
        "external_signature_gate_configured": len(key) == 32,
        "trusted_key_fingerprint_preapproved_outside_artifact": False,
        "unsigned_measurement_only_if_key_missing": True,
    }, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def payload(measured: dict) -> bytes:
    if (measured.get("uuid") is None or not UUID.fullmatch(measured["uuid"]) or
        not HEX64.fullmatch(measured.get("text_sha256", "")) or
        type(measured.get("text_size")) is not int or
        not (16 <= measured["text_size"] <= MAX_FILE)):
        raise AssertionError("K24 signing request source malformed")
    return (
        "DD_K24_SCHEMA=1\n"
        "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY\n"
        f"DD_K24_UUID={measured['uuid']}\n"
        f"DD_K24_TEXT_SIZE={measured['text_size']}\n"
        f"DD_K24_TEXT_SHA256={measured['text_sha256']}\n"
    ).encode("ascii")


def info_check(raw: bytes) -> None:
    obj = plistlib.loads(raw)
    for k, v in {
        "CFBundleExecutable": APP, "CFBundleIdentifier": BUNDLE,
        "CFBundleVersion": "1", "MinimumOSVersion": "15.0",
        "CFBundleSupportedPlatforms": ["iPhoneOS"], "UIDeviceFamily": [1],
        "CFBundlePackageType": "APPL", "LSRequiresIPhoneOS": True,
    }.items():
        if obj.get(k) != v:
            raise AssertionError("K24 unexpected Info.plist " + k)


def collect(out: Path) -> tuple[dict, bytes]:
    cfgp = out / KEY_CONFIG
    swiftp = out / EXPECTED_SWIFT
    app = out / (APP + ".app")
    if (not cfgp.is_file() or cfgp.is_symlink() or
        not swiftp.is_file() or swiftp.is_symlink() or
        not app.is_dir() or app.is_symlink()):
        raise AssertionError("K24 app/key config/source absent or symlinked")
    cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    key = public_key(cfg["public_key_b64"])
    if cfg != {
        "schema": 1, "scope": SCOPE, "public_key_b64": cfg["public_key_b64"],
        "external_signature_gate_configured": len(key) == 32,
        "trusted_key_fingerprint_preapproved_outside_artifact": False,
        "unsigned_measurement_only_if_key_missing": True,
    } or swiftp.read_text(encoding="utf-8") != pinned_source(key):
        raise AssertionError("K24 generated public-key source/config drifted")
    if {p.name for p in app.iterdir()} != {APP, "Info.plist"}:
        raise AssertionError("K24 app must contain exactly binary and plist")
    exe = app / APP
    if (not exe.is_file() or exe.is_symlink() or
        not (256 <= exe.stat().st_size <= MAX_FILE)):
        raise AssertionError("K24 executable missing/unbounded")
    raw = exe.read_bytes()
    m = k16.inspect_macho(raw)
    info_check((app / "Info.plist").read_bytes())
    measure = {
        "uuid": m["uuid"], "text_size": m["text_size"],
        "text_sha256": m["text_sha256"]
    }
    content = payload(measure)
    request = {
        "schema": 1, "scope": SCOPE,
        "domain": DOMAIN[:-1].decode("ascii"),
        "payload_b64": base64.b64encode(content).decode("ascii"),
        "expected_text_sha256": m["text_sha256"],
        "expected_text_size": m["text_size"],
        "expected_uuid": m["uuid"],
        "signature_required_from_offline_external_private_key": True,
        "external_signature_created_by_ci": False,
    }
    return {
        "schema": 1, "scope": SCOPE,
        "app_executable_sha256": sha(raw),
        "app_executable_uuid": m["uuid"],
        "self_text_section": "__TEXT,__text",
        "self_text_file_offset": m["text_file_offset"],
        "self_text_size": m["text_size"],
        "self_text_sha256": m["text_sha256"],
        "signature_envelope_imported_at_runtime": False,
        "public_key_pinned_into_compiled_app": len(key) == 32,
        "public_key_raw_sha256": sha(key) if key else None,
        "external_trust_root_independently_approved": False,
        "external_signature_created_by_ci": False,
        "device_runtime_text_matches_file": "NOT_TESTED",
        "signature_runtime_verification": "NOT_TESTED",
        "actual_runtime_self_measurement_source_present": True,
        "runtime_self_integrity_security_proven": False,
        "device_attestation": False,
        "anti_tamper_proven": False,
        "arm64e_pac_tested": False,
        "k15_bbcheck_dependency": False,
        "k18_dependency": False,
        "crane_production_modified": False,
        "signing": "UNSIGNED"
    }, json.dumps(request, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def package(out: Path) -> dict:
    report, req = collect(out)
    if any((out / n).exists() for n in (IPA, REQUEST, REPORT)):
        raise AssertionError("K24 refuses overwrite package outputs")
    app = out / (APP + ".app")
    with zipfile.ZipFile(out / IPA, "w") as archive:
        for member in ("Info.plist", APP):
            info = zipfile.ZipInfo(PREFIX + member, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | (0o755 if member == APP else 0o644)) << 16
            archive.writestr(info, (app / member).read_bytes())
    with zipfile.ZipFile(out / IPA) as archive:
        members = archive.infolist()
        if (len(members) != 2 or {m.filename for m in members} !=
            {PREFIX + APP, PREFIX + "Info.plist"} or archive.testzip() is not None):
            raise AssertionError("K24 malformed unsigned IPA")
        for member in members:
            if (stat.S_IFMT(member.external_attr >> 16) != stat.S_IFREG or
                member.file_size > MAX_FILE or member.flag_bits & 1 or
                archive.read(member.filename) !=
                (app / member.filename.rsplit("/", 1)[-1]).read_bytes()):
                raise AssertionError("K24 IPA entry mismatch")
    report["ipa_sha256"] = sha((out / IPA).read_bytes())
    report["signing_request_sha256"] = sha(req)
    (out / REQUEST).write_bytes(req)
    (out / REPORT).write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("mode", choices=("prepare", "package"))
    a.add_argument("--out", type=Path, required=True)
    a.add_argument("--trusted-ed25519-public-key-b64", default="")
    opts = a.parse_args()
    if opts.mode == "prepare":
        prepare(opts.out, opts.trusted_ed25519_public_key_b64)
    else:
        if opts.trusted_ed25519_public_key_b64:
            a.error("package does not accept new key values after compilation")
        package(opts.out)
    print("K24_OWN_TEXT_LAB_" + opts.mode.upper() +
          "_PASS: unsigned, iPhone NOT_TESTED, anti-tamper NOT_PROVEN")


if __name__ == "__main__":
    main()
