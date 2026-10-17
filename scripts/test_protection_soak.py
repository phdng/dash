#!/usr/bin/env python3
"""Portable regression for five-round on-device stability / soak testing.

No physical iPhone or runtime log is fabricated as a user result.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))
spec = importlib.util.spec_from_file_location("soak_audit", LAB / "soak_audit.py")
assert spec and spec.loader
soak = importlib.util.module_from_spec(spec)
spec.loader.exec_module(soak)

assert soak.ROUNDS == 5
assert soak.VECTORS == 8192
assert soak.STAGES == ("VM", "CE_ICALL", "IGV_IBR", "OBJC_CE")
assert soak.TOTAL_VECTOR_CHECKS == 163840
assert len(soak.expected_lines("arm64")) == 12

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    logfile = root / "soak.txt"
    for arch in ("arm64", "arm64e"):
        lines = soak.expected_lines(arch)
        logfile.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        report = soak.validate(logfile, arch)
        assert report["rounds"] == 5
        assert report["reported_total_vector_checks"] == 163840
        assert report["result"] == "REPORTED_FIVE_ROUND_PASS"
        assert report["device_execution_attested"] is False
        assert report["source"] == "USER_SHARED_TEXT_NOT_CRYPTOGRAPHICALLY_AUTHENTICATED"
        assert report["production_crane_verified"] is False
        assert len(report["log_sha256"]) == 64

        try:
            soak.validate(logfile, "arm64e" if arch == "arm64" else "arm64")
        except AssertionError:
            pass
        else:
            raise AssertionError("Wrong reported ABI accepted")

        for pos in range(len(lines)):
            shorter = lines.copy()
            del shorter[pos]
            logfile.write_text("\n".join(shorter) + "\n", encoding="utf-8")
            try:
                soak.validate(logfile, arch)
            except AssertionError:
                pass
            else:
                raise AssertionError(f"Missing soak field accepted: {pos}")

    original = soak.expected_lines("arm64")
    invalid = [
        original + [original[-1]],
        original[:-1] + ["DD_SOAK_COMPLETE=FAIL"],
        original[:5] + ["DD_SOAK_VM_ROUNDS_PASS=4"] + original[6:],
        original[:3] + ["DD_SOAK_ROUNDS=999"] + original[4:],
        original[:4] + ["DD_SOAK_VECTORS_PER_SUITE_PER_ROUND=1024"] + original[5:],
        original[:9] + ["DD_SOAK_TOTAL_VECTOR_CHECKS=32768"] + original[10:],
        original[:10] + ["DD_SOAK_NOTE=DEVICE_ATTESTED"] + original[11:],
        ["DD_SOAK_CONTEXT=MACOS_HOST"] + original[1:],
        original[:6] + original[7:8] + original[6:7] + original[8:],
        original + ["DD_EVIDENCE_DEVICE_ID=private"],
        ["DD_SOAK_ERROR=OBJC_CE:ROUND_3"],
    ]
    for index, lines in enumerate(invalid):
        logfile.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            soak.validate(logfile, "arm64")
        except AssertionError:
            pass
        else:
            raise AssertionError(f"Malformed soak report {index} accepted")
    logfile.write_text("x" * 2049, encoding="utf-8")
    try:
        soak.validate(logfile, "arm64")
    except AssertionError:
        pass
    else:
        raise AssertionError("Oversized soak report accepted")

source = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(encoding="utf-8")

# Exactly four real suite calls run inside one bounded outer round loop.
body = source.split("static NSString *DDRunSoak(", 1)[1].split(
    "static NSString *DDRunPerformance(", 1
)[0]
assert "enum { DD_SOAK_ROUNDS = 5 }" in source
assert "round < DD_SOAK_ROUNDS" in body
assert "@autoreleasepool" in body
for name in ("dd_device_test_vm()", "dd_device_test_ce_icall()",
             "dd_device_test_igv_ibr()", "DDNSStringParity()"):
    assert body.count("if (!" + name) == 1, name
for part in ("VM", "CE_ICALL", "IGV_IBR", "OBJC_CE"):
    assert f"DD_SOAK_ERROR={part}:ROUND_%u" in body
    assert f"DD_SOAK_{part}_ROUNDS_PASS=5" in body
assert body.index("DD_SOAK_ERROR=VM:ROUND_%u") < body.index("DD_SOAK_ERROR=CE_ICALL:ROUND_%u")
assert body.index("DD_SOAK_ERROR=CE_ICALL:ROUND_%u") < body.index("DD_SOAK_ERROR=IGV_IBR:ROUND_%u")
assert body.index("DD_SOAK_ERROR=IGV_IBR:ROUND_%u") < body.index("DD_SOAK_ERROR=OBJC_CE:ROUND_%u")
assert body.index("DD_SOAK_ERROR=OBJC_CE:ROUND_%u") < body.index("DD_SOAK_COMPLETE=PASS")

for literal in (
    'DD_SOAK_SCHEMA=1\\n',
    'DD_SOAK_CONTEXT=IOS_DEVICE\\n',
    'DD_SOAK_ROUNDS=5\\n',
    'DD_SOAK_VECTORS_PER_SUITE_PER_ROUND=8192\\n',
    'DD_SOAK_TOTAL_VECTOR_CHECKS=163840\\n',
    'DD_SOAK_NOTE=MANUAL_STRESS_NOT_SECURITY_ATTESTATION\\n',
    'DD_SOAK_COMPLETE=PASS\\n',
):
    assert literal in body, literal
assert "DD_SOAK_COMPLETE=PASS\\\\n" not in body  # no literal backslash+n!

# A bounded manual button, guarded by a successful regular four-suite run.
ui = source.split("@implementation DDProtectionLabViewController", 1)[1]
for expected in (
    'Run stability test (5 rounds)',
    '@selector(startSoak)',
    'self.soakButton.enabled = NO;',
    'self.soakButton.enabled = passed;',
    'if (self.running || !self.soakButton.enabled ||',
    '!DDValidationPassed(self.report)) return;',
    'NSString *result = DDRunSoak(abi,',
    'BOOL passed = [result hasSuffix:@"DD_SOAK_COMPLETE=PASS\\n"];',
    'Share stability/soak result',
    'presentShareWithText:self.soakReport',
    'Runtime: PASS (4/4) · Soak: PASS (5/5)',
    'Runtime: PASS (4/4) · Soak: FAILED / INCOMPLETE',
    'dispatch_get_main_queue()',
):
    assert expected in ui, expected
assert "self.soakReport = nil;" in ui
assert "self.benchmarkButton.enabled = YES;" in ui
assert "self.soakButton.enabled = YES;" in ui
assert "self.report = result;" in ui
assert "self.soakReport = result;" in ui
assert "No user data" in source
for forbidden in ("NSUserDefaults", "identifierForVendor", "sysctlbyname",
                  "serialNumber", "task_for_pid", "mprotect("):
    assert forbidden not in source, forbidden

assert "python3 scripts/test_protection_soak.py" in workflow
assert "package_trollstore_ipa.py" in workflow
assert "for arch in arm64 arm64e; do" in workflow
assert "build_gate.py" in workflow
assert "CODE_SIGNING_ALLOWED=NO build" in workflow

print("Protection Soak: 5x4x8192 vector accounting, 12-line strict parser, "
      "malformed/wrong-ABI checks, opt-in UI and CI isolation PASS")
