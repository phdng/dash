#!/usr/bin/env python3
"""K16 offline Mach-O __TEXT,__text measurement: no runtime/BBCheck claims.

The measurement manifest is UNSIGNED. This is a byte-corruption/difference
oracle against separately retained expected digests, NOT adversarial tamper
resistance: an attacker controlling both binary and manifest can change both.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import uuid
from pathlib import Path

HEADER_SIZE = 32
SEGMENT64_SIZE = 72
SECTION64_SIZE = 80
MAX_FILE = 128 * 1024 * 1024
MAX_CMDS = 4096
MAGIC64_LE = 0xFEEDFACF
ARM64_CPU = 0x0100000C
MH_EXECUTE = 2
LC_SEGMENT_64 = 0x19
LC_UUID = 0x1B
SCHEMA = 1
SCOPE = "K16_OFFLINE_POST_LINK_TEXT_MEASUREMENTS_NO_RUNTIME_PROTECTION"
FILE_NAMES = {
    "macos_baseline": "macos-baseline",
    "macos_csebreak": "macos-cse-break",
    "ios_csebreak_lab": "KaguraCSEBreakLab.app/KaguraCSEBreakLab",
}
MANIFEST = "Kagura-K16-OFFLINE-TEXT-MANIFEST.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def name16(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("ascii")


def inspect_macho(data: bytes) -> dict:
    """Parse thin arm64 MH_EXECUTE; select one file-backed __TEXT,__text."""
    if not isinstance(data, bytes) or not (HEADER_SIZE <= len(data) <= MAX_FILE):
        raise AssertionError("K16 Mach-O data missing/oversize")
    magic, cpu, subtype, filetype, ncmds, sizeofcmds, flags, reserved = (
        struct.unpack_from("<8I", data))
    if (magic, cpu, subtype, filetype) != (
            MAGIC64_LE, ARM64_CPU, 0, MH_EXECUTE):
        raise AssertionError("K16 only arm64 subtype0 MH_EXECUTE; no fat/arm64e/object")
    if (ncmds < 1 or ncmds > MAX_CMDS or sizeofcmds < 24 or
            sizeofcmds > 4 * 1024 * 1024 or
            HEADER_SIZE + sizeofcmds > len(data)):
        raise AssertionError("K16 corrupt Mach-O load-command range")
    start, end = HEADER_SIZE, HEADER_SIZE + sizeofcmds
    cursor = start
    found, uuids = [], []
    for _ in range(ncmds):
        if cursor + 8 > end:
            raise AssertionError("K16 truncated load command")
        cmd, size = struct.unpack_from("<II", data, cursor)
        if size < 8 or size % 8 or cursor + size > end:
            raise AssertionError("K16 malformed load command")
        if cmd == LC_UUID:
            if size != 24:
                raise AssertionError("K16 malformed LC_UUID")
            uuids.append(str(uuid.UUID(bytes=data[cursor + 8:cursor + 24])))
        if cmd == LC_SEGMENT_64:
            if size < SEGMENT64_SIZE:
                raise AssertionError("K16 truncated segment_command_64")
            (segment, vmaddr, vmsize, fileoff, filesize, maxprot, initprot,
             nsects, segflags) = struct.unpack_from("<16sQQQQIIII",
                                                      data, cursor + 8)
            segment_name = name16(segment)
            if (nsects > 8192 or
                    SEGMENT64_SIZE + nsects * SECTION64_SIZE != size or
                    fileoff > len(data) or filesize > len(data) - fileoff):
                raise AssertionError("K16 segment section count/file range invalid")
            for k in range(nsects):
                p = cursor + SEGMENT64_SIZE + k * SECTION64_SIZE
                (sectname, sectseg, secaddr, secsize, offset, align,
                 reloff, nreloc, secflags, reserved1, reserved2,
                 reserved3) = struct.unpack_from("<16s16sQQIIIIIIII", data, p)
                if name16(sectname) == "__text" and name16(sectseg) == "__TEXT":
                    if segment_name != "__TEXT":
                        raise AssertionError("K16 mismatched segment name for text")
                    if (secsize < 16 or secsize > MAX_FILE or
                            offset < end or offset < fileoff or
                            offset > len(data) or
                            secsize > len(data) - offset or
                            secsize > fileoff + filesize - offset):
                        raise AssertionError("K16 __TEXT,__text offset/size out of range")
                    if (secsize > vmsize or secaddr < vmaddr or
                            secaddr - vmaddr > vmsize - secsize or
                            secaddr - vmaddr != offset - fileoff):
                        raise AssertionError("K16 __text vmaddr not within segment")
                    found.append((offset, secsize))
        cursor += size
    if cursor != end or len(uuids) != 1 or len(found) != 1:
        raise AssertionError("K16 requires exactly one UUID and one __TEXT,__text")
    offset, length = found[0]
    return {
        "architecture": "arm64:0x00000000",
        "filetype": "MH_EXECUTE",
        "uuid": uuids[0],
        "binary_size": len(data),
        "binary_sha256": sha(data),
        "text_section": "__TEXT,__text",
        "text_file_offset": offset,
        "text_size": length,
        "text_sha256": sha(data[offset:offset + length]),
    }


def measure(out: Path, *, write: bool = True) -> dict:
    """Bind real K13/K14 provenance to three post-linked Mach-O files."""
    k13path = out / "Kagura-K13-REPORT.json"
    k14path = out / "Kagura-K14-IPA-report.json"
    k14ev = out / "Kagura-K14-IPA-EVIDENCE.json"
    k15file = Path(__file__).resolve().parents[3] / "docs/KAGURA_K15_ARTIFACT_REVIEW.md"
    if any(not p.is_file() for p in (k13path, k14path, k14ev, k15file)):
        raise AssertionError("K16 needs real K13/K14 manifests and K15 stub blocker doc")
    k13 = json.loads(k13path.read_text(encoding="utf-8"))
    k14 = json.loads(k14path.read_text(encoding="utf-8"))
    evidence = json.loads(k14ev.read_text(encoding="utf-8"))
    if (k13.get("scope") !=
            "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY" or
            k13.get("pass") != "kagura-cse-break" or
            k13.get("pass_class") != "kagura::CSEBreakPass" or
            k13.get("targets", {}).get("macos", {}).get("native_parity") != "PASS" or
            k13["targets"]["macos"].get("native_vectors") != 4096 or
            k13["targets"]["macos"].get("baseline_checksum") !=
            k13["targets"]["macos"].get("protected_checksum") or
            k13["targets"]["macos"].get("baseline_checksum") !=
            "25a3318e3d7d6525" or
            k14.get("scope") != "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB" or
            k14.get("signing") != "UNSIGNED" or
            evidence.get("k13_cse_break_ios_object_embedded") is not True or
            evidence.get("ipa_sha256") != k14.get("ipa_sha256") or
            evidence.get("app_binary_sha256") != k14.get("binary_sha256") or
            evidence.get("ios_device_execution") != "NOT_TESTED_BY_CI" or
            evidence.get("security_attestation") is not False or
            "ALWAYS-PASS" not in k15file.read_text(encoding="utf-8").upper().replace(
                " ", "-")):
        raise AssertionError("K16 K13/K14 source scope or K15 weak-stub guard failed")
    result = {key: inspect_macho((out / path).read_bytes())
              for key, path in FILE_NAMES.items()}
    if (result["ios_csebreak_lab"]["uuid"] != k14.get("app_macho_uuid") or
            result["ios_csebreak_lab"]["binary_sha256"] != k14.get("binary_sha256")):
        raise AssertionError("K16 iOS final linked executable differs from verified IPA")
    if (result["macos_baseline"]["binary_sha256"] ==
            result["macos_csebreak"]["binary_sha256"] or
            result["macos_baseline"]["text_sha256"] ==
            result["macos_csebreak"]["text_sha256"]):
        raise AssertionError("K16 CSEBreak did not change actual linked code bytes")
    if k13.get("security_strength_claim") is not False:
        raise AssertionError("K16 cannot upgrade checksum parity into security claim")
    manifest = {
        "schema": SCHEMA,
        "scope": SCOPE,
        "reference_kind": "UNSIGNED_OFFLINE_POST_LINK_MEASUREMENT",
        "sources": {"k13_report_sha256": sha(k13path.read_bytes()),
                    "k14_ipa_report_sha256": sha(k14path.read_bytes()),
                    "k14_evidence_sha256": sha(k14ev.read_bytes()),
                    "k15_weak_stub_review_sha256": sha(k15file.read_bytes())},
        "linked_binaries": result,
        "bbcheck_security_integrity": "BLOCKED_K15_WEAK_ALWAYS_PASS_STUB",
        "metadata_authenticated": False,
        "runtime_verifier_implemented": False,
        "per_basic_block_identity_and_hashing": False,
        "adversarial_tamper_protection_proven": False,
        "iphone_device_executed_for_k16": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
    }
    if write:
        (out / MANIFEST).write_text(json.dumps(manifest, sort_keys=True,
                                               indent=2) + "\n", encoding="utf-8")
    return manifest


def replay(out: Path) -> dict:
    p = out / MANIFEST
    if not p.is_file():
        raise AssertionError("K16 manifest missing")
    m = json.loads(p.read_text(encoding="utf-8"))
    # Recompute all authoritative file hashes and parsed sections, not JSON PASS.
    if not isinstance(m, dict) or m != measure(out, write=False):
        raise AssertionError("K16 original manifest not equal to real linked bytes")
    return m


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    if args.verify:
        replay(args.out)
        print("K16_OFFLINE_MACHO_TEXT_REPLAY_PASS: no runtime tamper/IPA new pass/security claim")
    else:
        measure(args.out)
        print("K16_OFFLINE_MACHO_TEXT_MEASUREMENT_STAGED: three real linked executables; no security claim")


if __name__ == "__main__":
    main()
