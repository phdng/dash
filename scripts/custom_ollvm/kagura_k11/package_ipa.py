#!/usr/bin/env python3
"""K11 standalone deterministic unsigned iOS arm64 IPA; no device claim."""
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

APP = "KaguraFiveLab"
BUNDLE = "com.duodash.research.kagurafivelab"
PREFIX = "Payload/KaguraFiveLab.app/"
MAX = 24 * 1024 * 1024

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def executable_uuid(raw: bytes) -> str:
    if not 56 <= len(raw) <= MAX:
        raise AssertionError("K11 malformed binary size")
    magic, cpu, sub, kind, count, sizecmds, _, _ = struct.unpack_from(
        "<IIIIIIII", raw)
    if (magic, cpu, sub, kind) != (0xfeedfacf, 0x0100000c, 0, 2):
        raise AssertionError("K11 expects real arm64 subtype0 MH_EXECUTE")
    if not (1 <= count <= 4096 and
            24 <= sizecmds <= (1 << 20) and 32 + sizecmds <= len(raw)):
        raise AssertionError("K11 MachO command bounds")
    pos, end, uuids = 32, 32 + sizecmds, []
    for _ in range(count):
        if end - pos < 8:
            raise AssertionError("K11 truncated load command")
        cmd, length = struct.unpack_from("<II", raw, pos)
        if length < 8 or length % 4 or length > end - pos:
            raise AssertionError("K11 invalid load command length")
        if cmd == 0x1b:
            if length != 24:
                raise AssertionError("K11 malformed LC_UUID")
            uuids.append(str(uuid.UUID(bytes=raw[pos + 8:pos + 24])))
        pos += length
    if pos != end or len(uuids) != 1:
        raise AssertionError("K11 missing/duplicate LC_UUID")
    return uuids[0]

def check_info(raw: bytes) -> None:
    info = plistlib.loads(raw)
    expected = {
        "CFBundleIdentifier": BUNDLE,
        "CFBundleExecutable": APP,
        "CFBundlePackageType": "APPL",
        "CFBundleSupportedPlatforms": ["iPhoneOS"],
        "MinimumOSVersion": "15.0",
        "UIDeviceFamily": [1],
        "LSRequiresIPhoneOS": True,
    }
    if any(info.get(k) != v for k, v in expected.items()):
        raise AssertionError("K11 bundle metadata invalid")

def check_app(app: Path) -> dict:
    if app.name != APP + ".app" or not app.is_dir() or app.is_symlink():
        raise AssertionError("K11 requires stand-alone app")
    children = list(app.iterdir())
    if {x.name for x in children} != {"Info.plist", APP} or any(
            not x.is_file() or x.is_symlink() for x in children):
        raise AssertionError("K11 rejects extra app resources/symlinks")
    check_info((app / "Info.plist").read_bytes())
    exe = (app / APP).read_bytes()
    return {"uuid": executable_uuid(exe), "binary_sha256": sha(exe)}

def zip_entry(name: str, executable: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    return info

def verify_ipa(ipa: Path) -> dict:
    with zipfile.ZipFile(ipa) as zf:
        infos = zf.infolist()
        if (len(infos) != 2 or
                {i.filename for i in infos} !=
                {PREFIX + APP, PREFIX + "Info.plist"} or
                zf.testzip() is not None):
            raise AssertionError("K11 IPA must contain only exact two files")
        for item in infos:
            mode = item.external_attr >> 16
            if (item.file_size > MAX or
                    stat.S_IFMT(mode) != stat.S_IFREG or
                    (item.filename.endswith("/" + APP) and
                     not mode & stat.S_IXUSR)):
                raise AssertionError("K11 IPA invalid permissions/type")
        check_info(zf.read(PREFIX + "Info.plist"))
        binary = zf.read(PREFIX + APP)
    return {
        "schema": 1,
        "scope": "STANDALONE_K11_FIVE_PASS_LAB_IPA",
        "bundle_identifier": BUNDLE,
        "architecture": "arm64",
        "filetype": "MH_EXECUTE",
        "macho_uuid": executable_uuid(binary),
        "binary_sha256": sha(binary),
        "ipa_sha256": sha(ipa.read_bytes()),
        "compiler_evidence": "Kagura-K11-IPA-EVIDENCE.json",
        "device_execution": "NOT_TESTED_BY_CI",
        "trollstore_import": "MANUAL_NOT_TESTED",
        "signed_by_ci": False,
        "arm64e_pac_runtime": "NOT_TESTED",
        "crane_production_modified": False,
        "security_attestation": False,
    }

def package(app: Path, ipa: Path, report: Path) -> dict:
    expected = check_app(app)
    ipa.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ipa, "w") as zf:
        for file in ("Info.plist", APP):
            zf.writestr(zip_entry(PREFIX + file, file == APP),
                        (app / file).read_bytes())
    result = verify_ipa(ipa)
    if (result["macho_uuid"] != expected["uuid"] or
            result["binary_sha256"] != expected["binary_sha256"]):
        raise AssertionError("K11 IPA embeds different binary than app")
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    return result

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("app", "ipa", "report"):
        p.add_argument("--" + name, type=Path, required=True)
    x = p.parse_args()
    package(x.app, x.ipa, x.report)
    print("K11_IPA_STRUCTURE_PASS: unsigned arm64 LC_UUID, device NOT TESTED")

if __name__ == "__main__":
    main()
