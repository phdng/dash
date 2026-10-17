#!/usr/bin/env python3
"""Strict observation-only performance log parser and source/CI safety guards."""
from __future__ import annotations

import importlib.util
import json
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))
spec = importlib.util.spec_from_file_location("perf_audit", LAB / "perf_audit.py")
assert spec.loader is not None
perf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(perf)


def sample(context: str, arch: str | None = None,
           timings: list[int] | None = None) -> list[str]:
    values = timings if timings is not None else [
        100000, 310000, 80000, 90000, 130000, 135000,
        115000, 119000, 405000, 605000,
    ]
    assert len(values) == 10
    lines = perf.expected_prefix(context, arch)
    for pos, pair in enumerate(perf.PAIRS):
        lines += [
            f"DD_PERF_{pair}_NATIVE_NS={values[2 * pos]}",
            f"DD_PERF_{pair}_PROTECTED_NS={values[2 * pos + 1]}",
        ]
    lines.append("DD_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_PROOF")
    return lines


assert perf.ITERATIONS == 20000 and perf.REPEATS == 5
assert perf.PAIRS == ("VM", "CE", "ICALL", "IGV", "IBR")
with tempfile.TemporaryDirectory() as folder:
    temp = Path(folder)
    log = temp / "perf-log.txt"
    for context, arch in (("MACOS_HOST", None),
                          ("IOS_DEVICE", "arm64"),
                          ("IOS_DEVICE", "arm64e")):
        lines = sample(context, arch)
        log.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
        output = perf.verify(log, context, arch)
        assert output["context_claimed"] == context
        assert output["architecture_claimed"] == arch
        assert list(output["measurements"]) == list(perf.PAIRS)
        assert output["measurements"]["VM"]["observed_ratio_not_an_acceptance_gate"] == 3.1
        assert output["performance_gate"] == "NONE"
        assert output["ios_device_runtime_verified"] is False
        assert output["attestation"].endswith("PROVENANCE_NOT_AUTHENTICATED")
        if context == "IOS_DEVICE":
            try:
                perf.verify(log, "IOS_DEVICE", "arm64" if arch == "arm64e" else "arm64e")
            except AssertionError:
                pass
            else:
                raise AssertionError("Wrong iOS ABI was accepted")
        else:
            try:
                perf.verify(log, "IOS_DEVICE", "arm64")
            except AssertionError:
                pass
            else:
                raise AssertionError("Mac host performance used as iOS result")

    original = sample("IOS_DEVICE", "arm64e")
    # Exhaustively remove any of the 17 lines; no partial log must pass.
    for idx in range(len(original)):
        bad = original.copy()
        del bad[idx]
        log.write_text("\n".join(bad) + "\n", encoding="utf-8")
        try:
            perf.verify(log, "IOS_DEVICE", "arm64e")
        except AssertionError:
            pass
        else:
            raise AssertionError(f"Missing log line {idx} accepted")
    variants = [
        original + [original[-1]],
        ["DD_PERF_CONTEXT=MACOS_HOST"] + original[1:],
        original[:6] + original[7:9] + original[6:7] + original[9:],
        original[:6] + ["DD_PERF_VM_NATIVE_NS=0"] + original[7:],
        original[:6] + ["DD_PERF_VM_NATIVE_NS=-1"] + original[7:],
        original[:6] + ["DD_PERF_VM_NATIVE_NS=NaN"] + original[7:],
        original[:6] + ["DD_PERF_VM_NATIVE_NS=00001"] + original[7:],
        original[:6] + ["DD_PERF_VM_NATIVE_NS=9223372036854775808"] + original[7:],
        original[:7] + ["DD_PERF_VM_PROTECTED_NS=1.1"] + original[8:],
        original[:5] + ["DD_PERF_ESTIMATOR=MIN_ELAPSED_NS"] + original[6:],
        original[:-1] + ["DD_PERF_NOTE=DEVICE_ATTESTED"],
        original[:4] + ["DD_PERF_REPEATS=1"] + original[5:],
    ]
    for index, values in enumerate(variants):
        log.write_text("\n".join(values) + "\n", encoding="utf-8")
        try:
            perf.verify(log, "IOS_DEVICE", "arm64e")
        except AssertionError:
            pass
        else:
            raise AssertionError(f"Malformed performance log {index} accepted")

    rng = random.Random(42216)
    for _ in range(1000):
        times = [rng.randint(1, 10_000_000_000) for _ in range(10)]
        lines = sample("IOS_DEVICE", "arm64", times)
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = perf.verify(log, "IOS_DEVICE", "arm64")
        assert result["measurements"]["IBR"]["protected_elapsed_ns"] == times[-1]

src = (LAB / "perf_pilot.c").read_text(encoding="utf-8")
header = (LAB / "perf_pilot.h").read_text(encoding="utf-8")
report = (LAB / "perf_report.c").read_text(encoding="utf-8")
host_runner = (LAB / "perf_host_runner.c").read_text(encoding="utf-8")
ui = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(encoding="utf-8")
for required in (
    "clock_gettime(CLOCK_MONOTONIC", "dd_perf_sink ^=", "dd_median(",
    "dd_perf_plain_fns[DD_PERF_PAIRS]", "dd_perf_protected_fns[DD_PERF_PAIRS]",
    "rep & 1U", "dd_measure(", "dd_perf_run(",
):
    assert required in src, required
for required in ("DD_PERF_ITERATIONS = 20000", "DD_PERF_REPEATS = 5",
                 "DD_PERF_PAIRS = 5"):
    assert required in header
for pair in perf.PAIRS:
    assert f"DD_PERF_{pair}_NATIVE_NS=" in report
    assert f"DD_PERF_{pair}_PROTECTED_NS=" in report
assert "OBSERVATIONAL_NOT_SECURITY_PROOF" in report
assert "MACOS_HOST" in host_runner and "NOT_APPLICABLE" in host_runner

for required in (
    "startBenchmark", "Measure overhead (optional)", "dd_perf_run(&times)",
    "dd_perf_render(encoded", "dd_device_test_vm()",
    "self.benchmarkButton.enabled = NO", "self.benchmarkButton.enabled =",
    "UIScrollView", "contentLayoutGuide", "frameLayoutGuide",
    "DD_RUNTIME_COMPLETE=PASS", "self.performanceReport", "UIAlertController",
    "Share functional PASS/failure", "Share observational benchmark",
    "presentShareWithText:self.report", "presentShareWithText:self.performanceReport",
):
    assert required in ui, required
assert ui.index("DD_RUNTIME_COMPLETE=PASS") < ui.index("startBenchmark")
validation = ui.split("static NSString *DDRunValidation(", 1)[1].split("static NSString *DDRunPerformance(", 1)[0]
assert validation.index("DD_RUNTIME_ERROR=OBJC_CE") < validation.index("DD_RUNTIME_COMPLETE=PASS")
assert "NSString *result = DDRunPerformance(abi);" in ui
assert "if (self.running || !self.benchmarkButton.enabled ||" in ui

for required in (
    "python3 scripts/test_protection_perf.py",
    "Verify macOS host timing protocol (not iOS performance)",
    "perf_pilot.c", "perf_report.c", "perf_host_runner.c",
    '"$lab/perf_audit.py" verify', "--context MACOS_HOST",
    "host-performance.log", "host-performance-report.json",
    "device_suites perf_pilot perf_report; do",
    "No CI signing, installation", "workflow_dispatch:",
):
    assert required in workflow, required
for disallowed in ("codesign -s", "ldid -S", "devicectl device install",
                   "make clean package", "TARGET_CC=", "fpass-plugin"):
    assert disallowed.lower() not in workflow.lower()
print("Performance pilot: 1000 timing vectors, 17-line strict parser "
      "negatives, 5 median-C pairs, opt-in UIKit separation, CI guards PASS")
