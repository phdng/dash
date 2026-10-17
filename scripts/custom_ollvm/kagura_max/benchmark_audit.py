#!/usr/bin/env python3
"""Strict host benchmark report: per-stage native ns/call, not a security score."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
from pathlib import Path

SAMPLES = 11
CALLS = 32768
STAGES = ("str", "fla", "bcf", "sub", "co", "bbr", "bbs")


def parse(path: Path) -> dict:
    content = path.read_bytes()
    if len(content) > 4096:
        raise AssertionError("Oversized native benchmark output")
    lines = content.decode("ascii", errors="strict").splitlines()
    prefix = [
        "DD_KAGURA_BENCH_SCHEMA=1",
        "DD_KAGURA_BENCH_CONTEXT=MACOS_HOST",
        f"DD_KAGURA_BENCH_SAMPLES={SAMPLES}",
        f"DD_KAGURA_BENCH_CALLS_PER_SAMPLE={CALLS}",
    ]
    if lines[:4] != prefix or len(lines) != 4 + SAMPLES + 2:
        raise AssertionError("Wrong host benchmark header or sample count")
    values = []
    for pos, line in enumerate(lines[4:4 + SAMPLES], 1):
        match = re.fullmatch(
            rf"DD_KAGURA_BENCH_SAMPLE_{pos:02d}_NS_PER_CALL=([0-9]+)", line
        )
        if not match:
            raise AssertionError("Malformed, missing or duplicate timing sample")
        value = int(match.group(1))
        if not 0 < value < 1_000_000_000:
            raise AssertionError("Implausible timing sample")
        values.append(value)
    checksum = re.fullmatch(
        r"DD_KAGURA_BENCH_CHECKSUM=([0-9a-f]{16})", lines[-2]
    )
    if checksum is None or lines[-1] != "DD_KAGURA_BENCH_COMPLETE=PASS":
        raise AssertionError("Missing observable result checksum or complete PASS")
    ranked = sorted(values)
    return {
        "samples": SAMPLES,
        "calls_per_sample": CALLS,
        "median_ns_per_call": int(statistics.median(ranked)),
        "p95_nearest_rank_ns_per_call": ranked[math.ceil(.95 * SAMPLES) - 1],
        "checksum": checksum.group(1),
        "log_sha256": hashlib.sha256(content).hexdigest(),
    }


def review(baseline: Path, stages: Path, output: Path) -> dict:
    plain = parse(baseline)
    result = {
        "schema": 1,
        "context": "MACOS_HOST_ONLY",
        "experiment": "KAGURA_K1_NATIVE_RELATIVE_MICROBENCH",
        "baseline": plain,
        "stages": [],
        "samples_per_binary": SAMPLES,
        "calls_per_sample": CALLS,
        "host_only_noise_and_thermal_throttling_possible": True,
        "cold_start_measured": False,
        "ios_device_runtime_measured": False,
        "arm64e_runtime_measured": False,
        "security_strength_score": None,
        "production_crane_modified": False,
    }
    for index, name in enumerate(STAGES, 1):
        path = stages / f"stage{index:02d}-{name}-bench.log"
        candidate = parse(path)
        if candidate["checksum"] != plain["checksum"]:
            raise AssertionError(f"{name}: native benchmark result differs from baseline")
        candidate.update({
            "stage": index,
            "pass": name,
            "median_overhead_ratio_vs_baseline":
                round(candidate["median_ns_per_call"] /
                      plain["median_ns_per_call"], 3),
            "p95_overhead_ratio_vs_baseline":
                round(candidate["p95_nearest_rank_ns_per_call"] /
                      plain["p95_nearest_rank_ns_per_call"], 3),
        })
        result["stages"].append(candidate)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("KAGURA_K1_HOST_BENCH_PASS: 11 samples x 32768 calls each "
          "for baseline and seven stages; no iOS runtime claim")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--stages", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    review(a.baseline, a.stages, a.out)


if __name__ == "__main__":
    main()
