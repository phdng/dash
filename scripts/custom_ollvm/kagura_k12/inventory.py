#!/usr/bin/env python3
"""K12: enumerate exact Kagura pass registry pinned in macOS CI, no guesses.

This is a structural source inventory, NOT native/device validation. Only
K1/K5, K8-K11 and K6/K7 have preexisting evidence; every other registered
pass is "REGISTERED_UNVERIFIED". No change to Crane's Obfuscator plugin.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

PIN = "ac2136ee0408677cf7cdee55307e9b16edd5f4d5"
COVERED_K1 = ("str", "fla", "bcf", "sub", "co", "bbr", "bbs")
COVERED_K8_K11 = ("ibr", "mvo", "genc", "fsplit", "ci")
COVERED_VM = ("vm",)
COVERED = tuple("kagura-" + p for p in (*COVERED_K1, *COVERED_K8_K11, *COVERED_VM))
K8_KINDS = {"ibr": "FN", "mvo": "FN", "genc": "MOD",
            "fsplit": "MOD", "ci": "MOD"}
KIND = re.compile(r"\bKAGURA_(FN|MOD|INFRA)_PASS\s*\(")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
NAME = re.compile(r"kagura-[a-z0-9]+(?:-[a-z0-9]+)*")
HEX = re.compile(r"[a-f0-9]{64}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_ir_sha(path: Path) -> str:
    """Ignore ONLY llvm-dis's input-path ModuleID comment before IR delta.

    LLVM-dis writes '; ModuleID = \'baseline.bc\'' or a different output
    path for byte-identical semantic modules. Treat that as a non-pass
    delta. Keep every actual IR instruction/attribute/metadata line.
    Require exactly one ModuleID header in a nonempty real .ll file.
    """
    contents = path.read_text(encoding="utf-8")
    if not contents or "\x00" in contents:
        raise AssertionError("K12 invalid text LLVM IR input")
    lines = contents.splitlines(keepends=True)
    match = [i for i, line in enumerate(lines)
             if line.startswith("; ModuleID = ")]
    if match != [0]:
        raise AssertionError("K12 expected exactly one llvm-dis ModuleID header")
    normalized = "".join(lines[1:])
    if not normalized.strip():
        raise AssertionError("K12 empty LLVM IR after ModuleID strip")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def skip_comments(code: str) -> str:
    """Remove C++ comments, retaining quoted content and newline positions."""
    out, i, n = [], 0, len(code)
    while i < n:
        if code.startswith("//", i):
            stop = code.find("\n", i)
            if stop == -1:
                out.extend(" " * (n - i))
                break
            out.extend(" " * (stop - i))
            i = stop
        elif code.startswith("/*", i):
            stop = code.find("*/", i + 2)
            if stop < 0:
                raise AssertionError("K12 unterminated upstream comment")
            part = code[i:stop + 2]
            out.extend("\n" if c == "\n" else " " for c in part)
            i = stop + 2
        elif code[i] in ("'", '"'):
            quote, start = code[i], i
            i += 1
            while i < n:
                if code[i] == "\\":
                    i += 2
                elif code[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            else:
                raise AssertionError("K12 malformed quoted upstream token")
            out.append(code[start:i])
        else:
            out.append(code[i])
            i += 1
    return "".join(out)


def balanced_args(code: str, start: int) -> tuple[list[str], int]:
    """Split comma arguments without breaking on nested LLVM pass ctor calls."""
    depth, i, pos, args = 1, start, start, []
    in_quote = None
    while i < len(code):
        ch = code[i]
        if in_quote:
            if ch == "\\":
                i += 2
                continue
            if ch == in_quote:
                in_quote = None
        elif ch in ("'", '"'):
            in_quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                args.append(code[pos:i].strip())
                return args, i + 1
        elif ch == "," and depth == 1:
            args.append(code[pos:i].strip())
            pos = i + 1
        i += 1
    raise AssertionError("K12 upstream pass macro has unbalanced parentheses")


def parse_registry(content: str) -> list[dict]:
    code = skip_comments(content)
    items = []
    for match in KIND.finditer(code):
        # Only actual macro rows, not preprocessor definitions or helpers.
        prefix = code[code.rfind("\n", 0, match.start()) + 1:match.start()]
        if prefix.strip().startswith("#"):
            continue
        args, _end = balanced_args(code, match.end())
        kind = match.group(1)
        if kind == "INFRA":
            if len(args) < 2:
                raise AssertionError("K12 infrastructure pass macro incomplete")
            literal = args[0]
            flag = None
        else:
            if len(args) < 4 or not IDENT.fullmatch(args[0]):
                raise AssertionError("K12 function/module pass macro missing enable flag")
            flag, literal = args[:2]
        if not (literal.startswith('"') and literal.endswith('"') and
                NAME.fullmatch(literal[1:-1])):
            raise AssertionError("K12 malformed actual named upstream pass")
        items.append({"name": literal[1:-1], "kind": kind, "enable_flag": flag})
    if not items:
        raise AssertionError("K12 no pinned upstream named Kagura passes")
    names = [item["name"] for item in items]
    if len(set(names)) != len(names):
        raise AssertionError("K12 duplicated registry pass name")
    if not set(COVERED).issubset(names):
        raise AssertionError("K12 pinned upstream lacks previously verified pass(es): " +
                             repr(sorted(set(COVERED) - set(names))))
    kinds = {item["name"]: item["kind"] for item in items}
    for short, kind in K8_KINDS.items():
        if kinds["kagura-" + short] != kind:
            raise AssertionError("K12 upstream kind changed for K8/K11 " + short)
    if any(not NAME.fullmatch(x) for x in names):
        raise AssertionError("K12 invalid pass registry syntax")
    return items


def build_report(registry_text: str, registry_sha: str, license_sha: str) -> dict:
    if not HEX.fullmatch(registry_sha) or not HEX.fullmatch(license_sha):
        raise AssertionError("K12 requires real upstream file hashes")
    rows = parse_registry(registry_text)
    covered = []
    remaining = []
    for row in rows:
        name = row["name"]
        if name in COVERED:
            stage = ("K1_K5_SEVEN_STRUCTURAL_PASSES" if name.endswith(
                tuple("-" + p for p in COVERED_K1)) else
                "K6_K7_SEPARATE_VM" if name == "kagura-vm" else
                "K8_TO_K11_FIVE_PASSES_IOS_IPA")
            covered.append({**row, "coverage": stage,
                            "validation": "PREVIOUS_ARTIFACT_SCOPE_ONLY"})
        else:
            remaining.append({**row, "coverage": "NONE",
                              "validation": "REGISTERED_UNVERIFIED"})
    if len(covered) != len(COVERED):
        raise AssertionError("K12 lost historical coverage while enumerating")
    return {
        "schema": 1,
        "scope": "K12_PINNED_SOURCE_PASS_INVENTORY_NOT_NEW_PASS_VALIDATION",
        "pinned_commit": PIN,
        "upstream_pass_registry_sha256": registry_sha,
        "upstream_license_sha256": license_sha,
        "registered_pass_count": len(rows),
        "historically_evidenced_distinct_pass_count": len(covered),
        "remaining_registered_unverified_count": len(remaining),
        "historically_evidenced": covered,
        "remaining_registered_unverified": remaining,
        "infra_passes_never_auto_executed": True,
        "new_pass_native_parity_verified": False,
        "new_pass_iphone_executed": False,
        "arm64e_pac_verified": False,
        "crane_production_modified": False,
        "security_strength_claim": False,
    }


def inventory(src: Path, out: Path) -> dict:
    registry = src / "include/kagura/PassRegistry.def"
    license_file = src / "LICENSE"
    if not registry.is_file() or not license_file.is_file():
        raise AssertionError("K12 needs pinned upstream registry and MIT LICENSE")
    if not license_file.stat().st_size:
        raise AssertionError("K12 empty upstream LICENSE")
    text = registry.read_text(encoding="utf-8")
    report = build_report(text, sha(registry), sha(license_file))
    out.mkdir(parents=True, exist_ok=True)
    (out / "Kagura-K12-REMAINING-PASS-INVENTORY.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    # Preserve raw pinned bytes byte-for-byte across Windows/macOS;
    # newline translation would invalidate the SHA replay audit.
    (out / "Kagura-K12-PINNED-PASS-REGISTRY.def").write_bytes(
        registry.read_bytes())
    print("K12_PINNED_PASS_INVENTORY_PASS: registered=" +
          str(report["registered_pass_count"]) + "; historically evidenced=" +
          str(report["historically_evidenced_distinct_pass_count"]) +
          "; remaining unverified=" +
          str(report["remaining_registered_unverified_count"]))
    for row in report["remaining_registered_unverified"]:
        print("K12_REMAINING_REGISTERED_NOT_VERIFIED=" +
              row["name"] + ":" + row["kind"])
    return report


def verify(out: Path) -> dict:
    report_path = out / "Kagura-K12-REMAINING-PASS-INVENTORY.json"
    registry_path = out / "Kagura-K12-PINNED-PASS-REGISTRY.def"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    expected = build_report(registry_path.read_text(encoding="utf-8"),
                            sha(registry_path),
                            report.get("upstream_license_sha256", ""))
    if report != expected:
        raise AssertionError("K12 inventory corrupted or evidence status inflated")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--src", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify-report", action="store_true")
    a = p.parse_args()
    if a.verify_report:
        verify(a.out)
        print("K12_PINNED_REGISTRY_INVENTORY_REPLAY_PASS")
    else:
        if a.src is None:
            p.error("--src is required for inventory")
        inventory(a.src, a.out)


if __name__ == "__main__":
    main()
