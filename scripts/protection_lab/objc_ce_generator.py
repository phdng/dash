#!/usr/bin/env python3
"""Build-time Objective-C NSString CE canary fixture. Reversible XOR, NOT crypto.

All three strings are public test inputs. Never put production secrets here.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

TEXTS = (
    "DUODASH_OBJC_CE_CANARY_V2_A64E_38C10E7F",
    "DuoDash | Tiếng Việt | arm64e | 🔐",
    "Credits & Licenses",
)
KEY, STEP, SLOT_STEP = 0xA7, 0x29, 0x31


def encode(index: int) -> bytes:
    raw = TEXTS[index].encode("utf-8")
    return bytes(byte ^ ((KEY + pos * STEP + index * SLOT_STEP) & 255)
                 for pos, byte in enumerate(raw))


def decode(index: int, encoded: bytes) -> str:
    data = bytes(byte ^ ((KEY + pos * STEP + index * SLOT_STEP) & 255)
                 for pos, byte in enumerate(encoded))
    return data.decode("utf-8", errors="strict")


def render() -> str:
    maximum = max(len(text.encode("utf-8")) for text in TEXTS)
    lines = [
        "/* GENERATED from PUBLIC fixture strings by objc_ce_generator.py. */",
        "#ifndef DD_OBJC_CE_DATA_H",
        "#define DD_OBJC_CE_DATA_H",
        f"#define DD_OBJC_CE_KEY 0x{KEY:02x}U",
        f"#define DD_OBJC_CE_STEP 0x{STEP:02x}U",
        f"#define DD_OBJC_CE_SLOT_STEP 0x{SLOT_STEP:02x}U",
        f"#define DD_OBJC_CE_MAX_LEN {maximum}U",
    ]
    for index, text in enumerate(TEXTS):
        data = encode(index)
        assert data and decode(index, data) == text
        lines.append(f"#define DD_OBJC_CE_LEN_{index} {len(data)}U")
        lines.append(f"static const volatile unsigned char dd_objc_ce_data_{index}[] = {{")
        for start in range(0, len(data), 12):
            lines.append("    " + ", ".join(f"0x{v:02x}" for v in data[start:start + 12]) + ",")
        lines.append("};")
    lines.append("#endif")
    result = "\n".join(lines) + "\n"
    if any(text.encode("utf-8") in result.encode("utf-8") for text in TEXTS):
        raise AssertionError("Generated header leaked a test string")
    return result


def emit(path: Path) -> None:
    content = render()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write exact UTF-8/LF bytes on Windows and macOS (no CRLF translation).
    path.write_bytes(content.encode("utf-8"))
    print("OBJC_CE_GENERATED: 3 public strings, sha256=" +
          hashlib.sha256(content.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    emit(parser.parse_args().out)
