#!/usr/bin/env python3
"""K19 isolate symbol-address intervals from *real post-link* arm64 Mach-O.

This does NOT infer function boundaries from codegen: each interval runs to
the next strictly higher symbol address in the same __TEXT,__text section,
or the section end. It may include alignment/padding or other functions.
Hashes are OFFLINE, unsigned, mutable reference measurements, NOT self
integrity, per-basic-block hashes, runtime anti-tamper, or PAC attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kagura_k16"))
import macho_measure as k16

SCOPE = "K19_OFFLINE_POST_LINK_SYMBOL_ADDRESS_INTERVAL_MEASUREMENT_ONLY"
NAME = "Kagura-K19-SYMBOL-RANGES.json"
INPUTS = {
    "macos_baseline": ("macos-baseline", ("_dd_k8_evaluate",)),
    "macos_csebreak": ("macos-cse-break", ("_dd_k8_evaluate",)),
    "ios_csebreak_lab": (
        "KaguraCSEBreakLab.app/KaguraCSEBreakLab",
        ("_dd_k8_evaluate", "_dd_k14_ios_parity")),
}
MAX_ENTRIES = 500000
MAX_STRING = 8 * 1024 * 1024
N_STAB = 0xe0
N_TYPE = 0x0e
N_SECT = 0x0e
N_EXT = 0x01
LC_SYMTAB = 0x2
LC_SEGMENT_64 = 0x19
TEXT_NAME = b"__text"
TEXT_SEG = b"__TEXT"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_slice(data: bytes, offset: int, size: int) -> bytes:
    if offset < 0 or size < 0 or offset > len(data) or size > len(data) - offset:
        raise AssertionError("K19 invalid file range")
    return data[offset:offset + size]


def decode_cname(raw: bytes, offset: int) -> str:
    if offset == 0 or offset >= len(raw):
        raise AssertionError("K19 empty/out-of-bounds symbol strx")
    # The first bytes can be linker padding (for example SPACE, NUL).
    # n_strx indexes the actual NUL-terminated name; it need not be
    # preceded by NUL (linkers may reuse a string suffix). Enforce
    # in-bounds, non-empty, ASCII, NUL-terminated names instead.
    end = raw.find(b"\0", offset)
    if end <= offset:
        raise AssertionError("K19 unterminated/empty symbol")
    try:
        return raw[offset:end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise AssertionError("K19 non-ASCII symbols not supported") from exc


def inspect(data: bytes, targets: tuple[str, ...]) -> dict:
    """Require K16 exact arm64 MH_EXECUTE, unique text section and LC_SYMTAB."""
    base = k16.inspect_macho(data)
    _, _, _, _, ncmds, sizeofcmds, _, _ = struct.unpack_from("<8I", data)
    at, end = 32, 32 + sizeofcmds
    ordinal = 0
    text = None
    symtab = None
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", data, at)
        if cmd == LC_SEGMENT_64:
            _, _, _, _, _, _, _, nsects, _ = struct.unpack_from(
                "<16sQQQQIIII", data, at + 8)
            for n in range(nsects):
                off = at + 72 + n * 80
                (sect, segment, vaddr, vsize, foff, _, _, _, flags, _, _, _) = (
                    struct.unpack_from("<16s16sQQIIIIIIII", data, off))
                ordinal += 1
                if sect.split(b"\0", 1)[0] == TEXT_NAME and (
                        segment.split(b"\0", 1)[0] == TEXT_SEG):
                    if text is not None:
                        raise AssertionError("K19 duplicate __TEXT,__text")
                    text = (ordinal, vaddr, vsize, foff)
        if cmd == LC_SYMTAB:
            if symtab is not None or cmdsize != 24:
                raise AssertionError("K19 duplicate/bad LC_SYMTAB")
            symtab = struct.unpack_from("<4I", data, at + 8)
        at += cmdsize
    if at != end or text is None or symtab is None:
        raise AssertionError("K19 missing text or real native LC_SYMTAB")
    section_id, text_addr, text_size, text_off = text
    if text_size != base["text_size"] or text_off != base["text_file_offset"]:
        raise AssertionError("K19 text section does not agree with K16")
    symoff, count, stroff, strsize = symtab
    if (count < 1 or count > MAX_ENTRIES or strsize < 2 or
            strsize > MAX_STRING or symoff < end or stroff < end):
        raise AssertionError("K19 corrupt symbol/string table sizes or overlapping commands")
    symbols_raw = exact_slice(data, symoff, count * 16)
    strs = exact_slice(data, stroff, strsize)
    # Apple ld64 may reserve a nonzero leading padding byte, typically
    # b" \\0". No Mach-O contract requires strs[0] to equal 0.
    # decode_cname guards strx bounds and terminator, not padding bytes.
    if (symoff < stroff + strsize and stroff < symoff + count * 16):
        raise AssertionError("K19 overlapping nlist and string table")
    all_text = []
    ignored_out_of_range_text_nlists = 0
    for k in range(count):
        strx, typ, sect, desc, val = struct.unpack_from("<IBBHQ",
                                                         symbols_raw, k * 16)
        if (typ & N_STAB) or (typ & N_TYPE) != N_SECT or sect != section_id:
            continue
        # Decode the name BEFORE deciding whether an nlist address can
        # delimit machine code. ld64 can emit N_SECT records whose n_value
        # points at the __text end marker or outside its file-backed range.
        # Such unrelated records must not poison the symbol-address oracle;
        # requested ABI targets must still be strictly inside __text.
        if strx == 0:
            # An unnamed LOCAL text symbol may still delimit the next
            # higher code address; an external target must be named.
            if typ & N_EXT:
                raise AssertionError("K19 external text nlist has zero strx")
            name = ""
        else:
            name = decode_cname(strs, strx)
        if not (text_addr <= val < text_addr + text_size):
            if name in targets:
                raise AssertionError("K19 required target outside __text: " + name)
            ignored_out_of_range_text_nlists += 1
            continue
        all_text.append((val, name, bool(typ & N_EXT), desc))
    addresses = sorted(set(v for v, _, _, _ in all_text))
    results = {}
    for target in targets:
        hits = [(v, name, desc) for v, name, ext, desc in all_text
                if name == target and ext]
        if len(hits) != 1:
            raise AssertionError("K19 target missing, duplicate or non-exported: " + target)
        address, _, desc = hits[0]
        if [name for val, name, _, _ in all_text if val == address] != [target]:
            raise AssertionError("K19 aliases/duplicate entries at target address")
        next_addresses = [v for v in addresses if v > address]
        stop = min(next_addresses) if next_addresses else text_addr + text_size
        relative = address - text_addr
        length = stop - address
        if (relative % 4 != 0 or length < 4 or length % 4 != 0 or
                relative > text_size or length > text_size - relative):
            raise AssertionError("K19 invalid/unaligned target symbol interval")
        off = text_off + relative
        raw = exact_slice(data, off, length)
        results[target] = {
            "symbol": target,
            "kind": "LC_SYMTAB_NEXT_ADDRESS_BOUND_NOT_FUNCTION_SIZE",
            "text_section_ordinal": section_id,
            "symbol_vmaddr": address,
            "end_vmaddr_exclusive": stop,
            "file_offset": off,
            "length": length,
            "sha256": digest(raw),
            "n_desc": desc,
        }
    return {"macho_uuid": base["uuid"],
            "binary_sha256": base["binary_sha256"],
            "text_sha256": base["text_sha256"],
            "text_offset": text_off,
            "text_size": text_size,
            "nlist_count": count,
            "text_symbol_count": len(all_text),
            "ignored_out_of_range_text_nlists": ignored_out_of_range_text_nlists,
            "observed_symbols": results}


def manifest(out: Path) -> dict:
    # Every K19 run starts with the real K13 native, K14 IPA and K16
    # raw manifest replayer; never substitute fabricated PASS JSON.
    k16.replay(out)
    m16 = (out / k16.MANIFEST).read_bytes()
    records = {}
    for key, (path, symbols) in INPUTS.items():
        p = out / path
        if not p.is_file() or p.is_symlink():
            raise AssertionError("K19 missing genuine linked executable: " + path)
        current = inspect(p.read_bytes(), symbols)
        old = json.loads(m16)["linked_binaries"][key]
        if (current["macho_uuid"] != old["uuid"] or
            current["binary_sha256"] != old["binary_sha256"] or
            current["text_sha256"] != old["text_sha256"] or
            current["text_offset"] != old["text_file_offset"] or
            current["text_size"] != old["text_size"]):
            raise AssertionError("K19 symbol map not bound to K16 reference")
        records[key] = current
    if (records["macos_baseline"]["observed_symbols"]["_dd_k8_evaluate"]["sha256"] ==
        records["macos_csebreak"]["observed_symbols"]["_dd_k8_evaluate"]["sha256"]):
        raise AssertionError("K19 protected source canary symbol bytes did not change")
    return {
        "schema": 1,
        "scope": SCOPE,
        "k18_dependency": "NONE_SKIPPED_BY_USER_NOT_TESTED",
        "k16_unsigned_manifest_sha256": digest(m16),
        "source_type": "REAL_MACHO_LC_SYMTAB_N_SECT_EXPORT_ADDRESS_BOUND",
        "addresses_are_boundaries_not_precise_function_lengths": True,
        "authentic_cryptographic_reference": False,
        "per_basic_block_integrity": False,
        "runtime_verifier_implemented": False,
        "security_anti_tamper_proven": False,
        "iphone_device_execution": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "targets": records,
    }


def record(out: Path) -> dict:
    p = out / NAME
    if p.exists():
        raise AssertionError("K19 refuses to overwrite a previous symbol manifest")
    generated = manifest(out)
    p.write_text(json.dumps(generated, indent=2, sort_keys=True) + "\n",
                 encoding="utf-8")
    return generated


def verify(out: Path) -> dict:
    p = out / NAME
    if not p.is_file() or p.is_symlink() or p.stat().st_size > 512000:
        raise AssertionError("K19 original symbol manifest missing/oversize")
    saved = json.loads(p.read_text(encoding="utf-8"))
    actual = manifest(out)
    if type(saved) is not dict or saved != actual:
        raise AssertionError("K19 raw nlist symbol-range replay mismatch")
    return saved


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    if args.verify:
        verify(args.out)
        print("K19_OFFLINE_NLIST_SYMBOL_BOUNDED_RANGES_REPLAY_PASS: no K18, no runtime/security")
    else:
        record(args.out)
        print("K19_SYMBOL_RANGE_REFERENCE_WRITTEN: macOS/iOS real Mach-O inputs required")


if __name__ == "__main__":
    main()
