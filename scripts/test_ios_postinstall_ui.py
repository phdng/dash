#!/usr/bin/env python3
"""Post-install Protection Lab UIKit safety and truthful progress regression.

App opening does not imply that four suites passed. This checks the live
Objective-C source protocol and the exact PASS predicate (including newline)
that controls the identity report and optional benchmark.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
source = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(encoding="utf-8")
sys.path.insert(0, str(LAB))

# Source uses a SINGLE escaped newline as a valid ObjC string-literal suffix.
# A double escaped backslash emits backslash+'n' at runtime and silently
# suppresses the identity share report even after the four suites PASS.
match = re.search(
    r"static BOOL DDValidationPassed\(NSString \*result\) \{\s*"
    r"return \[result hasSuffix:(@\"(?:[^\"\\]|\\.)*\")\];\s*\}",
    source,
)
assert match is not None, "Missing canonical PASS predicate"
suffix_literal = match.group(1)
assert suffix_literal == r'@"DD_RUNTIME_COMPLETE=PASS\n"', (
    "Expected one C escape for newline; double escape would disable identity export"
)
assert r'@"DD_RUNTIME_COMPLETE=PASS\\n"' not in source
assert source.count("DD_RUNTIME_COMPLETE=PASS") == 2
assert source.count("BOOL passed = DDValidationPassed(result);") == 1
assert "NSString *identity = passed ? DDRunEvidence(DDRuntimeABI()) : nil;" in source
assert "self.evidenceReport = identity;" in source
assert "self.benchmarkButton.enabled = passed;" in source
assert "if (self.running || !self.benchmarkButton.enabled ||" in source
assert "!DDValidationPassed(self.report)) return;" in source

# Progress tracks actual per-suite invocation on the worker, while every
# UIKit label mutation is dispatched to the main thread.
validation = source.split("static NSString *DDRunValidation(", 1)[1].split(
    "static NSString *DDRunPerformance(", 1
)[0]
assert "void (^progress)(NSString *)" in source
stages = (
    ("Testing VM (1/4)", "dd_device_test_vm()"),
    ("Testing CE/ICALL (2/4)", "dd_device_test_ce_icall()"),
    ("Testing IGV/IBR (3/4)", "dd_device_test_igv_ibr()"),
    ("Testing Objective-C/ARC (4/4)", "DDNSStringParity()"),
)
indexes = []
for message, call in stages:
    msg_pos = validation.index('progress(@"' + message + '")')
    fn_pos = validation.index("if (!" + call)
    assert msg_pos < fn_pos, (message, call)
    indexes.append(msg_pos)
assert indexes == sorted(indexes)
assert "DD_RUNTIME_ERROR=ARCH_OR_PAC_ABI_MISMATCH" in validation
assert validation.index("DD_RUNTIME_ERROR=OBJC_CE") < validation.index(
    'DD_RUNTIME_COMPLETE=PASS'
)
for required in (
    'App launched · Runtime: NOT TESTED',
    'Runtime: RUNNING (0/4)',
    'Runtime: PASS (4/4)',
    'Runtime: FAILED / INCOMPLETE — see report',
    'Runtime: PASS (4/4) · Benchmark: RUNNING',
    'Runtime: PASS (4/4) · Benchmark: RECORDED',
    'Runtime: PASS (4/4) · Benchmark: FAILED',
    'UILabel *runtimeStatusLabel',
    'self.runtimeStatusLabel.text = stage',
    'dispatch_get_main_queue()',
    'self.shareButton.enabled = YES',
    'Share binary identity / OS model',
    'presentShareWithText:self.evidenceReport',
    'presentShareWithText:self.performanceReport',
    'presentShareWithText:self.report',
):
    assert required in source, required
assert source.index("self.runtimeStatusLabel.text = stage") > source.index(
    "dispatch_get_main_queue()"
)
assert source.index("self.runtimeStatusLabel.text = result ?") > source.index(
    "- (void)startBenchmark"
)
assert 'self.benchmarkButton.enabled = NO;' in source

# The parity and identity reports retain exact original 7-line shape.
import device_audit
import device_evidence
for arch in ("arm64", "arm64e"):
    lines = device_audit.expected_lines("IOS_DEVICE", arch)
    assert len(lines) == 7
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        parity = root / "parity.txt"
        parity.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
        proof = device_audit.verify_run_log(parity, "IOS_DEVICE", arch)
        assert proof["vector_count_per_stage"] == 8192

assert "python3 scripts/test_ios_postinstall_ui.py" in workflow
assert "package_trollstore_ipa.py" in workflow
assert "build_gate.py" in workflow
assert "for arch in arm64 arm64e; do" in workflow
assert "CODE_SIGNING_ALLOWED=NO build" in workflow
for forbidden in ("devicectl device install", "ldid -S", "codesign -s",
                  "task_for_pid", "mprotect(", "MSHookFunction"):
    assert forbidden.lower() not in workflow.lower()
print("Post-install UIKit: real 4-stage progress, exact newline PASS "
      "predicate, identity export, separated sharing and arm64e build-only PASS")
