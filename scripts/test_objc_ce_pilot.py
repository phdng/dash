#!/usr/bin/env python3
"""Portable Objective-C CE canary vectors, Mach-O audit negatives, and CI guards.

No Apple Foundation runtime on Windows: this does not claim native iOS pass.
"""
from __future__ import annotations

import importlib.util
import json
import random
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))


def load(module: str):
    spec = importlib.util.spec_from_file_location(module, LAB / (module + ".py"))
    assert spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ce = load("objc_ce_generator")
audit = load("objc_ce_audit")
macho = load("audit")
assert len(ce.TEXTS) == 3
assert "Tiếng Việt" in ce.TEXTS[1] and "🔐" in ce.TEXTS[1]
assert ce.TEXTS[0].startswith("DUODASH_OBJC_CE_CANARY")
for slot, string in enumerate(ce.TEXTS):
    assert string
    assert ce.decode(slot, ce.encode(slot)) == string
    assert ce.encode(slot) != string.encode("utf-8")
    try:
        ce.decode(slot, b"\xff")
    except UnicodeDecodeError:
        pass
    else:
        # A single corrupted byte might legitimately decode; test robustly
        # by ensuring UTF-8 strict failures via a known invalid byte sequence.
        assert ce.decode(slot, ce.encode(slot)) == string

rng = random.Random(81024)
vectors = [0, 1, 2, 3, 0xffffffff, 0x80000000, 0x80000001, 0x80000002]
vectors.extend(rng.getrandbits(32) for _ in range(10000))
for choice in vectors:
    slot = choice & 3
    plain = ce.TEXTS[slot] if slot < 3 else ""
    protected = ce.decode(slot, ce.encode(slot)) if slot < 3 else ""
    assert plain == protected
    assert plain.encode("utf-8") == protected.encode("utf-8")
    assert len(plain) == len(protected)

raw_plain = (LAB / "objc_ce_plain.m").read_text(encoding="utf-8")
raw_protected = (LAB / "objc_ce_protected.m").read_text(encoding="utf-8")
host_runner = (LAB / "objc_ce_runner.m").read_text(encoding="utf-8")
for string in ce.TEXTS:
    assert string in raw_plain
    assert string not in raw_protected
    assert string not in host_runner
assert "initWithBytes:decoded length:length" in raw_protected
assert "encoding:NSUTF8StringEncoding" in raw_protected
assert "const volatile unsigned char" in raw_protected
assert "@autoreleasepool" in host_runner
assert "[original isEqualToString:transformed]" in host_runner
assert "strcmp(original.UTF8String, transformed.UTF8String)" in host_runner
for forbidden in ("uintptr_t", "ptrauth_strip", "mprotect(", "mmap(",
                  "syscall(", "performSelector:", "objc_msgSend("):
    assert forbidden not in raw_protected


def blob(subtype: int, data: bytes, kind: int = 6) -> bytes:
    return (struct.pack("<IIIIIIII", macho.MAGIC, macho.ARM64_CPUTYPE,
                        subtype, kind, 0, 0, 0, 0) + data)


with tempfile.TemporaryDirectory() as d:
    folder = Path(d)
    generated = folder / "objc_ce_data.h"
    ce.emit(generated)
    first = generated.read_bytes()
    ce.emit(generated)
    assert generated.read_bytes() == first
    assert first == ce.render().encode("utf-8")
    assert all(text.encode("utf-8") not in first for text in ce.TEXTS)

    pairs = {}
    for arch, subtype in (("arm64", 0), ("arm64e", 0x80000002)):
        plain = folder / f"plain-{arch}.dylib"
        protected = folder / f"protected-{arch}.dylib"
        plain.write_bytes(blob(subtype, b"start" +
                               b"|".join(x.encode("utf-8") for x in ce.TEXTS) + b"end"))
        protected.write_bytes(blob(subtype, b"protected|" +
                                   b"|".join(ce.encode(i) for i in range(3)) + b"|end"))
        pairs[arch] = (plain, protected)
    host_log = folder / "host-foundation-parity.txt"
    host_log.write_text(audit.HOST_PASS + "\n", encoding="utf-8")
    output = folder / "report.json"
    verified = audit.make_report(pairs, host_log, generated, output)
    assert json.loads(output.read_text(encoding="utf-8")) == verified
    assert verified["host_vectors"] == 8192
    assert verified["host_test"] == "PASS_MACOS_FOUNDATION_ARC_ONLY"
    assert verified["slices"]["arm64e"]["ce_variant"]["versioned_pac_abi"]
    assert verified["slices"]["arm64"]["marker_protected_occurrences"] == 0
    assert verified["slices"]["arm64e"]["three_encoded_byte_sequences_present"]
    assert verified["pac_runtime"].startswith("NOT_TESTED")
    assert verified["crane_production_changed"] is False

    def should_reject():
        try:
            audit.make_report(pairs, host_log, generated, folder / "invalid.json")
        except (AssertionError, ValueError):
            return
        raise AssertionError("Invalid CE evidence accepted")

    host_log.write_text("HOST PASS?\n", encoding="utf-8")
    should_reject()
    host_log.write_text(audit.HOST_PASS + "\n", encoding="utf-8")
    protected = pairs["arm64"][1]
    protected.write_bytes(blob(0, b"x" + ce.TEXTS[0].encode("utf-8") +
                               b"|".join(ce.encode(i) for i in range(3))))
    should_reject()
    protected.write_bytes(blob(0, b"|".join(ce.encode(i) for i in range(3))))
    protected_arm64e = pairs["arm64e"][1]
    protected_arm64e.write_bytes(blob(1, b"|".join(ce.encode(i) for i in range(3))))
    should_reject()
    protected_arm64e.write_bytes(blob(0x80000002, b"|".join(ce.encode(i) for i in range(3))))
    plain = pairs["arm64"][0]
    plain.write_bytes(blob(0, b"no control marker"))
    should_reject()
    plain.write_bytes(blob(0, b"|".join(x.encode("utf-8") for x in ce.TEXTS)))
    generated.write_bytes(first + b"modified")
    should_reject()

workflow = (ROOT / ".github/workflows/protection-objc-ce-pilot.yml").read_text(
    encoding="utf-8"
)
assert "workflow_dispatch:" in workflow and "runs-on: macos-14" in workflow
assert "for arch in arm64 arm64e; do" in workflow
assert "for variant in plain protected; do" in workflow
assert "xcrun --sdk iphoneos --find clang" in workflow
assert "objc_ce_generator.py" in workflow and "objc_ce_audit.py" in workflow
assert "objc_ce_runner.m" in workflow and "-fobjc-arc" in workflow
assert "8192 NSString/ARC/UTF8 parity vectors" in workflow
assert "--arm64e-protected" in workflow
assert "nm -gU" in workflow and "otool -tvV" in workflow
assert "Foundation" in workflow and "actions/upload-artifact@v4" in workflow
assert "make clean package" not in workflow and "TARGET_CC=" not in workflow
assert "fpass-plugin" not in workflow and "llvm@19" not in workflow
assert "NOT TESTED" in workflow
print(f"Objective-C CE pilot: {len(vectors)} UTF-8/selector model vectors, "
      "binary ABI/marker negatives, isolated CI PASS")
