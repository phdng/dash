#!/usr/bin/env python3
"""Portable regression guards for isolated SLLVM-inspired CE/ICALL dual-ABI pilot."""
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


def load(name: str):
    path = LAB / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(obj)
    return obj


ce = load("sllvm_generator")
audit = load("sllvm_audit")
macho = load("audit")
marker = ce.MARKER
encoded = ce.encode()
assert len(marker) >= 24
assert marker != encoded and marker not in encoded
assert ce.decode(encoded) == marker
assert ce.encode(encoded) == marker
assert marker.decode("ascii") in (LAB / "sllvm_plain.c").read_text(encoding="utf-8")
assert marker.decode("ascii") not in (LAB / "sllvm_protected.c").read_text(encoding="utf-8")
assert marker.decode("ascii") not in (LAB / "sllvm_runner.c").read_text(encoding="utf-8")

random_source = random.Random(93473)
values = [(0, 0, 0), (0, (1 << 64) - 1, 1),
          ((1 << 64) - 1, (1 << 64) - 1, 2)]
values.extend((random_source.getrandbits(64), random_source.getrandbits(64),
               random_source.getrandbits(32)) for _ in range(10000))
for a, b, mode in values:
    assert ce.hash_model((a >> 32) & 0xffffffff) == ce.hash_model(
        (a >> 32) & 0xffffffff, ce.decode(encoded)
    )
    assert ce.dispatch_model(a, b, mode) == ce.dispatch_model(a, b, mode & 1)


def fixture(subtype: int, payload: bytes) -> bytes:
    return (struct.pack("<IIIIIIII", macho.MAGIC, macho.ARM64_CPUTYPE,
                        subtype, macho.MH_DYLIB, 0, 0, 0, 0) + payload)


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    header = tmp / "sllvm_encoded.h"
    ce.make_header(header)
    generated = header.read_bytes()
    ce.make_header(header)
    assert generated == header.read_bytes()
    assert marker not in generated
    assert b"#define DD_CE_DATA {" in generated

    binaries = {}
    for arch, subtype in (("arm64", 0), ("arm64e", 0x80000002)):
        plain, protected = (tmp / f"plain-{arch}.dylib",
                            tmp / f"protected-{arch}.dylib")
        plain.write_bytes(fixture(subtype, b"baseline...." + marker + b"tail"))
        protected.write_bytes(fixture(subtype, b"protected...." + encoded + b"tail"))
        binaries[arch] = (plain, protected)

    host_log = tmp / "host-vectors.txt"
    host_log.write_text("SLLVM_PILOT_HOST_PASS: 8192 CE/ICALL parity vectors\n",
                        encoding="utf-8")
    report = audit.build_report(binaries, host_log, header, tmp / "report.json")
    assert json.loads((tmp / "report.json").read_text(encoding="utf-8")) == report
    assert report["host_vectors_verified"] == 8192
    assert report["ios_device_pac_runtime"].startswith("NOT_TESTED")
    assert report["slices"]["arm64e"]["protected"]["versioned_pac_abi"] is True
    for arch in ("arm64", "arm64e"):
        assert report["slices"][arch]["plain_marker_occurrences"] == 1
        assert report["slices"][arch]["protected_marker_occurrences"] == 0
        assert report["slices"][arch]["sllvm_commercial_plugin_loaded"] is False

    def reject():
        try:
            audit.build_report(binaries, host_log, header, tmp / "invalid-report.json")
        except (AssertionError, ValueError):
            return
        raise AssertionError("Invalid binary/host evidence was accepted")

    host_log.write_text("not a pass\n", encoding="utf-8")
    reject()
    host_log.write_text("SLLVM_PILOT_HOST_PASS: 8192 CE/ICALL parity vectors\n",
                        encoding="utf-8")
    p = binaries["arm64"][1]
    p.write_bytes(fixture(0, b"protected" + encoded + marker))
    reject()
    p.write_bytes(fixture(0, b"protected" + encoded + b"tail"))
    p = binaries["arm64e"][1]
    p.write_bytes(fixture(1, encoded))
    reject()
    p.write_bytes(fixture(0x80000002, b"protected" + encoded))
    p = binaries["arm64e"][0]
    p.write_bytes(fixture(0x80000002, b"NO_PLAINTEXT_CONTROL"))
    reject()

workflow = (ROOT / ".github/workflows/protection-sllvm-pilot.yml").read_text(
    encoding="utf-8"
)
assert "workflow_dispatch:" in workflow and "runs-on: macos-14" in workflow
assert "xcrun --sdk iphoneos --find clang" in workflow
assert "for arch in arm64 arm64e; do" in workflow
assert "for variant in plain protected; do" in workflow
assert "--arm64e-protected" in workflow and "--host-log" in workflow
assert "sllvm_audit.py" in workflow and "sllvm_runner.c" in workflow
assert "SLLVM_PILOT_HOST_PASS: 8192 CE/ICALL parity vectors" in workflow
assert "otool -tvV" in workflow and "report.json" in workflow
assert "actions/upload-artifact@v4" in workflow
assert "make clean package" not in workflow and "TARGET_CC=" not in workflow
assert "llvm@19" not in workflow and "fpass-plugin" not in workflow
assert "NOT TESTED" in workflow
assert "protection-lab.yml" not in workflow
print(f"SLLVM-inspired CE/ICALL pilot: {len(values)} portable vectors, "
      "arm64/arm64e binary negative gates, CI isolation PASS")
