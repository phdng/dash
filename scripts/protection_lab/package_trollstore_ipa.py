#!/usr/bin/env python3
"""Pack a standalone arm64 Protection Lab .app into a standard iOS IPA.

No signing, entitlements, TrollStore installation, CoreTrust manipulation,
or modification of the Mach-O takes place. Structure/ABI audit only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import stat
import struct
import zipfile
from pathlib import Path

import device_audit

EXPECTED_EXECUTABLE = "ProtectionLab"
EXPECTED_BUNDLE_ID = "com.duodash.research.protectionlab"
PAYLOAD_PREFIX = "Payload/ProtectionLab.app/"
MAX_FILES = 128
MAX_BYTES = 64 * 1024 * 1024


def _app_entries(app: Path) -> list[Path]:
    if not app.is_dir() or app.is_symlink():
        raise AssertionError("Expected a real ProtectionLab.app directory")
    all_paths = sorted(app.rglob("*"), key=lambda p: p.relative_to(app).as_posix())
    files = []
    for path in all_paths:
        if path.is_symlink():
            raise AssertionError("IPA cannot contain symbolic links")
        if path.is_dir():
            continue
        if not path.is_file():
            raise AssertionError("Unexpected nonregular bundle entry")
        if any(part.startswith(".") for part in path.relative_to(app).parts):
            raise AssertionError("No hidden/developer metadata inside lab IPA")
        files.append(path)
    if not files or len(files) > MAX_FILES:
        raise AssertionError("Missing or unexpectedly large app payload")
    if sum(path.stat().st_size for path in files) > MAX_BYTES:
        raise AssertionError("Unexpectedly large app payload")
    return files


def inspect_app(app: Path) -> dict:
    files = _app_entries(app)
    plist = app / "Info.plist"
    executable = app / EXPECTED_EXECUTABLE
    if not plist.is_file() or not executable.is_file():
        raise AssertionError("Bundle missing Info.plist or ProtectionLab executable")
    with plist.open("rb") as handle:
        info = plistlib.load(handle)
    required = {
        "CFBundleIdentifier": EXPECTED_BUNDLE_ID,
        "CFBundleExecutable": EXPECTED_EXECUTABLE,
        "CFBundlePackageType": "APPL",
        "MinimumOSVersion": "15.0",
    }
    if any(info.get(key) != value for key, value in required.items()):
        raise AssertionError("Unexpected bundle identifier, platform, or executable")
    if info.get("CFBundleSupportedPlatforms") != ["iPhoneOS"]:
        raise AssertionError("Must target physical iPhoneOS")
    if info.get("UIDeviceFamily") != [1]:
        raise AssertionError("Expected iPhone-only app")
    if any(part == "_CodeSignature" for file in files
           for part in file.relative_to(app).parts):
        raise AssertionError("Unexpected preexisting code signing bundle")
    details = device_audit.inspect_executable(executable, "arm64")
    return {"details": details, "files": files, "identifier": info["CFBundleIdentifier"]}


def _zip_info(arcname: str, executable: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(arcname, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    return info


def verify_ipa(ipa: Path) -> dict:
    if not ipa.is_file():
        raise AssertionError("Missing IPA archive")
    with zipfile.ZipFile(ipa, "r") as archive:
        members = archive.infolist()
        names = [item.filename for item in members]
        if len(names) != len(set(names)):
            raise AssertionError("Duplicate IPA file entries")
        if len(names) < 2 or len(names) > MAX_FILES:
            raise AssertionError("Unexpected number of IPA entries")
        if any(not name.startswith(PAYLOAD_PREFIX) or
               name.endswith("/") or ".." in Path(name).parts or
               name.startswith("/") for name in names):
            raise AssertionError("IPA contains path outside the expected Payload")
        if PAYLOAD_PREFIX + EXPECTED_EXECUTABLE not in names or (
            PAYLOAD_PREFIX + "Info.plist" not in names
        ):
            raise AssertionError("Not a valid Payload/ProtectionLab.app layout")
        if sum(item.file_size for item in members) > MAX_BYTES:
            raise AssertionError("IPA exceeds size limit")
        for member in members:
            mode = member.external_attr >> 16
            if stat.S_IFMT(mode) != stat.S_IFREG:
                raise AssertionError("IPA entries must be regular files")
        if archive.testzip() is not None:
            raise AssertionError("Invalid ZIP checksum")
        data = archive.read(PAYLOAD_PREFIX + EXPECTED_EXECUTABLE)
        if len(data) < 32:
            raise AssertionError("Truncated Mach-O executable in IPA")
        magic, cputype, subtype, filetype = struct.unpack_from("<IIII", data)
        if (magic != device_audit.MAGIC or
                cputype != device_audit.ARM64_CPUTYPE or
                subtype & 0x00FFFFFF != 0 or
                filetype != device_audit.MH_EXECUTE):
            raise AssertionError("IPA must contain an arm64 MH_EXECUTE, never arm64e")
        parsed = plistlib.loads(archive.read(PAYLOAD_PREFIX + "Info.plist"))
        if parsed.get("CFBundleIdentifier") != EXPECTED_BUNDLE_ID:
            raise AssertionError("IPA Info.plist bundle identifier mismatch")
        mode = archive.getinfo(PAYLOAD_PREFIX + EXPECTED_EXECUTABLE).external_attr >> 16
        if not (mode & stat.S_IXUSR):
            raise AssertionError("App executable lacks executable permission")
        return {
            "schema": 1,
            "container": "IPA_ZIP",
            "payload_root": "Payload/ProtectionLab.app/",
            "architecture_expected": "arm64",
            "files": len(members),
            "binary_sha256": hashlib.sha256(data).hexdigest(),
            "ipa_sha256": hashlib.sha256(ipa.read_bytes()).hexdigest(),
            "trollstore_installation": "NOT_TESTED",
            "code_signing": "NOT_PERFORMED",
            "on_device_runtime": "NOT_TESTED",
            "arm64e_pac_runtime": "NOT_TESTED_A12_PLUS_REQUIRED",
        }


def package(app: Path, ipa: Path, report: Path) -> dict:
    checked = inspect_app(app)
    files = checked["files"]
    ipa.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ipa, "w") as archive:
        for path in files:
            target = PAYLOAD_PREFIX + path.relative_to(app).as_posix()
            archive.writestr(_zip_info(target, path.name == EXPECTED_EXECUTABLE),
                             path.read_bytes())
    result = verify_ipa(ipa)
    if result["binary_sha256"] != checked["details"]["sha256"]:
        raise AssertionError("Mach-O bytes changed inside IPA")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("PROTECTION_LAB_IPA_STRUCTURE_PASS: arm64, Payload/ProtectionLab.app, "
          "signing/install/device runtime NOT_TESTED")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--app", type=Path, required=True)
    p.add_argument("--ipa", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    package(args.app, args.ipa, args.report)


if __name__ == "__main__":
    main()
