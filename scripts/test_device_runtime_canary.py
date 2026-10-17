#!/usr/bin/env python3
"""Portable guard for isolated iOS runtime harness and strict MH_EXECUTE gating."""
from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))
spec = importlib.util.spec_from_file_location("device_audit", LAB / "device_audit.py")
assert spec.loader is not None
aud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aud)


def fixture(raw_subtype: int, filetype: int = aud.MH_EXECUTE,
            cputype: int = aud.ARM64_CPUTYPE) -> bytes:
    return (struct.pack("<IIIIIIII", aud.MAGIC, cputype, raw_subtype,
                        filetype, 0, 0, 0, 0) + b"isolated-device-canary-only")


with tempfile.TemporaryDirectory() as scratch:
    root = Path(scratch)
    a, e = root / "arm64", root / "arm64e"
    a.write_bytes(fixture(0))
    e.write_bytes(fixture(0x80000002))
    report = aud.build_report(a, e, root / "build-report.json")
    assert json.loads((root / "build-report.json").read_text(encoding="utf-8")) == report
    assert report["arm64e"]["cpu_subtype_raw"] == "0x80000002"
    assert report["arm64"]["filetype"] == "MH_EXECUTE"
    assert report["iOS_pac_runtime"] == "NOT_TESTED_A12_PLUS_REQUIRED"
    assert report["ios_on_device_runtime"] == "NOT_TESTED"
    assert report["automatic_device_installation"] is False

    for malformed in (
        fixture(1), fixture(2), fixture(0), fixture(0x40000002),
        fixture(0xc0000002), fixture(0x80000002, filetype=6),
        fixture(0x80000002, cputype=7), b"invalid",
    ):
        e.write_bytes(malformed)
        try:
            aud.inspect_executable(e, "arm64e")
        except AssertionError:
            pass
        else:
            raise AssertionError("Rejected arm64e invalid ABI/object was accepted")
    e.write_bytes(fixture(0x80000002))
    for malformed in (fixture(2), fixture(1), fixture(0x80000002),
                      fixture(0, filetype=6), b""):
        a.write_bytes(malformed)
        try:
            aud.inspect_executable(a, "arm64")
        except AssertionError:
            pass
        else:
            raise AssertionError("Rejected arm64 invalid ABI/object was accepted")
    a.write_bytes(fixture(0))

    host = root / "host-runtime.log"
    host.write_text("\n".join(aud.expected_lines("MACOS_HOST")) + "\n", encoding="utf-8")
    host_report = aud.verify_run_log(host, "MACOS_HOST")
    assert host_report["context_from_log"] == "MACOS_HOST"
    assert host_report["validated_stages"] == list(aud.STAGES)
    assert host_report["vector_count_per_stage"] == 8192
    assert host_report["attestation"].startswith("USER_SUPPLIED_")

    ios = root / "ios-runtime.log"
    for arch in ("arm64", "arm64e"):
        expected = aud.expected_lines("IOS_DEVICE", arch)
        assert len(expected) == 7
        ios.write_bytes(("\r\n".join(expected) + "\r\n").encode("utf-8"))
        result = aud.verify_run_log(ios, "IOS_DEVICE", arch)
        assert result["reported_architecture"] == arch
        try:
            aud.verify_run_log(ios, "IOS_DEVICE",
                               "arm64" if arch == "arm64e" else "arm64e")
        except AssertionError:
            pass
        else:
            raise AssertionError("Wrong iOS architecture log accepted")

        bad_logs = [
            expected[:-1],                       # missing final completion
            expected[:2] + expected[3:],          # missing VM
            expected + [expected[-1]],           # duplicated pass
            ["DD_RUNTIME_CONTEXT=MACOS_HOST"] + expected[1:],
            expected[:3] + ["DD_RUNTIME_VM_PASS=8192"] + expected[3:],
            expected[:4] + ["DD_RUNTIME_IGV_IBR_PASS=1"] + expected[5:],
            expected[:6] + ["DD_RUNTIME_COMPLETE=FAIL"],
            expected + ["DD_RUNTIME_ERROR=HIDDEN"],  # extra text
        ]
        for lines in bad_logs:
            ios.write_text("\n".join(lines) + "\n", encoding="utf-8")
            try:
                aud.verify_run_log(ios, "IOS_DEVICE", arch)
            except AssertionError:
                pass
            else:
                raise AssertionError("Forged/partial iOS runtime log accepted")

    for malformed in ("DD_RUNTIME_CONTEXT=IOS_DEVICE\n", ""):
        host.write_text(malformed, encoding="utf-8")
        try:
            aud.verify_run_log(host, "MACOS_HOST")
        except AssertionError:
            pass
        else:
            raise AssertionError("Bad host log accepted")

main = (LAB / "device_main.m").read_text(encoding="utf-8")
suites = (LAB / "device_suites.c").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/protection-device-runtime.yml").read_text(
    encoding="utf-8"
)
for name in ("dd_device_test_vm", "dd_device_test_ce_icall", "dd_device_test_igv_ibr"):
    assert name in main and name in suites
for name in ("DDObjCPlainValue", "DDObjCProtectedValue", "isEqualToString:",
             "lengthOfBytesUsingEncoding:", "@autoreleasepool"):
    assert name in main
for name in ("_dyld_get_image_header(0)", "__arm64e__", "TARGET_OS_IPHONE",
             "MH_MAGIC_64", "CPU_TYPE_ARM64", "ARM64E_PAC_ABI_MISMATCH",
             "DD_RUNTIME_CONTEXT=IOS_DEVICE", "DD_RUNTIME_COMPLETE=PASS"):
    assert name in main
assert "DD_DEVICE_VECTORS = 8192" in (LAB / "device_suites.h").read_text(encoding="utf-8")
assert "DD_RUNTIME_ERROR=CE_ICALL" in suites
assert "DD_RUNTIME_ERROR=VM" in suites
assert "DD_RUNTIME_ERROR=IGV_IBR" in suites
assert "make clean package" not in workflow and "TARGET_CC=" not in workflow
assert "xcrun --sdk iphoneos --find clang" in workflow
assert "for arch in arm64 arm64e; do" in workflow
assert 'python3 "$lab/device_audit.py" build' in workflow
assert 'python3 "$lab/device_audit.py" verify-host' in workflow
assert "device_main.m" not in workflow or "device_main" in workflow
assert "objc_ce_generator.py" in workflow
assert "sllvm_generator.py" in workflow and "program.py" in workflow
assert "xcrun clang -fobjc-arc" in workflow and "xcrun clang -std=c11" in workflow
assert "Device-specific signing/provisioning/install: NOT PERFORMED" in workflow
assert "actions/upload-artifact@v4" in workflow
assert "workflow_dispatch:" in workflow and "runs-on: macos-14" in workflow
assert "NOT TESTED" in workflow and "test_objc_ce_pilot.py" in workflow
for prohibited in ("brew install", "ldid -S", "ssh ", "scp ", "dpkg ",
                   "fpass-plugin", "vmprotect", "security import"):
    assert prohibited not in workflow.lower(), prohibited

print("Device runtime harness: strict 2-slice MH_EXECUTE, host/iOS "
      "4-suite log validation, negative vectors and CI isolation PASS")
