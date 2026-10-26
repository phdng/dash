#!/usr/bin/env python3
"""K23 unsigned iOS lab packaging; detects corrupted BUNDLED K14 references only.

The trusted digest is compiled into the lab app from a K21-verified build,
not authenticated by an independent trust root. This is NOT self-integrity.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import plistlib
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kagura_k21"))
import opcode_inventory as k21  # noqa: E402

APP = "KaguraK23RuntimeLab"
BUNDLE = "com.duodash.research.kagurak23runtimelab"
PREFIX = f"Payload/{APP}.app/"
IPA = f"{APP}-TrollStore-arm64.ipa"
REPORT = "Kagura-K23-RUNTIME-REFERENCE-IPA-REPORT.json"
SCOPE = "K23_ISOLATED_BUNDLED_K14_CODE_REFERENCE_SHA256_RUNTIME_FUNCTIONALITY_NO_SELF_SECURITY"
REFERENCE = "KaguraCSEBreakLab.reference.b64"
# Keep Mach-O executable magic out of the on-device resource: installers
# must not see a nested executable to consider re-signing or rewriting it.
# This transport is NOT encryption, signing or a root of trust.
TRANSPORT_MAGIC = b"K23-BUNDLED-K14-REFERENCE-BASE64-V1\n"
EXPECTED_MEMBERS = {APP, "Info.plist", REFERENCE}
MAX_FILE = 32 * 1024 * 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_reference(data: bytes) -> bytes:
    if type(data) is not bytes or not (56 <= len(data) <= MAX_FILE):
        raise AssertionError("K23 reference Mach-O bytes missing/unbounded")
    return TRANSPORT_MAGIC + base64.b64encode(data) + b"\n"


def decode_reference(blob: bytes) -> bytes:
    if (type(blob) is not bytes or not blob.startswith(TRANSPORT_MAGIC) or
            not blob.endswith(b"\n") or len(blob) > 2 * MAX_FILE or
            blob.count(b"\n") != 2):
        raise AssertionError("K23 malformed/oversized opaque binary transport")
    try:
        decoded = base64.b64decode(blob[len(TRANSPORT_MAGIC):-1], validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise AssertionError("K23 base64 resource corrupt") from exc
    if not (56 <= len(decoded) <= MAX_FILE) or encode_reference(decoded) != blob:
        raise AssertionError("K23 noncanonical/corrupted reference transport")
    return decoded


def source(out: Path) -> tuple[bytes, dict, dict]:
    saved = k21.verify(out)  # complete K13/K14/K16/K19/K20/K21 replay.
    report = saved["specimens"]["ios_csebreak_lab"]
    target_path = out / "KaguraCSEBreakLab.app/KaguraCSEBreakLab"
    if not target_path.is_file() or target_path.is_symlink():
        raise AssertionError("K23 source K14 Mach-O missing")
    data = target_path.read_bytes()
    if sha(data) != report["binary_sha256"]:
        raise AssertionError("K23 source executable mismatches K21")
    targets = report["targets"]
    if set(targets) != {"_dd_k8_evaluate", "_dd_k14_ios_parity"}:
        raise AssertionError("K23 strict K14 symbol set required")
    for name, record in targets.items():
        off, length = record["file_offset"], record["size"]
        if (type(off) is not int or type(length) is not int or
                off < 0 or off % 4 or length < 4 or length % 4 or
                length > MAX_FILE or off > len(data) - length or
                sha(data[off:off + length]) != record["bytes_sha256"]):
            raise AssertionError("K23 bounded K14 code source mismatch " + name)
    return data, report, targets


def generated_expected(ref: dict, targets: dict, data: bytes) -> str:
    if not re.fullmatch(r"[0-9a-f-]{36}", ref["macho_uuid"]):
        raise AssertionError("K23 K14 UUID malformed")
    lines = [
        "// Generated from K21-verified linked K14 Mach-O; NOT an immutable trust root.",
        "import Foundation",
        "enum K23Expected {",
        f'    static let uuid = "{ref["macho_uuid"]}"',
        f'    static let fullSHA256 = "{ref["binary_sha256"]}"',
        f'    static let fileSize = {len(data)}',
        f'    static let transportSHA256 = "{sha(encode_reference(data))}"',
        f'    static let transportSize = {len(encode_reference(data))}',
        "    static let targetRanges: [(Int, Int, String)] = [",
    ]
    for key in sorted(targets):
        r = targets[key]
        lines.append(
            f'        ({r["file_offset"]}, {r["size"]}, "{r["bytes_sha256"]}"), // {key}')
    lines += ["    ]", "}", ""]
    return "\n".join(lines)


def prepare(out: Path) -> dict:
    data, ref, targets = source(out)
    app = out / f"{APP}.app"
    if app.exists() or app.is_symlink() or (out / "K23Expected.swift").exists():
        raise AssertionError("K23 refuses to overwrite app or generated Swift")
    app.mkdir()
    shutil.copyfile(HERE / "Info.plist", app / "Info.plist")
    (app / REFERENCE).write_bytes(encode_reference(data))
    (out / "K23Expected.swift").write_text(
        generated_expected(ref, targets, data), encoding="utf-8")
    return {"reference_binary_sha256": ref["binary_sha256"],
            "reference_uuid": ref["macho_uuid"]}


def info_check(data: bytes) -> None:
    v = plistlib.loads(data)
    for key, value in {
        "CFBundleExecutable": APP,
        "CFBundleIdentifier": BUNDLE,
        "CFBundleVersion": "2",
        "CFBundlePackageType": "APPL",
        "CFBundleSupportedPlatforms": ["iPhoneOS"],
        "MinimumOSVersion": "15.0",
        "UIDeviceFamily": [1],
        "LSRequiresIPhoneOS": True,
    }.items():
        if v.get(key) != value:
            raise AssertionError("K23 Info.plist field mismatch " + key)


def collect(out: Path) -> dict:
    data, ref, targets = source(out)
    app = out / f"{APP}.app"
    if not app.is_dir() or app.is_symlink() or (
        {p.name for p in app.iterdir()} != EXPECTED_MEMBERS):
        raise AssertionError("K23 app must contain exactly executable/plist/reference")
    for p in app.iterdir():
        if p.is_symlink() or not p.is_file() or not (0 < p.stat().st_size <= MAX_FILE):
            raise AssertionError("K23 unexpected/unbounded app member")
    info_check((app / "Info.plist").read_bytes())
    packed = (app / REFERENCE).read_bytes()
    actual = decode_reference(packed)
    if actual != data or sha(actual) != ref["binary_sha256"]:
        raise AssertionError("K23 transported K14 executable differs from K21 source")
    generated = out / "K23Expected.swift"
    if (not generated.is_file() or generated.is_symlink() or
            generated.read_text(encoding="utf-8") != generated_expected(ref, targets, data)):
        raise AssertionError("K23 compiled expected digests drifted from K21 source")
    program = k21.k20.k19.k16.inspect_macho((app / APP).read_bytes())
    if program["binary_sha256"] == ref["binary_sha256"]:
        raise AssertionError("K23 app executable incorrectly equals K14 reference")
    return {
        "schema": 1, "scope": SCOPE, "bundle_identifier": BUNDLE,
        "app_executable_uuid": program["uuid"],
        "app_executable_sha256": program["binary_sha256"],
        "reference_uuid": ref["macho_uuid"],
        "reference_binary_sha256": ref["binary_sha256"],
        "reference_transport_format": "BASE64_V1_INERT_RESOURCE_NOT_TRUST_ANCHOR",
        "reference_transport_sha256": sha(packed),
        "reference_transport_member": REFERENCE,
        "reference_target_region_sha256": {
            name: v["bytes_sha256"] for name, v in sorted(targets.items())},
        "bundled_reference_checked_at_packaging": True,
        "compiled_digests_not_immutable_trust_anchor": True,
        "runtime_reference_verifier_source_present": True,
        "iphone_runtime": "NOT_TESTED_BY_CI",
        "negative_tests_on_device": "NOT_TESTED_BY_CI",
        "running_app_self_integrity": False,
        "security_anti_tamper_proven": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "k18_dependency": False,
        "signing": "UNSIGNED",
    }


def zipinfo(name: str, executable: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    return info


def package(out: Path) -> dict:
    report = collect(out)
    ipa = out / IPA
    if ipa.exists() or ipa.is_symlink():
        raise AssertionError("K23 refuses to overwrite IPA")
    app = out / f"{APP}.app"
    with zipfile.ZipFile(ipa, "w") as z:
        for name in sorted(EXPECTED_MEMBERS):
            z.writestr(zipinfo(PREFIX + name, name == APP), (app / name).read_bytes())
    with zipfile.ZipFile(ipa) as z:
        members = z.infolist()
        if (len(members) != len(EXPECTED_MEMBERS) or
                {m.filename for m in members} !=
                {PREFIX + name for name in EXPECTED_MEMBERS} or
                z.testzip() is not None):
            raise AssertionError("K23 IPA malformed entries or CRC")
        for m in members:
            mode = m.external_attr >> 16
            if (m.file_size > MAX_FILE or stat.S_IFMT(mode) != stat.S_IFREG or
                    (m.filename == PREFIX + APP and not mode & stat.S_IXUSR)):
                raise AssertionError("K23 IPA invalid member permissions")
            if z.read(m.filename) != (app / m.filename.rsplit("/", 1)[-1]).read_bytes():
                raise AssertionError("K23 IPA reference byte drift")
    report["ipa_sha256"] = sha(ipa.read_bytes())
    (out / REPORT).write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("prepare", "package"))
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    result = prepare(a.out) if a.mode == "prepare" else package(a.out)
    print("K23_BUNDLED_REFERENCE_LAB_" + a.mode.upper() +
          "_PASS: iPhone runtime NOT_TESTED, self-integrity NOT_IMPLEMENTED")


if __name__ == "__main__":
    main()
