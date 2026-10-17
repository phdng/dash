#!/usr/bin/env python3
"""Strict parser for observation-only Protection Lab host/iPhone timing logs.

This is NOT a device attestation, and never turns timings into security scores.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PAIRS = ("VM", "CE", "ICALL", "IGV", "IBR")
ITERATIONS = 20000
REPEATS = 5
TIMING = re.compile(r"[1-9][0-9]{0,18}\Z")


def expected_prefix(context: str, arch: str | None) -> list[str]:
    if context == "MACOS_HOST" and arch is None:
        abi = "NOT_APPLICABLE"
    elif context == "IOS_DEVICE" and arch in ("arm64", "arm64e"):
        abi = "arm64:0x00000000" if arch == "arm64" else "arm64e:0x80000002"
    else:
        raise ValueError("Context and architecture must match")
    return [
        "DD_PERF_SCHEMA=1",
        "DD_PERF_CONTEXT=" + context,
        "DD_PERF_ABI=" + abi,
        f"DD_PERF_ITERATIONS={ITERATIONS}",
        f"DD_PERF_REPEATS={REPEATS}",
        "DD_PERF_ESTIMATOR=MEDIAN_ELAPSED_NS",
    ]


def verify(path: Path, context: str, arch: str | None = None) -> dict:
    raw = path.read_bytes()
    lines = raw.decode("utf-8", errors="strict").splitlines()
    prefix = expected_prefix(context, arch)
    if len(lines) != 17 or lines[:6] != prefix or lines[-1] != (
        "DD_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_PROOF"
    ):
        raise AssertionError("Missing/altered performance report schema or context")
    samples: dict[str, dict] = {}
    for index, pair in enumerate(PAIRS):
        native_label = f"DD_PERF_{pair}_NATIVE_NS="
        candidate_label = f"DD_PERF_{pair}_PROTECTED_NS="
        before = lines[6 + 2 * index]
        after = lines[7 + 2 * index]
        if not before.startswith(native_label) or not after.startswith(candidate_label):
            raise AssertionError(f"Wrong benchmark pair order: {pair}")
        raw_n = before[len(native_label):]
        raw_p = after[len(candidate_label):]
        if not TIMING.fullmatch(raw_n) or not TIMING.fullmatch(raw_p):
            raise AssertionError(f"Invalid elapsed nanoseconds for {pair}")
        n, p = int(raw_n), int(raw_p)
        if n >= (1 << 63) or p >= (1 << 63):
            raise AssertionError("Elapsed benchmark time exceeds usable range")
        samples[pair] = {
            "native_elapsed_ns": n,
            "protected_elapsed_ns": p,
            "observed_ratio_not_an_acceptance_gate": round(p / n, 6),
            "calls_per_sample": ITERATIONS,
            "sampling": f"median_of_{REPEATS}_elapsed_samples",
        }
    return {
        "schema": 1,
        "context_claimed": context,
        "architecture_claimed": arch,
        "measurements": samples,
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "performance_gate": "NONE",
        "ios_device_runtime_verified": False,
        "attestation": "LOG_CONTENT_VALIDATED_PROVENANCE_NOT_AUTHENTICATED",
        "note": "No claim of security improvement, real PAC device runtime, or iOS performance from a host log",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("verify", choices=("verify",))
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--context", choices=("MACOS_HOST", "IOS_DEVICE"), required=True)
    parser.add_argument("--arch", choices=("arm64", "arm64e"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.log, args.context, args.arch)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"DD_PERF_LOG_ACCEPTED: {args.context}, 5 measured pairs, "
          "observation only, provenance NOT VERIFIED")
