#!/usr/bin/env python3
"""Build-time CE-inspired encoding for a PUBLIC canary. Not cryptography."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

MARKER = b"DUODASH_CE_PILOT_CANARY_V1_7F29D1B3"
KEY = 0xA7
STEP = 0x29


def encode(data: bytes = MARKER) -> bytes:
    return bytes(b ^ ((KEY + i * STEP) & 255) for i, b in enumerate(data))


def decode(encoded: bytes) -> bytes:
    return encode(encoded)


def hash_model(seed: int, data: bytes = MARKER) -> int:
    state = seed ^ 2166136261
    for b in data:
        state = ((state ^ b) * 16777619) & 0xFFFFFFFF
    return state


def dispatch_model(a: int, b: int, mode: int) -> int:
    mask = (1 << 64) - 1
    if (mode & 1) == 0:
        return ((a ^ 0x9E3779B97F4A7C15) + b * 0x00000100000001B3) & mask
    return (((a + b) & mask) ^ 0xD1B54A32D192ED03) + (b >> 11) & mask


def make_header(output: Path) -> None:
    data = encode()
    encoded = ", ".join(f"0x{value:02x}" for value in data)
    content = (
        "/* Generated from public pilot marker by sllvm_generator.py. */\n"
        "#ifndef DD_SLLVM_ENCODED_H\n"
        "#define DD_SLLVM_ENCODED_H\n"
        f"#define DD_CE_KEY 0x{KEY:02x}U\n"
        f"#define DD_CE_STEP 0x{STEP:02x}U\n"
        f"#define DD_CE_DATA {{{encoded}}}\n"
        "#endif\n"
    )
    if MARKER in content.encode("utf-8"):
        raise AssertionError("Generated header leaks plaintext marker")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"CE PILOT: bytes={len(data)} encoded-sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    make_header(args.out)
