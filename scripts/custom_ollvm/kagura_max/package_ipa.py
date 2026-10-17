#!/usr/bin/env python3
"""Deterministic independent arm64 KaguraLab IPA for manual TrollStore import.

This does NOT sign, install, launch, alter Mach-O subtypes or establish
device runtime evidence. Requires genuine Apple linker MH_EXECUTE + LC_UUID.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import stat
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/protection_lab"))
import device_audit
import device_evidence

APP_NAME = "KaguraLab"
BUNDLE_ID = "com.duodash.research.kaguralab"
PREFIX = "Payload/KaguraLab.app/"
FILES = ("Info.plist", APP_NAME)
MAX_BINARY = 16 * 1024 * 1024


def inspect_app(app: Path) -> dict:
    if not app.is_dir() or app.is_symlink() or app.name != APP_NAME + ".app":
        raise AssertionError("Expected a real KaguraLab.app")
    members = list(app.iterdir())
    if {p.name for p in members} != set(FILES) or any(
        not p.is_file() or p.is_symlink() for p in members
    ):
        raise AssertionError("Standalone IPA must contain only Info.plist and Mach-O")
    info = plistlib.loads((app / "Info.plist").read_bytes())
    for key, value in {
        "CFBundleIdentifier": BUNDLE_ID, "CFBundleExecutable": APP_NAME,
        "CFBundlePackageType": "APPL", "MinimumOSVersion": "15.0",
        "UIDeviceFamily": [1], "CFBundleSupportedPlatforms": ["iPhoneOS"],
        "LSRequiresIPhoneOS": True,
    }.items():
        if info.get(key) != value:
            raise AssertionError(f"Unexpected KaguraLab bundle setting: {key}")
    exe = app / APP_NAME
    if not (32 <= exe.stat().st_size <= MAX_BINARY):
        raise AssertionError("Unexpected IPA executable size")
    details = device_audit.inspect_executable(exe, "arm64")
    details["macho_uuid"] = device_evidence.macho_uuid(exe)
    return details


def zip_entry(path: str, executable: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG |
                          (0o755 if executable else 0o644)) << 16
    return info


def in_archive_uuid(data: bytes) -> str:
    import uuid
    if len(data) < 32:
        raise AssertionError("Truncated embedded Mach-O")
    magic, cpu, subtype, kind, count, cmdsize, _, _ = struct.unpack_from(
        "<IIIIIIII", data
    )
    if (magic != device_audit.MAGIC or cpu != device_audit.ARM64_CPUTYPE or
        subtype != 0 or kind != device_audit.MH_EXECUTE or
        not 1 <= count <= 4096 or not 24 <= cmdsize <= 1024 * 1024 or
        len(data) < 32 + cmdsize):
        raise AssertionError("IPA must embed genuine arm64 MH_EXECUTE")
    cursor, end, uuids = 32, 32 + cmdsize, []
    for _ in range(count):
        if end - cursor < 8:
            raise AssertionError("Truncated Mach-O load command")
        tag, length = struct.unpack_from("<II", data, cursor)
        if length < 8 or length % 4 or length > end - cursor:
            raise AssertionError("Malformed embedded Mach-O load command")
        if tag == 0x1B:
            if length != 24:
                raise AssertionError("Malformed embedded LC_UUID")
            uuids.append(str(uuid.UUID(bytes=data[cursor + 8: cursor + 24])))
        cursor += length
    if cursor != end or len(uuids) != 1:
        raise AssertionError("Expected exactly one embedded Mach-O LC_UUID")
    return uuids[0]


def verify_ipa(ipa: Path) -> dict:
    if not ipa.is_file():
        raise AssertionError("IPA not created")
    with zipfile.ZipFile(ipa) as zf:
        files = zf.infolist()
        names = [item.filename for item in files]
        if set(names) != {PREFIX + item for item in FILES} or len(names) != 2:
            raise AssertionError("IPA contains unexpected paths/files")
        if zf.testzip() is not None:
            raise AssertionError("Invalid embedded CRC")
        for item in files:
            if item.file_size > MAX_BINARY or (
                stat.S_IFMT(item.external_attr >> 16) != stat.S_IFREG
            ):
                raise AssertionError("Unexpected archive mode or size")
        exe_info = zf.getinfo(PREFIX + APP_NAME)
        if not (exe_info.external_attr >> 16) & stat.S_IXUSR:
            raise AssertionError("Mach-O executable permission missing")
        info = plistlib.loads(zf.read(PREFIX + "Info.plist"))
        if info.get("CFBundleIdentifier") != BUNDLE_ID or (
            info.get("CFBundleExecutable") != APP_NAME
        ):
            raise AssertionError("Wrong KaguraLab Info.plist")
        data = zf.read(PREFIX + APP_NAME)
        bundle_uuid = in_archive_uuid(data)
    return {
        "schema": 1,
        "bundle_identifier": BUNDLE_ID,
        "architecture": "arm64",
        "filetype": "MH_EXECUTE",
        "macho_uuid": bundle_uuid,
        "binary_sha256": hashlib.sha256(data).hexdigest(),
        "ipa_sha256": hashlib.sha256(ipa.read_bytes()).hexdigest(),
        "pipeline_expected": "LLVM19_KAGURA_STR_FLA_BCF_SUB_CO_BBR_BBS",
        "compiler_provenance_verified_by_ipa_parser": False,
        "separate_compiler_evidence": "KaguraLab-seven-pass-evidence.json",
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "trollstore_installation": "NOT_TESTED_BY_CI",
        "arm64e_pac_runtime": "DEFERRED_NO_A12_DEVICE",
        "crane_production_changed": False,
        "security_strength_attested": False,
    }


def package(app: Path, ipa: Path, report: Path) -> dict:
    details = inspect_app(app)
    ipa.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ipa, "w") as zf:
        for name in FILES:
            zf.writestr(zip_entry(PREFIX + name, name == APP_NAME),
                        (app / name).read_bytes())
    checked = verify_ipa(ipa)
    if checked["binary_sha256"] != details["sha256"] or (
        checked["macho_uuid"] != details["macho_uuid"]
    ):
        raise AssertionError("Embedded Mach-O does not match on-disk app")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(checked, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("KAGURA_TROLLSTORE_IPA_STRUCTURE_PASS: arm64 MH_EXECUTE, LC_UUID and "
          "SHA256, no signing/install/runtime claimed")
    return checked


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--ipa", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    opts = parser.parse_args()
    package(opts.app, opts.ipa, opts.report)


if __name__ == "__main__":
    main()
