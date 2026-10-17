#!/usr/bin/env python3
"""Portable regression for counterbalanced 16-round Kagura K3 host benchmarks."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_max"
sys.path.insert(0, str(LAB))
spec = importlib.util.spec_from_file_location(
    "interleaved_benchmark", LAB / "interleaved_benchmark.py"
)
assert spec and spec.loader
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)

bench.validate_order()
assert bench.ROUNDS == 16
assert bench.TOTAL_PER_VARIANT == 176
assert bench.LABELS == (
    "baseline", "str", "fla", "bcf", "sub", "co", "bbr", "bbs"
)
for label in bench.LABELS:
    for position in range(8):
        assert sum(bench.round_order(r)[position] == label
                   for r in range(bench.ROUNDS)) == 2
for r in range(bench.ROUNDS):
    assert set(bench.round_order(r)) == set(bench.LABELS)
assert bench.nearest_rank(list(range(1, 177)), 0.95) == 168
assert bench.nearest_rank(list(range(1, 177)), 0.95) != 176


def benchmark_log(value: int, checksum: str = "0123456789abcdef") -> bytes:
    lines = [
        "DD_KAGURA_BENCH_SCHEMA=1",
        "DD_KAGURA_BENCH_CONTEXT=MACOS_HOST",
        "DD_KAGURA_BENCH_SAMPLES=11",
        "DD_KAGURA_BENCH_CALLS_PER_SAMPLE=32768",
        *(
            f"DD_KAGURA_BENCH_SAMPLE_{i:02d}_NS_PER_CALL={value + i - 1}"
            for i in range(1, 12)
        ),
        f"DD_KAGURA_BENCH_CHECKSUM={checksum}",
        "DD_KAGURA_BENCH_COMPLETE=PASS",
    ]
    return ("\n".join(lines) + "\n").encode("ascii")


with tempfile.TemporaryDirectory(prefix="kagura K3 fixture ") as temp:
    root = Path(temp)
    logs = root / "logs"
    stages = root / "stage executables"
    logs.mkdir()
    stages.mkdir()
    for i, (label, binary) in enumerate(bench.executable_paths(stages).items()):
        binary.write_bytes(("FAKE_BIN_" + label).encode("ascii"))
    for r in range(bench.ROUNDS):
        for i, label in enumerate(bench.LABELS):
            value = 15 + i * 5 + r % 3
            bench.log_path(logs, r, label).write_bytes(benchmark_log(value))
    manifest = bench.review_logs(logs, root / "report.json")
    assert manifest["context"] == "MACOS_HOST_ONLY"
    assert manifest["total_samples_per_variant"] == 176
    assert len(manifest["raw_rounds"]) == 16
    assert len(manifest["variants"]) == 8
    assert manifest["p95_method"] == "NEAREST_RANK_OVER_176_RAW_SAMPLES_NOT_MAX"
    assert manifest["all_native_checksums_equal"] is True
    assert manifest["cold_start_measured"] is False
    assert manifest["ios_runtime_measured"] is False
    assert manifest["arm64e_pac_runtime_measured"] is False
    assert manifest["crane_production_modified"] is False
    assert manifest["security_strength_score"] is None
    assert manifest["variants"][0]["pooled_median_ratio_vs_baseline"] == 1.0
    assert manifest["variants"][3]["pooled_median_ratio_vs_baseline"] > 1.0
    for entry in manifest["variants"]:
        assert entry["samples"] == 176
        assert entry["pooled_p95_nearest_rank_ns_per_call"] > 0
        assert entry["paired_round_median_ratio_vs_baseline"] > 0
    assert json.loads((root / "report.json").read_text()) == manifest

    def should_reject(message: str) -> None:
        try:
            bench.review_logs(logs, root / "bad.json")
        except (AssertionError, ValueError, UnicodeError, OSError):
            return
        raise AssertionError(f"Unsafe interleaved evidence accepted: {message}")

    victim = bench.log_path(logs, 3, "bbs")
    original = victim.read_bytes()
    victim.write_bytes(original.replace(
        b"DD_KAGURA_BENCH_CHECKSUM=0123456789abcdef",
        b"DD_KAGURA_BENCH_CHECKSUM=ffffffffffffffff"
    ))
    should_reject("cross-executable checksum mismatch")
    victim.write_bytes(original)
    victim.write_bytes(original.replace(
        b"DD_KAGURA_BENCH_COMPLETE=PASS", b"DD_KAGURA_BENCH_COMPLETE=FAIL"
    ))
    should_reject("failed benchmark")
    victim.write_bytes(original)
    victim.write_bytes(original.replace(
        b"DD_KAGURA_BENCH_CONTEXT=MACOS_HOST",
        b"DD_KAGURA_BENCH_CONTEXT=IOS_DEVICE"
    ))
    should_reject("device result masquerading as host")
    victim.write_bytes(original)
    victim.write_bytes(original + b"UDID=PRIVATE_DO_NOT_RECORD\n")
    should_reject("unexpected metadata")
    victim.write_bytes(original)
    victim.unlink()
    should_reject("missing round")
    victim.write_bytes(original)
    junk = logs / "round17-unknown.log"
    junk.write_bytes(original)
    should_reject("unexpected round or file")
    junk.unlink()

    # Mock only process I/O, not any CI/compiler or real device data.
    runs: list[str] = []
    original_run = bench.subprocess.run
    def fake_run(argv, capture_output, check, timeout):
        assert capture_output and not check and timeout == 30
        name = Path(argv[0]).name
        runs.append(name)
        assert name.endswith("-bench")
        return SimpleNamespace(returncode=0, stderr=b"",
                               stdout=benchmark_log(65))
    bench.subprocess.run = fake_run
    try:
        new_logs = root / "new-logs"
        hashes = bench.run_rounds(stages, new_logs)
        assert len(runs) == 16 * 8
        assert len(hashes) == 8
        assert len(list(new_logs.iterdir())) == 128
        observed = bench.review_logs(new_logs, root / "new-report.json", hashes)
        assert all(len(row["executable_sha256"]) == 64
                   for row in observed["variants"])
        try:
            bench.run_rounds(stages, new_logs)
        except AssertionError:
            pass
        else:
            raise AssertionError("Previous log directory silently reused")
    finally:
        bench.subprocess.run = original_run

workflow = (ROOT / ".github/workflows/kagura-max-candidate.yml").read_text(
    encoding="utf-8"
)
for required in (
    "workflow_dispatch:",
    "python3 scripts/test_kagura_interleaved_bench.py",
    "K3 counterbalanced host performance across all Kagura stages",
    "interleaved_benchmark.py",
    '--stages "$KAGURA_OUT/stages"',
    '--logs "$KAGURA_OUT/stages/interleaved"',
    "kagura-k3-host-interleaved.json",
    "kagura-k3-host-reverified.json",
    "--verify-only",
    "DuoDash-Kagura-MAX-CANDIDATE-LLVM19-EXPERIMENTAL",
):
    assert required in workflow, required
for excluded in (
    "make clean package", "DEVELOPMENT_TEAM=", "codesign -s",
    "devicectl device install", "ldid -S", "PAC_STRIP",
):
    assert excluded.lower() not in workflow.lower()
assert "scripts/custom_ollvm/kagura_max/out/" in workflow
assert "interleaved_benchmark" not in (ROOT / "Makefile").read_text(
    encoding="utf-8"
)
print(
    "KAGURA_K3_COUNTERBALANCED_PORTABLE_PASS: 16 rounds x 8 variants, "
    "balanced positions, 176 samples/pipeline, cross-binary checksum, "
    "negative evidence tests; macOS native CI NOT YET RUN"
)
