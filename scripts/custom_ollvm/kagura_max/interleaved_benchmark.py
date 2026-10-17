#!/usr/bin/env python3
"""Kagura K3: host-only counterbalanced, interleaved benchmark verification.

Run 8 fixed executable variants in 16 counterbalanced rounds: in each
8-round block every variant occupies each slot exactly once; second
block reverses the ordering. Every invocation emits eleven benchmark
samples and a checksum. All raw logs and executable SHA256 hashes
must agree before reporting pooled p95 or paired median overhead.

No claim of iPhone timing, cold-start latency, security strength, or
statistical significance on a shared CI runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
from pathlib import Path

from benchmark_audit import CALLS, SAMPLES, STAGES, parse

LABELS = ("baseline", *STAGES)
ROUNDS = 16
TOTAL_PER_VARIANT = ROUNDS * SAMPLES


def round_order(round_number: int) -> tuple[str, ...]:
    if not 0 <= round_number < ROUNDS:
        raise ValueError("Invalid interleaved round number")
    shift = round_number % len(LABELS)
    order = LABELS[shift:] + LABELS[:shift]
    if round_number >= len(LABELS):
        order = tuple(reversed(order))
    return order


def executable_paths(stages: Path) -> dict[str, Path]:
    return {
        label: stages / (
            "stage00-baseline-bench" if label == "baseline"
            else f"stage{idx:02d}-{label}-bench"
        )
        for idx, label in enumerate(LABELS)
    }


def log_path(logs: Path, round_number: int, label: str) -> Path:
    if label not in LABELS or not 0 <= round_number < ROUNDS:
        raise ValueError("Unrecognized interleaved benchmark step")
    return logs / f"round{round_number + 1:02d}-{label}.log"


def run_rounds(stages: Path, logs: Path) -> dict[str, str]:
    executables = executable_paths(stages)
    for name, path in executables.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing executable for {name}: {path}")
    binary_hashes = {
        label: hashlib.sha256(path.read_bytes()).hexdigest()
        for label, path in executables.items()
    }
    logs.mkdir(parents=True, exist_ok=True)
    # Fail closed rather than mixing logs from unrelated prior runs.
    if any(logs.iterdir()):
        raise AssertionError("Interleaved log directory must start empty")
    for round_index in range(ROUNDS):
        for label in round_order(round_index):
            raw = subprocess.run(
                [str(executables[label])], capture_output=True,
                check=False, timeout=30,
            )
            if raw.returncode or raw.stderr:
                raise RuntimeError(
                    f"Benchmark {label}, round {round_index + 1} failed: "
                    f"exit={raw.returncode}, stderr={raw.stderr[-500:]!r}"
                )
            output = log_path(logs, round_index, label)
            output.write_bytes(raw.stdout)
            parse(output)  # Validate EVERY run before the next one.
    return binary_hashes


def nearest_rank(values: list[int], fraction: float) -> int:
    if not values or not 0 < fraction <= 1:
        raise ValueError("Invalid p-rank inputs")
    ordered = sorted(values)
    return ordered[math.ceil(fraction * len(ordered)) - 1]


def validate_order() -> None:
    """Check Latin-square coverage and reversed second cycle."""
    if len(LABELS) != 8 or ROUNDS != 2 * len(LABELS):
        raise AssertionError("Kagura 8-variant benchmark design changed")
    for r in range(ROUNDS):
        if len(set(round_order(r))) != len(LABELS):
            raise AssertionError("Repeated/missing variant within one round")
    for block in (0, 1):
        for label in LABELS:
            positions = [
                round_order(r).index(label)
                for r in range(block * 8, (block + 1) * 8)
            ]
            if sorted(positions) != list(range(8)):
                raise AssertionError("Variant not position-balanced")


def review_logs(logs: Path, report: Path,
                binary_hashes: dict[str, str] | None = None) -> dict:
    validate_order()
    expected_paths = {
        log_path(logs, round_index, label).name
        for round_index in range(ROUNDS) for label in LABELS
    }
    actual_paths = {p.name for p in logs.iterdir()}
    if actual_paths != expected_paths:
        raise AssertionError("Missing or unexpected interleaved benchmark log")
    if binary_hashes is not None and (
        set(binary_hashes) != set(LABELS) or
        any(len(h) != 64 or any(c not in "0123456789abcdef" for c in h)
            for h in binary_hashes.values())
    ):
        raise AssertionError("Invalid executable SHA-256 manifest")

    by_variant: dict[str, list[int]] = {label: [] for label in LABELS}
    medians: dict[str, list[int]] = {label: [] for label in LABELS}
    checksums: set[str] = set()
    rounds: list[dict] = []
    for round_index in range(ROUNDS):
        entries: dict[str, dict] = {}
        for label in round_order(round_index):
            path = log_path(logs, round_index, label)
            parsed = parse(path)   # Schema, exact 11 samples, checksum, PASS
            # Keep the exact per-sample values, not only per-run median.
            lines = path.read_text(encoding="ascii").splitlines()
            samples = [
                int(line.split("=", 1)[1])
                for line in lines[4:4 + SAMPLES]
            ]
            assert len(samples) == SAMPLES
            by_variant[label].extend(samples)
            medians[label].append(parsed["median_ns_per_call"])
            checksums.add(parsed["checksum"])
            entries[label] = {
                "median_ns_per_call": parsed["median_ns_per_call"],
                "min_ns_per_call": min(samples),
                "max_ns_per_call": max(samples),
                "raw_log_sha256": parsed["log_sha256"],
            }
        if len(checksums) != 1:
            raise AssertionError("Native observable checksum differs across variants")
        rounds.append({
            "round": round_index + 1,
            "execution_order": list(round_order(round_index)),
            "measured": entries,
        })
    if len(checksums) != 1:
        raise AssertionError("No unique observable checksum")

    baseline = by_variant["baseline"]
    baseline_p50 = statistics.median(baseline)
    baseline_p95 = nearest_rank(baseline, 0.95)
    if not baseline_p50 or not baseline_p95:
        raise AssertionError("Zero baseline timing")
    variants: list[dict] = []
    for label in LABELS:
        samples = by_variant[label]
        if len(samples) != TOTAL_PER_VARIANT:
            raise AssertionError("Incomplete interleaved samples")
        med = statistics.median(samples)
        p95 = nearest_rank(samples, 0.95)
        paired = [
            medians[label][r] / medians["baseline"][r]
            for r in range(ROUNDS)
        ]
        variant = {
            "label": label,
            "samples": len(samples),
            "pooled_median_ns_per_call": med,
            "pooled_p95_nearest_rank_ns_per_call": p95,
            "pooled_median_ratio_vs_baseline": round(med / baseline_p50, 3),
            "pooled_p95_ratio_vs_baseline": round(p95 / baseline_p95, 3),
            "paired_round_median_ratio_vs_baseline":
                round(statistics.median(paired), 3),
            "rounds_above_5x_baseline_median": sum(value > 5 for value in paired),
            "round_median_min_ns": min(medians[label]),
            "round_median_max_ns": max(medians[label]),
        }
        if binary_hashes is not None:
            variant["executable_sha256"] = binary_hashes[label]
        variants.append(variant)

    result = {
        "schema": 1,
        "experiment": "KAGURA_K3_COUNTERBALANCED_HOST_MICROBENCH",
        "context": "MACOS_HOST_ONLY",
        "rounds": ROUNDS,
        "variants": variants,
        "raw_rounds": rounds,
        "samples_per_executable_per_round": SAMPLES,
        "calls_per_sample": CALLS,
        "total_samples_per_variant": TOTAL_PER_VARIANT,
        "p95_method": "NEAREST_RANK_OVER_176_RAW_SAMPLES_NOT_MAX",
        "execution_order": "TWO_8_ROUND_POSITION_BALANCED_CYCLES_SECOND_REVERSED",
        "all_native_checksums_equal": True,
        "observable_checksum": next(iter(checksums)),
        "host_noise_and_quantized_integer_ns_per_call": True,
        "cold_start_measured": False,
        "ios_runtime_measured": False,
        "arm64e_pac_runtime_measured": False,
        "security_strength_score": None,
        "crane_production_modified": False,
        "notes": (
            "Sequential in-process 11 samples per executable; rounds are "
            "counterbalanced, not a blinded or statistically randomized study. "
            "Pooled sample p95 values can be correlated within an invocation."
        ),
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "KAGURA_K3_HOST_COUNTERBALANCED_PASS: "
        "16 rounds, 8 variants, 176 samples per variant, strict checksum "
        "and raw-log validation; macOS host only"
    )
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stages", type=Path)
    p.add_argument("--logs", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify-only", action="store_true")
    args = p.parse_args()
    if args.verify_only:
        if args.stages is not None:
            p.error("--verify-only must not provide --stages")
        review_logs(args.logs, args.out)
    else:
        if args.stages is None:
            p.error("--stages is required without --verify-only")
        hashes = run_rounds(args.stages, args.logs)
        review_logs(args.logs, args.out, hashes)


if __name__ == "__main__":
    main()
