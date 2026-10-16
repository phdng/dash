#!/usr/bin/env python3
"""Portable tests for canary bytecode, ABI-v2 gate, and isolated CI surface."""
from __future__ import annotations
import importlib.util
import json
import random
import struct
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "scripts/protection_lab"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(obj)
    return obj


builder = load("pl_program", DIR / "program.py")
audit = load("pl_audit", DIR / "audit.py")
data = builder.program()


def run_vm(a: int, b: int, code: bytes) -> int:
    registers = [0] * 4
    pc = 0
    for _ in range(64):
        if pc >= len(code):
            raise ValueError("truncated VM code")
        op = code[pc]
        pc += 1
        if op == builder.RET:
            if pc >= len(code) or code[pc] >= 4 or pc + 1 != len(code):
                raise ValueError("bad return")
            return registers[code[pc]]
        if pc >= len(code):
            raise ValueError("truncated register")
        dst = code[pc]
        pc += 1
        if dst >= 4:
            raise ValueError("bad target")
        if op in (builder.LD_A, builder.LD_B):
            registers[dst] = a if op == builder.LD_A else b
            continue
        if op == builder.IMM:
            if len(code) - pc < 8:
                raise ValueError("truncated constant")
            registers[dst] = int.from_bytes(code[pc:pc+8], "little")
            pc += 8
            continue
        if len(code) - pc < 2:
            raise ValueError("truncated instruction")
        src, operand = code[pc:pc+2]
        pc += 2
        if src >= 4:
            raise ValueError("bad source")
        mask = (1 << 64) - 1
        x = registers[src]
        if op in (builder.XOR, builder.ADD, builder.MUL):
            if operand >= 4:
                raise ValueError("bad operand")
            y = registers[operand]
            result = (x ^ y) if op == builder.XOR else (x + y if op == builder.ADD else x * y)
        elif op == builder.ROL and operand < 64:
            result = x if not operand else ((x << operand) | (x >> (64 - operand)))
        elif op == builder.SHR and operand < 64:
            result = x >> operand
        else:
            raise ValueError("bad opcode")
        registers[dst] = result & mask
    raise ValueError("VM execution budget exceeded")


vectors = [(0, 0), (0, (1 << 64) - 1), ((1 << 64) - 1, 0),
           ((1 << 64) - 1, (1 << 64) - 1)]
rand = random.Random(61686)
vectors.extend((rand.getrandbits(64), rand.getrandbits(64)) for _ in range(10000))
assert all(run_vm(a, b, data) == builder.model(a, b) for a, b in vectors)
for invalid in (data[:-1], bytes((builder.IMM, 9)) + data,
                bytes((11,)) + data, data.replace(bytes((builder.RET, 0)), bytes((builder.RET, 9)))):
    try:
        run_vm(10, 20, invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid VM program accepted")
assert not any(token in (DIR / "vm.c").read_text(encoding="utf-8")
               for token in ("mprotect(", "mmap(", "VirtualAlloc(", "syscall("))

with tempfile.TemporaryDirectory() as d:
    temp = Path(d)
    header = temp / "vm_program.h"
    builder.emit_header(header)
    previous = header.read_bytes()
    builder.emit_header(header)
    assert header.read_bytes() == previous

    def fixture(subtype: int, kind: int = 6) -> bytes:
        return struct.pack("<IIIIIIII", audit.MAGIC, audit.ARM64_CPUTYPE,
                           subtype, kind, 0, 0, 0, 0) + b"dummy-body"

    arm64 = temp / "arm64.dylib"
    arm64e = temp / "arm64e.dylib"
    arm64.write_bytes(fixture(0))
    arm64e.write_bytes(fixture(0x80000002))
    output = temp / "report.json"
    result = audit.report(arm64, arm64e, [DIR / "canary.c", DIR / "vm.c", header], output)
    assert result["slices"]["arm64e"]["cpu_subtype"] == 2
    assert result["slices"]["arm64e"]["cpu_subtype_raw"] == "0x80000002"
    assert result["slices"]["arm64e"]["versioned_pac_abi"] is True
    assert result["slices"]["arm64"]["cpu_subtype"] == 0
    assert result["arm64e_pac_device_validation"].startswith("NOT_TESTED")
    assert result["host_runtime"] == "NOT_TESTED"
    assert json.loads(output.read_text(encoding="utf-8")) == result
    host_attestation = temp / "host-vectors.txt"
    host_attestation.write_text("PROTECTION_LAB_HOST_PASS: 8192 native/VM/indirect vectors\n", encoding="utf-8")
    attested = audit.report(arm64, arm64e, [DIR / "vm.c"], temp / "attested.json", host_attestation)
    assert attested["host_vectors"] == 8192
    assert attested["host_runtime"] == "PASS_HOST_MACOS_ONLY"
    host_attestation.write_text("bad", encoding="utf-8")
    try:
        audit.report(arm64, arm64e, [DIR / "vm.c"], temp / "invalid.json", host_attestation)
    except AssertionError:
        pass
    else:
        raise AssertionError("Forged/invalid host vector report accepted")
    for bad_subtype, bad_kind in ((1, 6), (0, 6), (2, 6), (0x40000002, 6),
                                  (0xc0000002, 6), (0x80000002, 1), (0x80000002, 2)):
        arm64e.write_bytes(fixture(bad_subtype, bad_kind))
        try:
            audit.inspect(arm64e, "arm64e")
        except AssertionError:
            pass
        else:
            raise AssertionError("arm64e.old/incorrect subtype or filetype passed")
    arm64e.write_bytes(b"bad")
    try:
        audit.inspect(arm64e, "arm64e")
    except AssertionError:
        pass
    else:
        raise AssertionError("Truncated Mach-O passed")

workflow = (ROOT / ".github/workflows/protection-lab.yml").read_text(encoding="utf-8")
assert "workflow_dispatch:" in workflow and "runs-on: macos-14" in workflow
assert "xcrun --sdk iphoneos --find clang" in workflow
assert 'for arch in arm64 arm64e; do' in workflow
assert "lipo -thin arm64e" in workflow and "universal-extraction-report.json" in workflow
assert 'cmp "$out/protection-arm64e.dylib" "$out/reextracted-arm64e.dylib"' in workflow
assert "host-canary" in workflow and "PROTECTION_LAB_HOST_PASS" in workflow
assert "test_demo_ollvm.py" in workflow
assert "make clean package" not in workflow
assert "TARGET_CC=" not in workflow
assert "NOT TESTED" in workflow
assert workflow.count('--host-log "$out/host-vectors.txt"') == 2
assert "actions/upload-artifact@v4" in workflow
assert "github.com/lich4" not in workflow
assert "vmprotect" not in workflow.lower()
print(f"Protection lab: {len(vectors)} VM parity vectors, native arm64e ABI fixture gates, CI guard PASS")
