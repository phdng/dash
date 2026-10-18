#!/usr/bin/env python3
"""K14 deterministic unsigned research IPA with strict arm64 Mach-O UUID."""
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

APP = "KaguraCSEBreakLab"
BUNDLE = "com.duodash.research.kaguracsebreaklab"
PREFIX = "Payload/" + APP + ".app/"
MAX = 24 * 1024 * 1024
SCOPE = "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def executable_uuid(data: bytes) -> str:
    if not (56 <= len(data) <= MAX):
        raise AssertionError("K14 executable size invalid")
    magic, cpu, sub, kind, ncmds, size, _, _ = struct.unpack_from("<IIIIIIII", data)
    if (magic, cpu, sub, kind) != (0xFEEDFACF, 0x0100000C, 0, 2):
        raise AssertionError("K14 only arm64 subtype0 MH_EXECUTE, not arm64e")
    if not (1 <= ncmds <= 4096 and 24 <= size <= 1 << 20 and
            32 + size <= len(data)):
        raise AssertionError("K14 Mach-O load command bounds invalid")
    pos, end, uuids = 32, 32 + size, []
    for _ in range(ncmds):
        if pos + 8 > end:
            raise AssertionError("K14 truncated load command")
        cmd, length = struct.unpack_from("<II", data, pos)
        if length < 8 or length % 4 or pos + length > end:
            raise AssertionError("K14 corrupted load command")
        if cmd == 0x1B:
            if length != 24:
                raise AssertionError("K14 wrong LC_UUID size")
            uuids.append(str(uuid.UUID(bytes=data[pos + 8:pos + 24])))
        pos += length
    if pos != end or len(uuids) != 1:
        raise AssertionError("K14 needs exactly one real LC_UUID")
    return uuids[0]


def check_info(data: bytes) -> None:
    info = plistlib.loads(data)
    expected = {
        "CFBundleExecutable": APP,
        "CFBundleIdentifier": BUNDLE,
        "CFBundlePackageType": "APPL",
        "CFBundleSupportedPlatforms": ["iPhoneOS"],
        "MinimumOSVersion": "15.0",
        "UIDeviceFamily": [1],
        "LSRequiresIPhoneOS": True,
    }
    if any(info.get(k) != v for k, v in expected.items()):
        raise AssertionError("K14 IPA Info.plist mismatch")


def check_app(app: Path) -> tuple[bytes, bytes]:
    if not app.is_dir() or app.is_symlink() or app.name != APP + ".app":
        raise AssertionError("K14 standalone app path invalid")
    entries = list(app.iterdir())
    if ({x.name for x in entries} != {APP, "Info.plist"} or
            any(not x.is_file() or x.is_symlink() for x in entries)):
        raise AssertionError("K14 app unexpected files/signatures/symlinks")
    info, executable = (app / "Info.plist").read_bytes(), (app / APP).read_bytes()
    check_info(info)
    executable_uuid(executable)
    return info, executable


def zip_info(name: str, executable: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    return info


def verify_ipa(ipa: Path) -> dict:
    with zipfile.ZipFile(ipa) as zf:
        entries = zf.infolist()
        if (len(entries) != 2 or
                {i.filename for i in entries} !=
                {PREFIX + APP, PREFIX + "Info.plist"} or
                zf.testzip() is not None):
            raise AssertionError("K14 IPA must contain exactly two clean files")
        for i in entries:
            mode = i.external_attr >> 16
            if (i.file_size > MAX or stat.S_IFMT(mode) != stat.S_IFREG or
                    (i.filename.endswith("/" + APP) and
                     not mode & stat.S_IXUSR)):
                raise AssertionError("K14 IPA permissions or member type invalid")
        info = zf.read(PREFIX + "Info.plist")
        binary = zf.read(PREFIX + APP)
    check_info(info)
    return {
        "schema": 1,
        "scope": SCOPE,
        "bundle_identifier": BUNDLE,
        "architecture": "arm64:0x00000000",
        "filetype": "MH_EXECUTE",
        "app_macho_uuid": executable_uuid(binary),
        "binary_sha256": sha(binary),
        "ipa_sha256": sha(ipa.read_bytes()),
        "signing": "UNSIGNED",
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "arm64e_pac_runtime": "NOT_TESTED",
        "crane_production_modified": False,
    }


def package(app: Path, ipa: Path, report_path: Path) -> dict:
    info, binary = check_app(app)
    ipa.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ipa, "w") as zf:
        zf.writestr(zip_info(PREFIX + APP, True), binary)
        zf.writestr(zip_info(PREFIX + "Info.plist", False), info)
    result = verify_ipa(ipa)
    if result["binary_sha256"] != sha(binary):
        raise AssertionError("K14 embedded app binary changed")
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("K14_UNSIGNED_IPA_STRUCTURE_PASS: arm64 UUID+SHA, device NOT_TESTED")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--app", type=Path, required=True)
    p.add_argument("--ipa", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    package(a.app, a.ipa, a.report)


if __name__ == "__main__":
    main()
