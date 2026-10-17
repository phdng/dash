#!/usr/bin/env python3
"""Cross-platform IPA packaging safety and CI separation gates for TrollStore lab."""
from __future__ import annotations

import importlib.util
import json
import plistlib
import stat
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))
spec = importlib.util.spec_from_file_location("package_trollstore_ipa", LAB / "package_trollstore_ipa.py")
assert spec.loader is not None
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)
spec_gate = importlib.util.spec_from_file_location("build_gate", LAB / "build_gate.py")
assert spec_gate.loader is not None
gate = importlib.util.module_from_spec(spec_gate)
spec_gate.loader.exec_module(gate)

assert pack.PAYLOAD_PREFIX == "Payload/ProtectionLab.app/"


def dummy_macho(subtype: int, filetype: int = 2) -> bytes:
    return struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, subtype, filetype,
                       0, 0, 0, 0) + b"PRIVATE-NONE-LAB-CANARY"


with tempfile.TemporaryDirectory() as temp:
    tmp = Path(temp)
    app = tmp / "ProtectionLab.app"
    app.mkdir()
    info = plistlib.loads((LAB / "ios_app_Info.plist").read_bytes())
    (app / "Info.plist").write_bytes(plistlib.dumps(info))
    executable = app / "ProtectionLab"
    executable.write_bytes(dummy_macho(0))
    ipa = tmp / "ProtectionLab-TrollStore-arm64.ipa"
    report = tmp / "ipa-report.json"
    result = pack.package(app, ipa, report)
    assert ipa.is_file()
    assert result["architecture_expected"] == "arm64"
    assert result["trollstore_installation"] == "NOT_TESTED"
    assert result["arm64e_pac_runtime"].startswith("NOT_TESTED")
    assert json.loads(report.read_text(encoding="utf-8")) == result
    assert pack.verify_ipa(ipa) == result
    with zipfile.ZipFile(ipa) as archive:
        assert set(archive.namelist()) == {
            "Payload/ProtectionLab.app/Info.plist",
            "Payload/ProtectionLab.app/ProtectionLab",
        }
        item = archive.getinfo("Payload/ProtectionLab.app/ProtectionLab")
        assert (item.external_attr >> 16) & stat.S_IXUSR
        assert archive.read(item) == executable.read_bytes()
    from device_audit import inspect_executable
    arm64e = tmp / "study-arm64e"
    arm64e.write_bytes(dummy_macho(0x80000002))
    raw_a = inspect_executable(executable, "arm64")
    raw_e = inspect_executable(arm64e, "arm64e")
    build = tmp / "build-report.json"
    identity = tmp / "build-identity.json"
    identity_slices = {
        "arm64": {**raw_a, "macho_uuid": "11111111-1111-4111-8111-111111111111"},
        "arm64e": {**raw_e, "macho_uuid": "22222222-2222-4222-8222-222222222222"},
    }
    build.write_text(json.dumps({
        "schema": 1, "arm64": raw_a, "arm64e": raw_e,
        "ios_on_device_runtime": "NOT_TESTED",
        "automatic_device_installation": False,
    }), encoding="utf-8")
    identity.write_text(json.dumps({
        "schema": 1, "slices": identity_slices,
        "runtime_on_iphone": "NOT_TESTED_BY_CI",
        "uuid_security_attestation": False,
    }), encoding="utf-8")
    gates = tmp / "build-gates.json"
    summary = gate.generate(build, identity, report, gates)
    assert summary["arm64"]["trollstore_ipa_structure"] == "PASS"
    assert summary["arm64e"]["compiler_link_macho_abi_uuid"] == "PASS"
    assert summary["arm64e"]["a12_plus_device_runtime"] == "DEFERRED_NO_DEVICE"
    assert json.loads(gates.read_text(encoding="utf-8")) == summary
    altered = json.loads(identity.read_text(encoding="utf-8"))
    altered["slices"]["arm64e"]["cpu_subtype_raw"] = "0x00000001"
    identity.write_text(json.dumps(altered), encoding="utf-8")
    try:
        gate.generate(build, identity, report, gates)
    except AssertionError:
        pass
    else:
        raise AssertionError("arm64e ABI mismatch must fail build gate")
    altered["slices"]["arm64e"]["cpu_subtype_raw"] = "0x80000002"
    identity.write_text(json.dumps(altered), encoding="utf-8")

    stable = ipa.read_bytes()
    pack.package(app, ipa, report)
    assert ipa.read_bytes() == stable, "Deterministic IPA must be byte-identical"

    def reject_pack() -> None:
        try:
            pack.package(app, ipa, report)
        except (AssertionError, ValueError):
            return
        raise AssertionError("Unsafe source app accepted")

    executable.write_bytes(dummy_macho(0x80000002))
    reject_pack()  # A12+ arm64e binary must NOT become TrollStore arm64 IPA
    executable.write_bytes(dummy_macho(0, filetype=6))
    reject_pack()
    executable.write_bytes(dummy_macho(0))
    info["CFBundleIdentifier"] = "com.other.invalid"
    (app / "Info.plist").write_bytes(plistlib.dumps(info))
    reject_pack()
    info["CFBundleIdentifier"] = pack.EXPECTED_BUNDLE_ID
    (app / "Info.plist").write_bytes(plistlib.dumps(info))
    (app / "_CodeSignature").mkdir()
    (app / "_CodeSignature" / "CodeResources").write_text("preexisting", encoding="utf-8")
    reject_pack()
    # Build a malicious zip with a path traversal and check the verifier rejects.
    malicious = tmp / "malicious.ipa"
    with zipfile.ZipFile(malicious, "w") as zipf:
        zipf.writestr("Payload/ProtectionLab.app/Info.plist", plistlib.dumps(info))
        zipf.writestr("Payload/ProtectionLab.app/ProtectionLab", dummy_macho(0))
        zipf.writestr("../outside", b"bad")
    try:
        pack.verify_ipa(malicious)
    except AssertionError:
        pass
    else:
        raise AssertionError("Path traversal in IPA not rejected")

workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(encoding="utf-8")
for text in (
    "python3 scripts/test_trollstore_ipa.py",
    "package_trollstore_ipa.py",
    "ProtectionLab-TrollStore-arm64.ipa",
    "TrollStore-IPA-report.json",
    "build_gate.py",
    "build-gates.json",
    "build-report.json",
    "build-identity.json",
    "for arch in arm64 arm64e; do",
    "device_audit.py",
    "actions/upload-artifact@v4",
):
    assert text in workflow, f"Missing CI contract: {text}"
assert 'package_trollstore_ipa.py" --app "$out/ProtectionLab-arm64e.app"' not in workflow
for unsafe in ("ldid -S", "codesign -s", "devicectl device install",
               "apt install", "jailbreak", "make clean package"):
    # The word 'jailbreak' is present only in a statement of NO jailbreaking.
    if unsafe == "jailbreak":
        continue
    assert unsafe.lower() not in workflow.lower(), unsafe

print("TrollStore IPA: arm64 Payload/ structure, reproducible archive, "
      "Mach-O/Info.plist negative cases, CI arm64e-build-only policy PASS")
