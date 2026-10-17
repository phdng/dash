#!/usr/bin/env python3
"""K7 iOS VM IPA portable fail-closed tests, all synthetic, never iPhone PASS."""
from __future__ import annotations

import json
import plistlib
import stat
import struct
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_vm"
sys.path.insert(0, str(LAB))
import audit
import ipa_evidence
import ios_device_log_audit as device_log
import package_ipa as package
from oracle import checksums

UUID = "179f30eb-1629-3658-86fc-cd7da188a483"
UUID_BYTES = uuid.UUID(UUID).bytes


def macho(*, subtype: int = 0, kind: int = 2) -> bytes:
    return (struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, subtype,
                        kind, 1, 24, 0, 0) +
            struct.pack("<II", 0x1B, 24) + UUID_BYTES +
            b"synthetic only, not native iOS execution")


def reject(call, reason):
    try:
        call()
    except (AssertionError, ValueError, KeyError, UnicodeError):
        return
    raise AssertionError("Accepted malformed K7 synthetic fixture: " + reason)


plist = plistlib.loads((LAB / "ios_app_Info.plist").read_bytes())
assert plist["CFBundleIdentifier"] == "com.duodash.research.kaguravmlab"
assert plist["CFBundleIdentifier"] not in ("com.duodash.research.kaguralab",
                                           "com.duodash.research.protectionlab")
assert plist["CFBundleExecutable"] == package.APP
assert plist["MinimumOSVersion"] == "15.0"
assert plist["UIDeviceFamily"] == [1]
assert "UIBackgroundModes" not in plist and "NSAppTransportSecurity" not in plist

with tempfile.TemporaryDirectory(prefix="synthetic K7 IPA ") as folder:
    root = Path(folder)
    app = root / "KaguraVMLab.app"
    app.mkdir()
    exe = app / "KaguraVMLab"
    exe.write_bytes(macho())
    manifest = app / "Info.plist"
    manifest.write_bytes(plistlib.dumps(plist))
    ipa = root / "vm.ipa"
    rep = root / "ipa.json"
    verified = package.package(app, ipa, rep)
    assert verified == package.verify_ipa(ipa)
    assert verified["macho_uuid"] == UUID
    assert verified["device_execution"] == "NOT_TESTED_BY_CI"
    assert verified["scope"] == "STANDALONE_K7_VM_IPA"
    original = ipa.read_bytes()
    package.package(app, ipa, rep)
    assert ipa.read_bytes() == original, "K7 IPA not deterministic"
    with zipfile.ZipFile(ipa) as zf:
        assert set(zf.namelist()) == {
            "Payload/KaguraVMLab.app/Info.plist",
            "Payload/KaguraVMLab.app/KaguraVMLab"
        }
        assert (zf.getinfo("Payload/KaguraVMLab.app/KaguraVMLab")
                .external_attr >> 16) & stat.S_IXUSR

    exe.write_bytes(macho(subtype=0x80000002))
    reject(lambda: package.package(app, ipa, rep), "arm64e-as-arm64")
    exe.write_bytes(macho(kind=6))
    reject(lambda: package.package(app, ipa, rep), "MH_DYLIB-as-app")
    exe.write_bytes(macho())
    badplist = plist.copy()
    badplist["CFBundleIdentifier"] = "com.duodash.research.kaguralab"
    manifest.write_bytes(plistlib.dumps(badplist))
    reject(lambda: package.package(app, ipa, rep), "K5 collision")
    manifest.write_bytes(plistlib.dumps(plist))
    (app / "_CodeSignature").mkdir()
    reject(lambda: package.package(app, ipa, rep), "extra signed resources")
    (app / "_CodeSignature").rmdir()

    baseline = root / "ios-plain.ll"
    vm = root / "ios-vm.ll"
    trace = root / "ios-vm-opt.log"
    plain_obj = root / "plain.o"
    vm_obj = root / "vm.o"
    interpreter = root / "vm-runtime.o"
    sym = root / "symbols.txt"
    k6_path = root / "k6.json"
    evidence = root / "k7.json"
    guard_body = "entry:\n  %a = xor i64 %x, %salt\n  ret i64 %a\n"
    baseline.write_text(
        "define i64 @dd_vm_plain(i64 %x, i64 %salt) {\n"
        "entry:\n  %a = add i64 %x, %salt\n  ret i64 %a\n}\n"
        "define i64 @dd_vm_guard_plain(i64 %x, i64 %salt) {\n" +
        guard_body + "}\n", encoding="utf-8")
    vm.write_text(
        "@kagura_vm_bc_44 = private constant [1 x i8] c\"A\"\n"
        "@kagura_vm_key_44 = private constant i64 11\n"
        "declare i64 @kagura_vm_execute(ptr, i32, ptr, i32, ptr, i32, i64)\n"
        "define i64 @dd_vm_protected(i64 %x, i64 %salt) {\n"
        "entry:\n"
        "  %a = call i64 @kagura_vm_execute(ptr null, i32 1, "
        "ptr null, i32 2, ptr null, i32 0, i64 11)\n"
        "  ret i64 %a\n}\n"
        "define i64 @dd_vm_guard_protected(i64 %x, i64 %salt) {\n" +
        guard_body + "}\n", encoding="utf-8")
    trace.write_text("Running pass: kagura::VMObfuscationPass "
                     "on dd_vm_protected (19 instructions)\n", encoding="utf-8")
    for f in (plain_obj, vm_obj, interpreter):
        f.write_bytes(macho(kind=1))
    syms = ("_dd_vm_plain", "_dd_vm_protected", "_dd_vm_guard_plain",
            "_dd_vm_guard_protected", "_kagura_vm_execute")
    sym.write_text("".join("0000000000001000 T " + x + "\n" for x in syms),
                   encoding="utf-8")
    parity, guard = checksums()
    k6 = {
        "schema": 1, "profile": "K6_VM_SELECTIVE_EXPERIMENTAL",
        "upstream_commit": "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
        "true_vm_trampoline_observed": True, "vm_bytecode_blob_observed": True,
        "native_guard_body_unchanged": True, "security_attestation": False,
        "production_crane_modified": False,
        "ios_arm64_build_only": {"device_execution": "NOT_TESTED"},
        "inputs_sha256": {
            "ios_vm_ir": audit.sha(vm),
            "ios_vm_trace": audit.sha(trace),
        },
        "macos": {
            "parity_vectors": 4096, "baseline_parity_checksum": parity,
            "unprotected_guard_checksum": guard,
        },
    }
    k6_path.write_text(json.dumps(k6), encoding="utf-8")
    args = dict(
        ipa=ipa, ipa_report=rep, k6_report=k6_path,
        ios_plain_ir=baseline, ios_vm_ir=vm, ios_vm_trace=trace,
        symbols=sym, ios_vm_obj=vm_obj, ios_plain_obj=plain_obj,
        vm_interpreter_obj=interpreter, output=evidence
    )
    proof = ipa_evidence.inspect(**args)
    assert proof["app_macho_uuid"] == UUID
    assert proof["ipa_sha256"] == verified["ipa_sha256"]
    assert proof["security_attestation"] is False
    assert proof["actual_ios_device_execution"] == "NOT_TESTED_BY_CI"
    old = vm.read_text(encoding="utf-8")
    vm.write_text(old.replace("kagura_vm_bc_", "no_vm_"), encoding="utf-8")
    reject(lambda: ipa_evidence.inspect(**args), "false VM blob")
    vm.write_text(old, encoding="utf-8")
    old = sym.read_text(encoding="utf-8")
    sym.write_text(old.replace("_kagura_vm_execute", "_no_vm"), encoding="utf-8")
    reject(lambda: ipa_evidence.inspect(**args), "VM runtime symbol missing")
    sym.write_text(old, encoding="utf-8")
    badk6 = k6.copy()
    badk6["true_vm_trampoline_observed"] = False
    k6_path.write_text(json.dumps(badk6), encoding="utf-8")
    reject(lambda: ipa_evidence.inspect(**args), "K6 real VM not proved")
    k6_path.write_text(json.dumps(k6), encoding="utf-8")
    badrep = root / "wrong-ipa-report.json"
    wrong = verified.copy()
    wrong["ipa_sha256"] = "0" * 64
    badrep.write_text(json.dumps(wrong), encoding="utf-8")
    reject(lambda: ipa_evidence.inspect(**(args | {"ipa_report": badrep})),
           "K7 fake IPA SHA")

    log = root / "device-text.log"
    line = [
        "DD_VM_IOS_SCHEMA=1", "DD_VM_IOS_CONTEXT=IOS_DEVICE",
        "DD_VM_IOS_ARCH=arm64:0x00000000",
        "DD_VM_IOS_APP_UUID=" + UUID,
        "DD_VM_IOS_PIPELINE=KAGURA_VM_SELECTIVE",
        "DD_VM_IOS_VECTORS_PASS=4096",
        "DD_VM_IOS_PARITY_CHECKSUM=" + parity,
        "DD_VM_IOS_GUARD_CHECKSUM=" + guard,
        "DD_VM_IOS_COMPLETE=PASS",
    ]
    perf = [
        "DD_VM_IOS_PERF_SCHEMA=1", "DD_VM_IOS_PERF_CONTEXT=IOS_DEVICE",
        "DD_VM_IOS_PERF_ARCH=arm64:0x00000000",
        "DD_VM_IOS_PERF_APP_UUID=" + UUID,
        "DD_VM_IOS_PERF_PAIRS=3",
        "DD_VM_IOS_PERF_CALLS_PER_SAMPLE=1024",
        "DD_VM_IOS_PERF_PLAIN_NS_0=3",
        "DD_VM_IOS_PERF_PROTECTED_NS_0=111",
        "DD_VM_IOS_PERF_PLAIN_NS_1=4",
        "DD_VM_IOS_PERF_PROTECTED_NS_1=110",
        "DD_VM_IOS_PERF_PLAIN_NS_2=3",
        "DD_VM_IOS_PERF_PROTECTED_NS_2=112",
        "DD_VM_IOS_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION",
        "DD_VM_IOS_PERF_COMPLETE=PASS",
    ]
    raw = "\n".join(line) + "\n\n" + "\n".join(perf) + "\n"
    log.write_text(raw, encoding="ascii")
    parsed = device_log.validate(log, ipa_report=rep, evidence=evidence)
    assert parsed["ci_build_correlation"]["claimed_uuid_matches_ipa_evidence"]
    assert parsed["cryptographic_device_attestation"] is False
    assert parsed["optional_benchmark"]["pairs_ns_per_call"][0] == [3, 111]
    def badlog(text: str):
        log.write_text(text, encoding="ascii")
        reject(lambda: device_log.validate(log), "device text")
    badlog(raw.replace("DD_VM_IOS_CONTEXT=IOS_DEVICE",
                       "DD_VM_IOS_CONTEXT=MACOS_HOST"))
    badlog(raw.replace(parity, "0000000000000000"))
    badlog(raw.replace("DD_VM_IOS_PERF_APP_UUID=" + UUID,
                       "DD_VM_IOS_PERF_APP_UUID=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
    badlog(raw[:-1])
    log.write_text(raw, encoding="ascii")
    reject(lambda: device_log.validate(log, ipa_report=badrep,
                                       evidence=evidence), "CI mismatch")

workflow = (ROOT / ".github/workflows/kagura-vm-ios-ipa.yml").read_text(
    encoding="utf-8")
build = (LAB / "build_ios_ipa.sh").read_text(encoding="utf-8")
app_source = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
probe = (LAB / "ios_probe.c").read_text(encoding="utf-8")
for required in (
    "workflow_dispatch:", "runs-on: macos-14",
    "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
    "python3 scripts/test_kagura_vm_ios_ipa.py",
    "bash scripts/custom_ollvm/kagura_vm/build.sh",
    "bash scripts/custom_ollvm/kagura_vm/build_ios_ipa.sh",
    "KaguraVMLab-K7-TrollStore-arm64-REAL-LLVM19-VM-EXPERIMENTAL",
):
    assert required in workflow, required
for required in (
    "-DDD_VM_ENTRY=dd_vm_plain", "ios-vm.o", "ios-vm-interpreter.o",
    "ios-plain.o", "ios_app_main.m", "ios_probe.c",
    "package_ipa.py", "ipa_evidence.py", "Kagura-K7-IPA-EVIDENCE.json",
):
    assert required in build, required
for required in (
    "UIApplicationMain(argc, argv", "DDVMExecutableUUID", "LC_UUID",
    "dd_vm_ios_parity(buffer, sizeof(buffer), uuid.UTF8String)",
    "dd_vm_ios_benchmark(buffer, sizeof(buffer), uuid.UTF8String)",
    "UIActivityViewController", "TARGET_OS_SIMULATOR", "__arm64e__",
    "dispatch_get_global_queue", "dispatch_get_main_queue",
):
    assert required in app_source, required
for required in (
    "DD_VM_IOS_APP_UUID=%s", "DD_VM_IOS_PERF_APP_UUID=%s",
    "DD_VM_IOS_VECTORS_PASS=4096", "DD_VM_IOS_COMPLETE=PASS",
    "0x9625f13d712f59c3", "0x09d9d53ddf189ce7",
    "DD_VM_IOS_PERF_PAIRS=3", "DD_VM_IOS_PERF_COMPLETE=PASS",
):
    assert required in probe, required
for source in (workflow, build, app_source, probe):
    for forbidden in ("devicectl device install", "codesign -s", "ldid -S",
                      "re/RECONSTRUCTION", "MSHook", "ptrauth_strip",
                      "THEOS_PACKAGE_SCHEME", "identifierForVendor"):
        assert forbidden not in source, forbidden
assert "KaguraVMLab" not in (ROOT / "Makefile").read_text(encoding="utf-8")
assert "kagura-vm" not in (ROOT / ".github/workflows/build.yml").read_text(
    encoding="utf-8")
print("KAGURA_K7_IPA_PORTABLE_PASS: synthetic IPA/UUID/VM evidence/log "
      "negative cases and manual CI isolation; real IPA and iPhone NOT YET TESTED")
