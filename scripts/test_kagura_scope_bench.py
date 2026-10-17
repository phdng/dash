#!/usr/bin/env python3
"""Kagura K2: translation-unit isolation and native host overhead gates.

This is not a per-function LLVM compiler filter; Kagura may transform its
generated decrypt helper. Timing fixtures are synthetic and not device proof.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "scripts/custom_ollvm/kagura_max"
sys.path.insert(0, str(DIR))
stage_spec = importlib.util.spec_from_file_location("stage_pipeline", DIR / "stage_pipeline.py")
bench_spec = importlib.util.spec_from_file_location("benchmark_audit", DIR / "benchmark_audit.py")
assert stage_spec and stage_spec.loader and bench_spec and bench_spec.loader
stage = importlib.util.module_from_spec(stage_spec)
bench = importlib.util.module_from_spec(bench_spec)
stage_spec.loader.exec_module(stage)
bench_spec.loader.exec_module(bench)

source = """define i64 @dd_kagura_critical(i64 %x) {
entry:
  ret i64 %x
}
"""
transformed = source + """define internal i32 @kagura_decrypt_123(i32 %x) {
entry:
  ret i32 %x
}
"""
assert stage.defined_functions(source) == {"dd_kagura_critical"}
assert stage.defined_functions(transformed) == {
    "dd_kagura_critical", "kagura_decrypt_123"
}
scope = stage.scope_report(source, transformed, "Running pass: Kagura")
assert scope["strict_single_function_pass_filter_verified"] is False
assert scope["scope"] == "ISOLATED_TRANSLATION_UNIT_NOT_FUNCTION_PASS_ALLOWLIST"
assert scope["generated_helpers_may_receive_kagura_function_passes"] is True
assert scope["generated_decryption_helpers"] == ["kagura_decrypt_123"]
assert scope["unprotected_sentinel_pass_invoked"] is False

def reject_scope(original, candidate, debug=""):
    try:
        stage.scope_report(original, candidate, debug)
    except AssertionError:
        return
    raise AssertionError("Unsafe allowlist/scope claim was accepted")

reject_scope(source + """define i32 @dd_kagura_unprotected_sentinel() {
entry:
  ret i32 0
}
""", transformed)
reject_scope(source, source.replace("dd_kagura_critical", "not_allowlisted"))
reject_scope(source, source + """define i32 @objc_msgSend() {
entry:
  ret i32 0
}
""")
reject_scope(source, transformed, "Running pass on dd_kagura_unprotected_sentinel")
reject_scope(source, source + """define i32 @generated_unreviewed_helper() {
entry:
  ret i32 0
}
""")

def make_log(samples: list[int], checksum: str = "0123456789abcdef") -> str:
    lines = [
        "DD_KAGURA_BENCH_SCHEMA=1",
        "DD_KAGURA_BENCH_CONTEXT=MACOS_HOST",
        "DD_KAGURA_BENCH_SAMPLES=11",
        "DD_KAGURA_BENCH_CALLS_PER_SAMPLE=32768",
        *(f"DD_KAGURA_BENCH_SAMPLE_{i:02d}_NS_PER_CALL={value}"
          for i, value in enumerate(samples, 1)),
        f"DD_KAGURA_BENCH_CHECKSUM={checksum}",
        "DD_KAGURA_BENCH_COMPLETE=PASS",
    ]
    return "\n".join(lines) + "\n"

assert bench.STAGES == ("str", "fla", "bcf", "sub", "co", "bbr", "bbs")
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    baseline = root / "stage00-baseline-bench.log"
    baseline.write_text(make_log([100, 80, 90, 102, 88, 105,
                                  99, 101, 120, 95, 110]), encoding="ascii")
    base = bench.parse(baseline)
    assert base["median_ns_per_call"] == 100
    assert base["p95_nearest_rank_ns_per_call"] == 120
    assert base["calls_per_sample"] == 32768

    for i, name in enumerate(bench.STAGES, 1):
        (root / f"stage{i:02d}-{name}-bench.log").write_text(
            make_log([200] * 11), encoding="ascii"
        )
    report = root / "summary.json"
    review = bench.review(baseline, root, report)
    assert len(review["stages"]) == 7
    assert review["stages"][0]["median_overhead_ratio_vs_baseline"] == 2.0
    assert review["stages"][0]["p95_overhead_ratio_vs_baseline"] == 1.667
    assert review["ios_device_runtime_measured"] is False
    assert review["arm64e_runtime_measured"] is False
    assert review["cold_start_measured"] is False
    assert review["security_strength_score"] is None
    assert json.loads(report.read_text(encoding="utf-8")) == review

    def reject_timing(raw: str):
        with tempfile.TemporaryDirectory() as nested:
            file = Path(nested) / "timing.txt"
            file.write_text(raw, encoding="ascii")
            try:
                bench.parse(file)
            except (AssertionError, UnicodeError):
                return
            raise AssertionError("Malformed benchmark timing report accepted")
    good = make_log([50] * 11)
    reject_timing(good.replace("CONTEXT=MACOS_HOST", "CONTEXT=IOS_DEVICE"))
    reject_timing(good.replace("SAMPLES=11", "SAMPLES=10"))
    reject_timing(good.replace("SAMPLE_01_NS_PER_CALL=50", "SAMPLE_01_NS_PER_CALL=0"))
    reject_timing(good.replace("SAMPLE_11_NS_PER_CALL=50", "SAMPLE_11_NS_PER_CALL=1000000000"))
    reject_timing(good.replace("SAMPLE_01_NS_PER_CALL", "SAMPLE_02_NS_PER_CALL"))
    reject_timing(good.replace("COMPLETE=PASS", "COMPLETE=FAIL"))
    reject_timing(good + "UDID=NEVER\n")
    reject_timing(good.replace("CHECKSUM=0123456789abcdef", "CHECKSUM=foo"))
    reject_timing("x" * 4097)

    wrong = root / "stage07-bbs-bench.log"
    wrong.write_text(make_log([100] * 11, "ffffffffffffffff"), encoding="ascii")
    try:
        bench.review(baseline, root, root / "bad.json")
    except AssertionError:
        pass
    else:
        raise AssertionError("Incorrect native bench result checksum accepted")

workflow = (ROOT / ".github/workflows/kagura-max-candidate.yml").read_text(
    encoding="utf-8"
)
for phrase in (
    "python3 scripts/test_kagura_scope_bench.py",
    'sentinel.c" -o "$out/sentinel-plain.o"',
    'bench_runner.c" -o "$out/bench-runner.o"',
    '--sentinel-obj "$KAGURA_OUT/sentinel-plain.o"',
    '--benchmark-obj "$KAGURA_OUT/bench-runner.o"',
    "benchmark_audit.py",
    "kagura-k1-host-benchmark.json",
    "workflow_dispatch:",
):
    assert phrase in workflow, phrase
assert "scripts/custom_ollvm/kagura_max/out/" in workflow
assert "scripts/custom_ollvm/kagura_max/critical.c" not in (
    ROOT / "Makefile"
).read_text(encoding="utf-8")
sentinel = (DIR / "sentinel.c").read_text(encoding="utf-8")
assert "dd_kagura_unprotected_sentinel" in sentinel
assert "DD_KAGURA_UNPROTECTED_SENTINEL" not in (DIR / "critical.c").read_text(encoding="utf-8")
bench_source = (DIR / "bench_runner.c").read_text(encoding="utf-8")
for name in ("CLOCK_MONOTONIC", "DD_BENCH_SAMPLES = 11", "DD_BENCH_CALLS = 32768",
             "DD_KAGURA_BENCH_SAMPLE_%02u_NS_PER_CALL=", "dd_bench_sink"):
    assert name in bench_source, name
for prohibited in ("codesign -s", "devicectl device install", "ldid -S",
                   "make clean package", "DEVELOPMENT_TEAM="):
    assert prohibited.lower() not in workflow.lower()

print("KAGURA_SCOPE_HOST_BENCH_PORTABLE_PASS: TU isolation/not full function "
      "allowlist, generated helper disclosure, timing parse and negative gates")
