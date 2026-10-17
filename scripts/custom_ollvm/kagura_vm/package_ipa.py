#!/usr/bin/env python3
"""Strict deterministic stand-alone Kagura VM arm64 TrollStore IPA packaging."""
from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import stat
import struct
import uuid
import zipfile
from pathlib import Path

APP = "KaguraVMLab"
BUNDLE = "com.duodash.research.kaguravmlab"
PREFIX = "Payload/KaguraVMLab.app/"
FILES = ("Info.plist", APP)
MAX_BINARY = 16 * 1024 * 1024


def binary_uuid(raw: bytes) -> str:
    if not 32 <= len(raw) <= MAX_BINARY:
        raise AssertionError("Unexpected executable binary size")
    magic, cpu, subtype, filetype, ncmds, sizecmds, _, _ = struct.unpack_from(
        "<IIIIIIII", raw
    )
    if (magic, cpu, subtype, filetype) != (0xFEEDFACF, 0x0100000C, 0, 2):
        raise AssertionError("K7 requires genuine arm64 MH_EXECUTE, not arm64e")
    if not (1 <= ncmds <= 4096 and
            24 <= sizecmds <= 1_048_576 and 32 + sizecmds <= len(raw)):
        raise AssertionError("Malformed native Mach-O load command bounds")
    start, end, uuids = 32, 32 + sizecmds, []
    for _ in range(ncmds):
        if end - start < 8:
            raise AssertionError("Truncated executable Mach-O command")
        cmd, length = struct.unpack_from("<II", raw, start)
        if length < 8 or (length % 4) or length > end - start:
            raise AssertionError("Invalid Mach-O command size")
        if cmd == 0x1B:
            if length != 24:
                raise AssertionError("Invalid LC_UUID command")
            uuids.append(str(uuid.UUID(bytes=raw[start + 8:start + 24])))
        start += length
    if start != end or len(uuids) != 1:
        raise AssertionError("Missing/duplicate LC_UUID or command list remainder")
    return uuids[0]


def inspect(app: Path) -> dict:
    if app.name != APP + ".app" or not app.is_dir() or app.is_symlink():
        raise AssertionError("Expected isolated KaguraVMLab.app")
    files = list(app.iterdir())
    if {p.name for p in files} != set(FILES) or any(
        not p.is_file() or p.is_symlink() for p in files
    ):
        raise AssertionError("Kagura VM IPA must contain only two regular files")
    info = plistlib.loads((app / "Info.plist").read_bytes())
    for key, value in {
        "CFBundleExecutable": APP,
        "CFBundleIdentifier": BUNDLE,
        "CFBundlePackageType": "APPL",
        "MinimumOSVersion": "15.0",
        "UIDeviceFamily": [1],
        "CFBundleSupportedPlatforms": ["iPhoneOS"],
        "LSRequiresIPhoneOS": True,
    }.items():
        if info.get(key) != value:
            raise AssertionError(f"Invalid K7 VM bundle property {key}")
    data = (app / APP).read_bytes()
    return {"macho_uuid": binary_uuid(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def zip_entry(path: str, executable: bool) -> zipfile.ZipInfo:
    z = zipfile.ZipInfo(path, date_time=(2020, 1, 1, 0, 0, 0))
    z.compress_type = zipfile.ZIP_DEFLATED
    z.create_system = 3
    z.external_attr = (stat.S_IFREG |
                       (0o755 if executable else 0o644)) << 16
    return z


def verify_ipa(ipa: Path) -> dict:
    if not ipa.is_file():
        raise AssertionError("K7 IPA missing")
    with zipfile.ZipFile(ipa) as zf:
        infos = zf.infolist()
        if len(infos) != 2 or {x.filename for x in infos} != {
            PREFIX + x for x in FILES
        } or zf.testzip() is not None:
            raise AssertionError("Unexpected K7 IPA ZIP paths/CRC")
        for item in infos:
            mode = item.external_attr >> 16
            if item.file_size > MAX_BINARY or stat.S_IFMT(mode) != stat.S_IFREG:
                raise AssertionError("Invalid K7 ZIP file type or size")
            if item.filename.endswith("/" + APP) and not mode & stat.S_IXUSR:
                raise AssertionError("Missing executable permission")
        info = plistlib.loads(zf.read(PREFIX + "Info.plist"))
        if info.get("CFBundleIdentifier") != BUNDLE or (
            info.get("CFBundleExecutable") != APP
        ):
            raise AssertionError("Wrong K7 embedded app identity")
        exe = zf.read(PREFIX + APP)
        embedded_uuid = binary_uuid(exe)
    return {
        "schema": 1,
        "scope": "STANDALONE_K7_VM_IPA",
        "bundle_identifier": BUNDLE,
        "architecture": "arm64",
        "filetype": "MH_EXECUTE",
        "macho_uuid": embedded_uuid,
        "binary_sha256": hashlib.sha256(exe).hexdigest(),
        "ipa_sha256": hashlib.sha256(ipa.read_bytes()).hexdigest(),
        "compiler_provenance_verified_by_ipa_parser": False,
        "separate_compiler_evidence": "Kagura-K7-IPA-EVIDENCE.json",
        "device_execution": "NOT_TESTED_BY_CI",
        "trollstore_installation": "MANUAL_NOT_TESTED_BY_CI",
        "arm64e_pac_runtime": "NOT_TESTED",
        "crane_production_modified": False,
        "k5_ipa_modified": False,
        "security_attestation": False,
    }


def package(app: Path, ipa: Path, report: Path) -> dict:
    source = inspect(app)
    ipa.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ipa, "w") as zf:
        for filename in FILES:
            zf.writestr(zip_entry(PREFIX + filename, filename == APP),
                        (app / filename).read_bytes())
    verified = verify_ipa(ipa)
    if verified["binary_sha256"] != source["sha256"] or (
        verified["macho_uuid"] != source["macho_uuid"]
    ):
        raise AssertionError("K7 packaged executable UUID/SHA mismatch")
    report.write_text(json.dumps(verified, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("K7_VM_IPA_STRUCTURE_PASS: separate arm64 MH_EXECUTE UUID/SHA; "
          "unsigned and no device execution claimed")
    return verified


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("app", "ipa", "report"):
        p.add_argument("--" + name, type=Path, required=True)
    options = p.parse_args()
    package(options.app, options.ipa, options.report)


if __name__ == "__main__":
    main()
