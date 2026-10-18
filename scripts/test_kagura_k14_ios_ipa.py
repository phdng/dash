#!/usr/bin/env python3
"""K14 portable IPA/UUID/device-log negative gates, not native iPhone proof."""
from __future__ import annotations
import hashlib
import json
import plistlib
import re
import stat
import struct
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_k14"
sys.path.insert(0, str(LAB))
import package_ipa as pkg
import device_log_audit as dev
import ipa_evidence as evidence


def rejects(fn, reason):
    try:
        fn()
    except (AssertionError, ValueError, UnicodeError, KeyError, OSError):
        return
    raise AssertionError("K14 fake positive accepted: " + reason)


TEST_UUID = "6ee048f1-8e5a-46ff-b8de-bc6947ec21e6"
def macho(*, subtype=0, kind=2, uuid_count=1):
    uuids = struct.pack("<II", 0x1B, 24) + uuid.UUID(TEST_UUID).bytes
    commands = uuids * uuid_count
    return (struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C,
                        subtype, kind, uuid_count, len(commands), 0, 0) +
            commands + b"synthetic K14 binary used only for portable tests")


info = plistlib.loads((LAB / "Info.plist").read_bytes())
assert info["CFBundleExecutable"] == pkg.APP == "KaguraCSEBreakLab"
assert info["CFBundleIdentifier"] == pkg.BUNDLE == (
    "com.duodash.research.kaguracsebreaklab")
assert info["MinimumOSVersion"] == "15.0"
assert info["UIDeviceFamily"] == [1]
assert pkg.BUNDLE not in {
    "com.duodash.research.kagurafivelab",
    "com.duodash.research.kaguravmlab",
    "com.duodash.research.kaguralab",
}
assert pkg.executable_uuid(macho()) == TEST_UUID
rejects(lambda: pkg.executable_uuid(macho(kind=1)),
        "object falsely marked executable")
rejects(lambda: pkg.executable_uuid(macho(subtype=0x80000002)),
        "arm64e falsely marked arm64")
rejects(lambda: pkg.executable_uuid(macho(uuid_count=2)),
        "duplicate LC_UUID")
rejects(lambda: pkg.executable_uuid(macho(uuid_count=0)),
        "missing LC_UUID")
rejects(lambda: pkg.executable_uuid(macho()[:41]), "truncated load command")
assert evidence.check_nm(
    "0000000000000000 T _dd_k8_evaluate\n"
    "0000000000000001 T _dd_k14_ios_parity\n"
    "0000000000000002 T _main\n") == evidence.EXPORTED
rejects(lambda: evidence.check_nm(
    "0000000000000000 T _dd_k8_evaluate\n"
    "0000000000000002 T _main\n"), "protected parity symbol missing")
rejects(lambda: evidence.check_nm(
    "0000000000000000 T _dd_k8_evaluate\n"
    "0000000000000002 U _main\n"
    "0000000000000001 T _dd_k14_ios_parity\n"),
    "undefined main classified as definition")

with tempfile.TemporaryDirectory(prefix="K14-synthetic-IPA-") as temp:
    out = Path(temp)
    app = out / (pkg.APP + ".app")
    app.mkdir()
    (app / "Info.plist").write_bytes((LAB / "Info.plist").read_bytes())
    (app / pkg.APP).write_bytes(macho())
    ipa = out / "lab.ipa"
    report = out / "report.json"
    got = pkg.package(app, ipa, report)
    assert got == pkg.verify_ipa(ipa)
    assert got["app_macho_uuid"] == TEST_UUID
    assert got["signing"] == "UNSIGNED"
    assert got["ios_device_execution"] == "NOT_TESTED_BY_CI"
    binary_original = ipa.read_bytes()
    pkg.package(app, ipa, report)
    assert ipa.read_bytes() == binary_original, "K14 deterministic IPA drift"
    with zipfile.ZipFile(ipa) as zf:
        assert {i.filename for i in zf.infolist()} == {
            pkg.PREFIX + "Info.plist", pkg.PREFIX + pkg.APP}
    (app / pkg.APP).write_bytes(macho(subtype=0x80000002))
    rejects(lambda: pkg.package(app, ipa, report), "arm64e masquerading iPhone")
    (app / pkg.APP).write_bytes(macho())
    metadata = dict(info)
    metadata["CFBundleIdentifier"] = "com.duodash.research.kagurafivelab"
    (app / "Info.plist").write_bytes(plistlib.dumps(metadata))
    rejects(lambda: pkg.package(app, ipa, report), "K11 bundle namespace collision")
    (app / "Info.plist").write_bytes((LAB / "Info.plist").read_bytes())
    (app / "_CodeSignature").mkdir()
    rejects(lambda: pkg.package(app, ipa, report), "forged IPA signature dir")
    (app / "_CodeSignature").rmdir()
    pkg.package(app, ipa, report)
    with zipfile.ZipFile(ipa, "a") as zf:
        zf.writestr("Payload/Evil.app/Evil", b"bad")
    rejects(lambda: pkg.verify_ipa(ipa), "extra IPA executable")
    pkg.package(app, ipa, report)

    evidence_file = out / "Kagura-K14-IPA-EVIDENCE.json"
    manifest = {
        "schema": 1,
        "scope": evidence.SCOPE,
        "app_macho_uuid": TEST_UUID,
        "ipa_sha256": got["ipa_sha256"],
        "app_binary_sha256": got["binary_sha256"],
        "k13_cse_break_ios_object_embedded": True,
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "security_attestation": False,
    }
    evidence_file.write_text(json.dumps(manifest), encoding="utf-8")
    log = out / "device-8-line.log"
    raw = (
        "DD_K14_IOS_SCHEMA=1\n"
        "DD_K14_IOS_CONTEXT=IOS_DEVICE\n"
        "DD_K14_IOS_ARCH=arm64:0x00000000\n"
        "DD_K14_IOS_APP_UUID=" + TEST_UUID + "\n"
        "DD_K14_IOS_PASS=CSE_BREAK\n"
        "DD_K14_IOS_VECTORS=4096\n"
        "DD_K14_IOS_CHECKSUM=25a3318e3d7d6525\n"
        "DD_K14_IOS_COMPLETE=PASS\n"
    )
    log.write_bytes(raw.encode("ascii"))
    checked = dev.validate(log, report, evidence_file)
    assert checked["ci_build_correlation"]["claimed_uuid_matches_ipa"] is True
    assert checked["device_execution_cryptographically_attested"] is False
    for why, bad in [
        ("UUID mismatch", raw.replace(TEST_UUID,
                                     "00000000-0000-0000-0000-000000000000")),
        ("wrong pass", raw.replace("CSE_BREAK", "CSE_BREAK_AND_PAC")),
        ("wrong checksum", raw.replace("25a3318e3d7d6525", "0" * 16)),
        ("wrong count", raw.replace("=4096", "=4095")),
        ("simulator fake", raw.replace("IOS_DEVICE", "IOS_SIMULATOR")),
        ("arm64e fake", raw.replace("arm64:0x00000000", "arm64e:0x80000002")),
        ("extra PASS line", raw + "K14_FAKE=PASS\n"),
        ("missing newline", raw[:-1]),
    ]:
        log.write_bytes(bad.encode("ascii"))
        rejects(lambda: dev.validate(log, report, evidence_file), why)
    log.write_bytes(raw.encode("ascii"))
    fake = dict(manifest)
    fake["k13_cse_break_ios_object_embedded"] = False
    evidence_file.write_text(json.dumps(fake), encoding="utf-8")
    rejects(lambda: dev.validate(log, report, evidence_file),
            "faked protected object provenance")
    evidence_file.write_text(json.dumps(manifest), encoding="utf-8")
    fake_pack = dict(got)
    fake_pack["binary_sha256"] = "0" * 64
    other = out / "wrong-report.json"
    other.write_text(json.dumps(fake_pack), encoding="utf-8")
    rejects(lambda: dev.validate(log, other, evidence_file),
            "mismatched embedded IPA SHA manifest")

for required in (
    'DD_K14_IOS_SCHEMA=1\\n', 'DD_K14_IOS_CONTEXT=IOS_DEVICE\\n',
    'DD_K14_IOS_ARCH=arm64:0x00000000\\n',
    'DD_K14_IOS_PASS=CSE_BREAK\\n',
    'DD_K14_IOS_VECTORS=4096\\n',
    'DD_K14_IOS_COMPLETE=PASS\\n',
    'UINT64_C(0x25a3318e3d7d6525)',
    'dd_k8_evaluate(', 'for (unsigned i = 0; i < 4096U',
):
    assert required in (LAB / "ios_probe.c").read_text(encoding="utf-8"), required
ui = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
assert "DDK14UUID()" in ui and "_dyld_get_image_header(0)" in ui
assert "dd_k14_ios_parity" in ui and "DDK14Controller" in ui
assert "TARGET_OS_SIMULATOR" in ui and "__arm64e__" in ui
build = (LAB / "build_ipa.sh").read_text(encoding="utf-8")
wf = (ROOT / ".github/workflows/kagura-k14-cse-break-ios-ipa.yml").read_text(
    encoding="utf-8")
for token in (
    "workflow_dispatch:", "runs-on: macos-14",
    "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
    "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa",
    "scripts/test_kagura_k14_ios_ipa.py",
    "scripts/custom_ollvm/kagura_k13/pilot.py",
    "scripts/custom_ollvm/kagura_k13/audit.py",
    "scripts/custom_ollvm/kagura_k14/build_ipa.sh",
    "DuoDash-Kagura-K14-CSEBREAK-IOS-ARM64-IPA-EXPERIMENTAL",
    "if: always()",
):
    assert token in wf, token
assert '"$out/ios-cse-break.o"' in build
assert '"$out/ios-app-main.o" "$out/ios-probe.o"' in build
assert "-framework Foundation -framework UIKit" in build
assert "ios-kagura-rtld.o" not in build
assert "05-ci/ios.o" not in build
for forbidden in ("devicectl device install", "codesign -s",
                  "ptrauth_strip", "MSHook", "git push"):
    assert forbidden not in wf + build + ui
for p in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k14" not in (ROOT / p).read_text(encoding="utf-8")
print("KAGURA_K14_PORTABLE_IPA_PASS: distinct bundle, arm64 UUID/SHA,"
      " strict K13 object/link provenance, eight-line device log negative"
      " gates; REAL macOS/iPhone K14 IPA NOT_TESTED")
