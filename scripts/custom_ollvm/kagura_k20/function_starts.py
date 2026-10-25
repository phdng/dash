#!/usr/bin/env python3
"""K20 fail-closed OFFLINE corroboration: LC_FUNCTION_STARTS versus K19 nlist.

LC_FUNCTION_STARTS is a ULEB128 stream of function-start offsets relative to
the __TEXT segment's vmaddr. It does NOT authenticate bytes, give explicit
function lengths or prove runtime integrity. The K19 interval's *next-symbol*
end is a candidate boundary, corroborated only if it appears as another
LC_FUNCTION_STARTS function start. This is source-level agreement in one
unsigned Mach-O, not an independent trust anchor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kagura_k19"))
import symbol_ranges as k19  # noqa: E402

SCOPE = "K20_OFFLINE_LC_FUNCTION_STARTS_NLIST_CORROBORATION_NO_RUNTIME_SECURITY"
NAME = "Kagura-K20-FUNCTION-START-CROSSCHECK.json"
LC_FUNCTION_STARTS = 0x26
LC_SEGMENT_64 = 0x19
MAX_STREAM = 8 * 1024 * 1024
MAX_STARTS = 250000
MAX_VM = (1 << 64) - 1


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def decode_uleb(data: bytes, offset: int) -> tuple[int, int]:
    """Decode one canonical unsigned 64-bit LEB128; reject overflow/truncation."""
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise AssertionError("K20 truncated ULEB128 function start")
        byte = data[offset]
        offset += 1
        fragment = byte & 0x7f
        if shift == 63 and fragment > 1:
            raise AssertionError("K20 ULEB128 unsigned 64-bit overflow")
        if shift > 63 and fragment:
            raise AssertionError("K20 ULEB128 overflow")
        value |= fragment << shift
        if not byte & 0x80:
            if shift and not fragment:
                raise AssertionError("K20 noncanonical ULEB128 encoding")
            return value, offset
    raise AssertionError("K20 overlong ULEB128")


def inspect_macho(data: bytes, k19_ranges: dict) -> dict:
    """Crosscheck actual raw MH_EXECUTE + bounded linkedit-data function starts."""
    base = k19.k16.inspect_macho(data)
    if (k19_ranges.get("macho_uuid") != base["uuid"] or
        k19_ranges.get("binary_sha256") != base["binary_sha256"] or
        k19_ranges.get("text_sha256") != base["text_sha256"] or
        k19_ranges.get("text_offset") != base["text_file_offset"] or
        k19_ranges.get("text_size") != base["text_size"]):
        raise AssertionError("K20 K19 symbol report not bound to genuine raw Mach-O")
    (_, _, _, _, ncmds, sizeofcmds, _, _) = struct.unpack_from("<8I", data, 0)
    end = 32 + sizeofcmds
    at = 32
    text_segment = None
    starts_lc = None
    for _ in range(ncmds):
        cmd, size = struct.unpack_from("<II", data, at)
        if cmd == LC_SEGMENT_64:
            (_, _, segname, vmaddr, vmsize, fileoff, filesize, _, _, nsects, _) = (
                struct.unpack_from("<II16sQQQQIIII", data, at))
            if segname.split(b"\0", 1)[0] == b"__TEXT":
                if text_segment is not None:
                    raise AssertionError("K20 duplicate __TEXT segment")
                if vmsize == 0 or vmaddr > MAX_VM - vmsize:
                    raise AssertionError("K20 invalid __TEXT virtual bounds")
                text_segment = (vmaddr, vmsize, fileoff, filesize)
        if cmd == LC_FUNCTION_STARTS:
            if starts_lc is not None or size != 16:
                raise AssertionError("K20 duplicate/malformed LC_FUNCTION_STARTS")
            starts_lc = struct.unpack_from("<II", data, at + 8)
        at += size
    if at != end or text_segment is None or starts_lc is None:
        raise AssertionError("K20 requires one __TEXT and one LC_FUNCTION_STARTS")
    vmaddr, vmsize, text_fileoff, _ = text_segment
    dataoff, datasize = starts_lc
    if (datasize < 2 or datasize > MAX_STREAM or
        dataoff < end or dataoff > len(data) or
        datasize > len(data) - dataoff):
        raise AssertionError("K20 LC_FUNCTION_STARTS dataoff/datasize invalid")
    # The segment and section have to use consistent file-to-VM mapping.
    if vmaddr + (base["text_file_offset"] - text_fileoff) >= vmaddr + vmsize:
        raise AssertionError("K20 invalid __TEXT/__text mapping")
    raw = data[dataoff:dataoff + datasize]
    offsets = []
    pos = 0
    cumulative = 0
    terminated = False
    while pos < len(raw):
        delta, pos = decode_uleb(raw, pos)
        if delta == 0:
            if any(raw[pos:]):
                raise AssertionError("K20 nonzero bytes after ULEB128 terminator")
            terminated = True
            break
        if len(offsets) >= MAX_STARTS or delta > MAX_VM - cumulative:
            raise AssertionError("K20 too many/overflowed LC_FUNCTION_STARTS")
        cumulative += delta
        if cumulative >= vmsize or cumulative % 4:
            raise AssertionError("K20 unaligned/out-of-range function start")
        offsets.append(cumulative)
    if not terminated or not offsets:
        raise AssertionError("K20 empty/unterminated LC_FUNCTION_STARTS stream")
    absolute = {vmaddr + off for off in offsets}
    if len(absolute) != len(offsets):
        raise AssertionError("K20 duplicate function starts")
    matches = {}
    for name, recorded in k19_ranges["observed_symbols"].items():
        symbol_addr = recorded["symbol_vmaddr"]
        next_addr = recorded["end_vmaddr_exclusive"]
        length = recorded["length"]
        offset = recorded["file_offset"]
        if (not isinstance(symbol_addr, int) or not isinstance(next_addr, int) or
            not isinstance(length, int) or not isinstance(offset, int) or
            next_addr <= symbol_addr or next_addr - symbol_addr != length or
            symbol_addr not in absolute or next_addr not in absolute):
            raise AssertionError("K20 K19 symbol interval lacks LC_FUNCTION_STARTS boundary: " + name)
        relative = symbol_addr - (vmaddr + base["text_file_offset"] - text_fileoff)
        if (relative < 0 or relative + length > base["text_size"] or
            offset != base["text_file_offset"] + relative or
            sha(data[offset:offset + length]) != recorded["sha256"]):
            raise AssertionError("K20 symbol range raw bytes mismatch: " + name)
        matches[name] = {
            "symbol": name,
            "start_vmaddr": symbol_addr,
            "next_symbol_vmaddr_exclusive": next_addr,
            "start_in_lc_function_starts": True,
            "next_symbol_start_in_lc_function_starts": True,
            "file_offset": offset,
            "length": length,
            "sha256": recorded["sha256"],
            "function_size_proven": False,
        }
    if not matches:
        raise AssertionError("K20 zero corroborated ABI targets")
    return {
        "macho_uuid": base["uuid"],
        "binary_sha256": base["binary_sha256"],
        "text_sha256": base["text_sha256"],
        "lc_function_starts_dataoff": dataoff,
        "lc_function_starts_datasize": datasize,
        "lc_function_starts_payload_sha256": sha(raw),
        "lc_function_starts_count": len(offsets),
        "lc_function_starts_offsets": offsets,
        "symbol_intervals_corroborated": matches,
    }


def regenerate(out: Path) -> dict:
    # k19.verify -> k16.replay -> real K13/K14 source and raw bytes.
    saved19 = k19.verify(out)
    raw19 = (out / k19.NAME).read_bytes()
    records = {}
    for key, (name, symbols) in k19.INPUTS.items():
        path = out / name
        if not path.is_file() or path.is_symlink():
            raise AssertionError("K20 genuine K19 Mach-O missing: " + name)
        check = inspect_macho(path.read_bytes(), saved19["targets"][key])
        if set(check["symbol_intervals_corroborated"]) != set(symbols):
            raise AssertionError("K20 ABI symbol set differs from K19")
        records[key] = check
    baseline = records["macos_baseline"]["symbol_intervals_corroborated"]["_dd_k8_evaluate"]
    protected = records["macos_csebreak"]["symbol_intervals_corroborated"]["_dd_k8_evaluate"]
    if baseline["sha256"] == protected["sha256"]:
        raise AssertionError("K20 CSEBreak native machine code not different")
    return {
        "schema": 1,
        "scope": SCOPE,
        "k18_dependency": "NONE_SKIPPED_BY_USER_NOT_TESTED",
        "source_k19_manifest_sha256": sha(raw19),
        "reference_authenticated": False,
        "two_data_sources_in_same_binary_not_independent_trust": True,
        "exact_function_size_proven": False,
        "per_basic_block_integrity": False,
        "runtime_self_verifier": False,
        "iphone_device_execution": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "specimens": records,
    }


def record(out: Path) -> dict:
    p = out / NAME
    if p.exists() or p.is_symlink():
        raise AssertionError("K20 refuses to overwrite existing result")
    result = regenerate(out)
    p.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def verify(out: Path) -> dict:
    p = out / NAME
    if not p.is_file() or p.is_symlink() or p.stat().st_size > 512000:
        raise AssertionError("K20 recorded result missing/invalid")
    raw = json.loads(p.read_text(encoding="utf-8"))
    expected = regenerate(out)
    if type(raw) is not dict or raw != expected:
        raise AssertionError("K20 source-grounded LC_FUNCTION_STARTS replay mismatch")
    return raw


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    if args.verify:
        verify(args.out)
        print("K20_LC_FUNCTION_STARTS_K19_DUAL_SOURCE_OFFLINE_REPLAY_PASS: no runtime security")
    else:
        record(args.out)
        print("K20_LC_FUNCTION_STARTS_K19_OFFLINE_MANIFEST_CREATED: macOS not yet verified")


if __name__ == "__main__":
    main()
