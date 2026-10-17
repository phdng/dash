#!/usr/bin/env python3
"""Independent deterministic oracle for KaguraLab's public C canary.

This verifies *values* in user-shared text; it cannot authenticate the phone,
the app, the installed IPA, or the reported timings. No device identifiers.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path

MASK = (1 << 64) - 1
PUBLIC_MARKER = b"DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1"
VECTORS = 8192
BENCH_CALLS = 4096


def rol(value: int, count: int) -> int:
    return ((value << count) | (value >> (64 - count))) & MASK


def canary(x: int, salt: int) -> int:
    acc = (x ^ salt ^ 0x6A09E667F3BCC909) & MASK
    for index, byte in enumerate(PUBLIC_MARKER[:8]):
        acc = rol(acc ^ byte, 7)
        acc = (acc + (0x9E3779B97F4A7C15 ^ index)) & MASK
    if x & 1:
        acc ^= (salt * 0x100000001B3) & MASK
        acc = rol(acc, 11)
    else:
        acc = (acc + (salt ^ 0xBF58476D1CE4E5B9)) & MASK
        acc ^= acc >> 13
    if (salt & 7) == 3:
        acc = (((acc * 0x94D049BB133111EB) & MASK) ^ x) & MASK
    return (acc ^ (acc >> 29)) & MASK


@lru_cache(maxsize=1)
def expected_checksums() -> dict[str, str]:
    seed = 0x123456789ABCDEF0
    digest = 0
    for i in range(VECTORS):
        seed ^= (seed << 13) & MASK
        seed ^= seed >> 7
        seed ^= (seed << 17) & MASK
        seed &= MASK
        x = i if i < 16 else seed
        salt = ((seed >> 1) ^ ((i * 0x9E3779B97F4A7C15) & MASK)) & MASK
        digest = (rol(digest ^ canary(x, salt), 9) + i) & MASK
    batch_digest = 0
    for i in range(BENCH_CALLS):
        x = (i * 0x9E3779B97F4A7C15) & MASK
        salt = ((x >> 3) ^ 0xC0FFEE123456789A) & MASK
        batch_digest ^= canary(x, salt)
    return {
        "parity_checksum": f"{digest:016x}",
        "benchmark_checksum": f"{batch_digest:016x}",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--check-host", type=Path)
    a = p.parse_args()
    if a.check_host is not None:
        lines = a.check_host.read_text(encoding="utf-8").splitlines()
        checksums = expected_checksums()
        if lines != [
            "DD_KAGURA_HOST_PARITY_CHECKSUM=" + checksums["parity_checksum"],
            "DD_KAGURA_HOST_BENCHMARK_CHECKSUM=" + checksums["benchmark_checksum"],
        ]:
            raise AssertionError("Compiled native C checksum disagrees with Python oracle")
    result = {
        "schema": 1,
        "canary": "PUBLIC_SYNTHETIC_ONLY",
        "parity_vectors": VECTORS,
        "benchmark_calls_per_sample": BENCH_CALLS,
        **expected_checksums(),
        "provenance": "INDEPENDENT_PYTHON_REFERENCE_NOT_DEVICE_ATTESTATION",
        "native_host_reference_checked": a.check_host is not None,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print("KAGURA_IOS_REFERENCE_READY: independent deterministic checksums")


if __name__ == "__main__":
    main()
