#!/usr/bin/env python3
"""Portable regression for REAL Kagura LLVM19 seven-pass iPhone arm64 IPA.

No host mock is claimed to be an iPhone runtime PASS. Packaging tests use
synthetic Mach-O headers solely to reject bad files and wrong ABIs.
"""
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
LAB = ROOT / "scripts/custom_ollvm/kagura_max"
sys.path.insert(0, str(LAB))
spec = importlib.util.spec_from_file_location("kagura_ipa", LAB / "package_ipa.py")
assert spec and spec.loader
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)
proof_spec = importlib.util.spec_from_file_location(
    "kagura_ios_proof", LAB / "ios_pipeline_audit.py"
)
assert proof_spec and proof_spec.loader
proof = importlib.util.module_from_spec(proof_spec)
proof_spec.loader.exec_module(proof)
report_spec = importlib.util.spec_from_file_location(
    "kagura_device_report", LAB / "ios_report_audit.py"
)
assert report_spec and report_spec.loader
report_audit = importlib.util.module_from_spec(report_spec)
report_spec.loader.exec_module(report_audit)

UUID_BYTES = bytes.fromhex("179f30eb1629365886fccd7da188a483")


def fake_macho(raw_subtype: int = 0, kind: int = 2) -> bytes:
    return (
        struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, raw_subtype,
                    kind, 1, 24, 0, 0)
        + struct.pack("<II", 0x1B, 24) + UUID_BYTES
        + b"public fixture, not a device binary"
    )


plist = plistlib.loads((LAB / "ios_app_Info.plist").read_bytes())
assert plist["CFBundleIdentifier"] == "com.duodash.research.kaguralab"
assert plist["CFBundleExecutable"] == "KaguraLab"
assert plist["MinimumOSVersion"] == "15.0"
assert plist["LSRequiresIPhoneOS"] is True
assert plist["CFBundleSupportedPlatforms"] == ["iPhoneOS"]
assert plist["UIDeviceFamily"] == [1]
assert "NSAppTransportSecurity" not in plist
assert "UIBackgroundModes" not in plist

with tempfile.TemporaryDirectory(prefix="Kagura device artifact ") as temp:
    root = Path(temp)
    app = root / "KaguraLab.app"
    app.mkdir()
    executable = app / "KaguraLab"
    executable.write_bytes(fake_macho())
    manifest = app / "Info.plist"
    manifest.write_bytes(plistlib.dumps(plist))
    ipa = root / "KaguraLab-TrollStore-arm64.ipa"
    report = root / "ipa-report.json"
    result = pack.package(app, ipa, report)
    assert result == json.loads(report.read_text(encoding="utf-8"))
    assert result["bundle_identifier"] == pack.BUNDLE_ID
    assert result["architecture"] == "arm64"
    assert result["filetype"] == "MH_EXECUTE"
    assert result["macho_uuid"] == "179f30eb-1629-3658-86fc-cd7da188a483"
    assert result["ios_device_execution"] == "NOT_TESTED_BY_CI"
    assert result["trollstore_installation"] == "NOT_TESTED_BY_CI"
    assert result["crane_production_changed"] is False
    assert result["arm64e_pac_runtime"] == "DEFERRED_NO_A12_DEVICE"
    assert result["compiler_provenance_verified_by_ipa_parser"] is False
    assert result["separate_compiler_evidence"] == "KaguraLab-seven-pass-evidence.json"
    assert result == pack.verify_ipa(ipa)
    with zipfile.ZipFile(ipa) as zf:
        assert set(zf.namelist()) == {
            "Payload/KaguraLab.app/Info.plist",
            "Payload/KaguraLab.app/KaguraLab",
        }
        binary = zf.getinfo("Payload/KaguraLab.app/KaguraLab")
        assert (binary.external_attr >> 16) & stat.S_IXUSR
        assert zf.read(binary) == executable.read_bytes()
    # Separate compiler trace audit: simulated Mach-O and pass logs verify
    # fail-closed provenance logic, NOT real Kagura compilation.
    candidate_obj = root / "protected.o"
    plain_obj = root / "plain.o"
    plain_obj.write_bytes(fake_macho(kind=1) +
        b"DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1")
    candidate_obj.write_bytes(fake_macho(kind=1) + b"kagura-encrypted")
    traces = root / "pass-traces"
    traces.mkdir()
    for step, class_name in proof.PASS_NAMES:
        (traces / f"pass-{step}.log").write_text(
            "Running pass: kagura::" + class_name +
            " on dd_kagura_protected\n", encoding="utf-8"
        )
    compiler_report = root / "seven-pass-evidence.json"
    provenance = proof.audit(plain=plain_obj, protected=candidate_obj,
                             app=executable, ipa=ipa, logs=traces,
                             output=compiler_report)
    assert provenance["passes_observed_count"] == 7
    assert all(x["pass_manager_invocation_observed"] is True
               for x in provenance["passes"])
    assert provenance["actual_device_execution"] == "NOT_TESTED_BY_CI"
    assert provenance["security_attestation"] is False
    assert len(provenance["protected_object_sha256"]) == 64

    def reject_proof(message: str):
        try:
            proof.audit(plain=plain_obj, protected=candidate_obj,
                        app=executable, ipa=ipa, logs=traces,
                        output=compiler_report)
        except (AssertionError, ValueError):
            return
        raise AssertionError("Malformed compiler evidence accepted: " + message)

    trace_file = traces / "pass-bbs.log"
    original_trace = trace_file.read_bytes()
    trace_file.write_bytes(b"Running pass: FakeUnrelatedPass on function\n")
    reject_proof("wrong LLVM pass name")
    trace_file.write_bytes(original_trace)
    trace_file.write_bytes(b"")
    reject_proof("empty real pass log")
    trace_file.write_bytes(original_trace)
    candidate_obj.write_bytes(fake_macho(kind=1) +
        b"DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1")
    reject_proof("candidate still plaintext")
    candidate_obj.write_bytes(fake_macho(raw_subtype=0x80000002, kind=1))
    reject_proof("incorrect object Mach-O subtype")
    candidate_obj.write_bytes(fake_macho(kind=1) + b"kagura-encrypted")

    # User-shared 7-line parity + optional 10-line benchmark protocol.
    # These are synthetic FORMAT fixtures, never iPhone evidence.
    parity_lines = [
        "DD_KAGURA_SCHEMA=1",
        "DD_KAGURA_CONTEXT=IOS_DEVICE",
        "DD_KAGURA_ARCH=arm64:0x00000000",
        "DD_KAGURA_PIPELINE=STR_FLA_BCF_SUB_CO_BBR_BBS",
        "DD_KAGURA_VECTORS_PASS=8192",
        "DD_KAGURA_CHECKSUM=0123456789abcdef",
        "DD_KAGURA_COMPLETE=PASS",
    ]
    bench_lines = [
        "DD_KAGURA_PERF_SCHEMA=1",
        "DD_KAGURA_PERF_CONTEXT=IOS_DEVICE",
        "DD_KAGURA_PERF_ARCH=arm64:0x00000000",
        "DD_KAGURA_PERF_PAIRS=5",
        "DD_KAGURA_PERF_CALLS_PER_SAMPLE=4096",
        "DD_KAGURA_PERF_PLAIN_MEDIAN_NS=25",
        "DD_KAGURA_PERF_PROTECTED_MEDIAN_NS=125",
        "DD_KAGURA_PERF_CHECKSUM=1111111111111111",
        "DD_KAGURA_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION",
        "DD_KAGURA_PERF_COMPLETE=PASS",
    ]
    device_log = root / "user-text.txt"
    device_log.write_text("\n".join(parity_lines) + "\n", encoding="utf-8")
    parsed = report_audit.validate(device_log)
    assert parsed["claimed_parity_vectors"] == 8192
    assert parsed["optional_benchmark"] is None
    assert parsed["device_execution_cryptographically_attested"] is False
    device_log.write_text(
        "\n".join(parity_lines) + "\n\n" + "\n".join(bench_lines) + "\n",
        encoding="utf-8"
    )
    parsed = report_audit.validate(device_log)
    assert parsed["optional_benchmark"]["ratio_vs_plain"] == 5.0
    assert parsed["optional_benchmark"]["observational_only"] is True

    def reject_shared_report(raw: str):
        device_log.write_text(raw, encoding="utf-8")
        try:
            report_audit.validate(device_log)
        except (AssertionError, ValueError):
            return
        raise AssertionError("Malformed user-shared device report was accepted")

    valid_report = "\n".join(parity_lines) + "\n"
    reject_shared_report(valid_report.replace("IOS_DEVICE", "MACOS_HOST"))
    reject_shared_report(valid_report.replace("arm64:0x00000000", "arm64e:0x80000002"))
    reject_shared_report(valid_report.replace("VECTORS_PASS=8192", "VECTORS_PASS=4096"))
    reject_shared_report(valid_report.replace("COMPLETE=PASS", "COMPLETE=FAIL"))
    reject_shared_report(valid_report + "UDID=DO_NOT_RECORD\n")
    reject_shared_report(valid_report.rstrip("\n"))  # incomplete newline
    reject_shared_report(valid_report.replace("0123456789abcdef", "invalid"))
    reject_shared_report(
        "\n".join(parity_lines) + "\n\n" +
        "\n".join(bench_lines).replace("PROTECTED_MEDIAN_NS=125",
                                     "PROTECTED_MEDIAN_NS=0") + "\n"
    )

    original_zip = ipa.read_bytes()
    pack.package(app, ipa, report)
    assert ipa.read_bytes() == original_zip, "Kagura IPA must be deterministic"

    def reject_package():
        try:
            pack.package(app, ipa, report)
        except (AssertionError, ValueError):
            return
        raise AssertionError("Rejected Kagura IPA input unexpectedly accepted")

    executable.write_bytes(fake_macho(raw_subtype=0x80000002))
    reject_package()  # never package AppleClang arm64e as arm64
    executable.write_bytes(fake_macho(raw_subtype=2))
    reject_package()
    executable.write_bytes(fake_macho(kind=6))
    reject_package()  # dynamic library cannot be a launchable IPA
    executable.write_bytes(fake_macho())
    info = plist.copy()
    info["CFBundleIdentifier"] = "com.duodash.research.protectionlab"
    manifest.write_bytes(plistlib.dumps(info))
    reject_package()
    info["CFBundleIdentifier"] = pack.BUNDLE_ID
    manifest.write_bytes(plistlib.dumps(info))
    (app / "_CodeSignature").mkdir()
    reject_package()
    (app / "_CodeSignature").rmdir()

    unsafe = root / "bad-kagura.ipa"
    with zipfile.ZipFile(unsafe, "w") as zf:
        for name in pack.FILES:
            zf.writestr(pack.zip_entry(pack.PREFIX + name, name == "KaguraLab"),
                        (app / name).read_bytes())
        zf.writestr("../../escaped.txt", "bad")
    try:
        pack.verify_ipa(unsafe)
    except AssertionError:
        pass
    else:
        raise AssertionError("IPA path traversal accepted")

source = (LAB / "critical.c").read_text(encoding="utf-8")
app_src = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
runtime = (LAB / "ios_canary.c").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/kagura-max-candidate.yml").read_text(
    encoding="utf-8"
)
for phrase in (
    "#ifndef DD_KAGURA_ENTRY",
    "#define DD_KAGURA_ENTRY dd_kagura_critical",
    "uint64_t DD_KAGURA_ENTRY(",
):
    assert phrase in source
for phrase in (
    "UIApplicationMain(argc, argv",
    "DDIsPhysicalArm64()",
    "Run 8192 Kagura vectors",
    "Measure Kagura overhead (optional)",
    "Share Kagura test logs",
    "dd_kagura_ios_parity(buffer, sizeof(buffer))",
    "dd_kagura_ios_benchmark(buffer, sizeof(buffer))",
    "hasSuffix:@\"DD_KAGURA_COMPLETE=PASS\\n\"",
    "self.perfButton.enabled = NO",
    "self.perfButton.enabled = passed",
    "dispatch_get_global_queue",
    "dispatch_get_main_queue",
    "UIActivityViewController",
    "TARGET_OS_SIMULATOR",
    "__arm64e__",
    "_dyld_get_image_header(0)",
):
    assert phrase in app_src, phrase
for phrase in (
    "extern uint64_t dd_kagura_plain(",
    "extern uint64_t dd_kagura_protected(",
    "DD_KAGURA_VECTORS = 8192",
    "DD_KAGURA_PIPELINE=STR_FLA_BCF_SUB_CO_BBR_BBS",
    "DD_KAGURA_CONTEXT=IOS_DEVICE",
    "DD_KAGURA_ARCH=arm64:0x00000000",
    "DD_KAGURA_VECTORS_PASS=8192",
    "DD_KAGURA_COMPLETE=PASS",
    "DD_KAGURA_ERROR=MISMATCH_AT_",
    "DD_KAGURA_PERF_CONTEXT=IOS_DEVICE",
    "DD_KAGURA_PERF_PAIRS=5",
    "DD_KAGURA_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION",
):
    assert phrase in runtime, phrase
for name in ("objc_msgSend(", "MSHook", "ptrauth_strip",
             "task_for_pid", "mprotect(", "dlopen(", "syscall(",
             "identifierForVendor", "NSUserDefaults"):
    assert name not in runtime, name
for name in ("MSHook", "MobileSubstrate", "ptrauth_strip",
             "task_for_pid", "mprotect(", "dlopen(",
             "identifierForVendor", "NSUserDefaults"):
    assert name not in app_src, name

for required in (
    "workflow_dispatch:",
    "python3 scripts/test_kagura_ios_ipa.py",
    "Build standalone Kagura arm64 UIKit IPA with actual seven LLVM passes",
    '-DDD_KAGURA_ENTRY=dd_kagura_"$variant"',
    "for pass in str fla bcf sub co bbr bbs; do",
    '-passes="$pipeline"',
    "xcrun nm -gU",
    "KaguraLab-TrollStore-arm64.ipa",
    "package_ipa.py",
    "ios_pipeline_audit.py",
    "KaguraLab-seven-pass-evidence.json",
    "KaguraLab-TrollStore-report.json",
    "arm64e: Apple Clang build/audit ONLY",
    "actions/upload-artifact@v4",
):
    assert required in workflow, required
assert "for variant in plain protected; do" in workflow
assert "KAGURA_LLVM" in workflow and "--load-pass-plugin=" in workflow
assert "xcrun clang -target arm64-apple-ios15.0" in workflow
for forbidden in (
    "make clean package", "ldid -S", "codesign -s", "DEVELOPMENT_TEAM=",
    "devicectl device install", "PAC_STRIP", "lipo -create",
):
    assert forbidden.lower() not in workflow.lower()
# Dedicated manual IPA workflow must not depend on K3 host benchmark;
# users can build KaguraLab IPA without repeating 128 host processes.
standalone = (ROOT / ".github/workflows/kagura-ios-ipa.yml").read_text(
    encoding="utf-8"
)
build_script = (LAB / "build_ipa.sh").read_text(encoding="utf-8")
for required in (
    "workflow_dispatch:",
    "runs-on: macos-14",
    "python3 scripts/test_kagura_ios_ipa.py",
    "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
    "https://github.com/qusamulab/kagura.git",
    "brew install llvm@19",
    "bash scripts/custom_ollvm/kagura_max/build_ipa.sh",
    "KaguraLab-TrollStore-arm64-LLVM19-SEVEN-PASSES",
    "AppleClang-arm64e-BUILD-ONLY.dylib",
    "0x80000002",
    "arm64e-build-only-uuid.txt",
):
    assert required in standalone, required
for required in (
    "-DDD_KAGURA_ENTRY=dd_kagura_",
    "for pass in str fla bcf sub co bbr bbs; do",
    '-passes="$pipeline"',
    "ios_canary.c",
    "ios_app_main.m",
    "package_ipa.py",
    "ios_pipeline_audit.py",
    "KaguraLab-seven-pass-evidence.json",
    "KaguraLab-TrollStore-arm64.ipa",
):
    assert required in build_script, required
assert "kagura-k3-host-interleaved" not in standalone
assert "interleaved_benchmark.py" not in standalone
for source_text in (workflow, standalone, build_script):
    for forbidden in (
        "make clean package", "ldid -S", "codesign -s",
        "DEVELOPMENT_TEAM=", "devicectl device install", "PAC_STRIP",
        "lipo -create", "ptrauth_strip",
    ):
        assert forbidden.lower() not in source_text.lower(), forbidden
assert "KaguraLab" not in (ROOT / "Makefile").read_text(encoding="utf-8")
assert "KaguraLab" not in (
    ROOT / ".github/workflows/protection-ios-app.yml"
).read_text(encoding="utf-8")

print("KAGURA_IOS_IPA_PORTABLE_PASS: separate arm64 UI, two real LLVM19 "
      "object entrypoints, seven opt stages, payload ABI/UUID/hash and "
      "malformed-IPA negatives; physical iPhone NOT YET TESTED")
