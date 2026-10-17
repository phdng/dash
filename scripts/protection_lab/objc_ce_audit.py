#!/usr/bin/env python3
"""Fail-closed binary audit for isolated Objective-C literal CE experiment.

A marker disappearing from a Mach-O is not proof of secrecy or security.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import audit as macho
import objc_ce_generator as fixture

HOST_PASS = "OBJC_CE_HOST_PASS: 8192 NSString/ARC/UTF8 parity vectors"


def check_pair(plain: Path, protected: Path, arch: str) -> dict:
    before, after = plain.read_bytes(), protected.read_bytes()
    original = macho.inspect(plain, arch)
    transformed = macho.inspect(protected, arch)
    marker = fixture.TEXTS[0].encode("utf-8")
    if before == after:
        raise AssertionError(f"{arch}: Objective-C baseline and CE binary identical")
    if before.count(marker) < 1:
        raise AssertionError(f"{arch}: baseline missing exact NSString marker bytes")
    for index, text in enumerate(fixture.TEXTS):
        raw = text.encode("utf-8")
        if raw in after:
            raise AssertionError(f"{arch}: plaintext index={index} leaked")
        if fixture.encode(index) not in after:
            raise AssertionError(f"{arch}: encoded index={index} missing")
    return {
        "arch": arch,
        "baseline": original,
        "ce_variant": transformed,
        "marker_baseline_occurrences": before.count(marker),
        "marker_protected_occurrences": after.count(marker),
        "three_encoded_byte_sequences_present": True,
        "source_level_objc_ce_only": True,
        "compiler": "Apple Clang ARC",
        "sllvm_plugin_loaded": False,
        "vmprotect_plugin_loaded": False,
        "objc_runtime_on_ios": "NOT_TESTED",
        "arm64e_pac_runtime": "NOT_TESTED_A12_PLUS_REQUIRED",
        "security_score": None,
    }


def make_report(pairs: dict[str, tuple[Path, Path]], log: Path,
                header: Path, destination: Path) -> dict:
    if log.read_text(encoding="utf-8").strip() != HOST_PASS:
        raise AssertionError("Missing or malformed native host Foundation/ARC parity log")
    header_bytes = header.read_bytes()
    expected = fixture.render().encode("utf-8")
    if header_bytes != expected:
        raise AssertionError("Encoded fixture header inconsistent with pinned generator")
    result = {
        "schema": 1,
        "scope": "standalone_foundation_objc_ce_canary_only",
        "host_vectors": 8192,
        "host_test": "PASS_MACOS_FOUNDATION_ARC_ONLY",
        "generated_header_sha256": hashlib.sha256(header_bytes).hexdigest(),
        "slices": {arch: check_pair(*pairs[arch], arch)
                   for arch in ("arm64", "arm64e")},
        "ios_device_runtime": "NOT_TESTED",
        "pac_runtime": "NOT_TESTED_A12_PLUS_REQUIRED",
        "crane_production_changed": False,
        "security_claim": "source-level visibility test, no cryptographic secrecy",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("OBJC_CE_BINARY_PASS: Apple arm64/arm64e Mach-O CE byte delta, "
          "host ARC parity; iOS device runtime NOT_TESTED")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for arch in ("arm64", "arm64e"):
        for variant in ("plain", "protected"):
            p.add_argument(f"--{arch}-{variant}", type=Path, required=True)
    p.add_argument("--host-log", type=Path, required=True)
    p.add_argument("--header", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_report({
        arch: (getattr(a, arch + "_plain"), getattr(a, arch + "_protected"))
        for arch in ("arm64", "arm64e")
    }, a.host_log, a.header, a.out)
