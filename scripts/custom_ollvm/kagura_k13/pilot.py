#!/usr/bin/env python3
"""K13 isolated Kagura CSEBreakPass real LLVM19 native/arm64 object pilot.

Run ONLY on macOS GitHub Actions with the exact Kagura pinned commit.
No IPA, iPhone execution, arm64e PAC or Crane production integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from sys import path as module_search_path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
module_search_path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k12"))
from inventory import PIN, parse_registry, normalized_ir_sha  # noqa: E402

PASS = "kagura-cse-break"
PASS_CLASS = "kagura::CSEBreakPass"
REGISTRY_SHA = "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa"
PIPELINE = "function(kagura-cse-break),verify"
VECTORS = 4096
NATIVE_RE = re.compile(
    r"\ADD_K8_SCHEMA=1\nDD_K8_VECTORS=4096\n"
    r"DD_K8_CHECKSUM=([0-9a-f]{16})\nDD_K8_COMPLETE=PASS\n\Z"
)
LLVM_SYMBOL = re.compile(r"(?m)^define\s+[^\n]*@dd_k8_evaluate\(")
TRACE = re.compile(
    r"(?m)^Running pass: (?:kagura::)?CSEBreakPass on dd_k8_evaluate \(")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_registry(source: str) -> dict:
    rows = parse_registry(source)
    hits = [row for row in rows if row["name"] == PASS]
    if len(hits) != 1 or hits[0]["kind"] != "FN" or (
            hits[0]["enable_flag"] != "CSEBreak"):
        raise AssertionError("K13 Kagura pinned CSEBreak FN/type/enable drift")
    return hits[0]


def validate_native(raw: str) -> str:
    match = NATIVE_RE.fullmatch(raw)
    if not match:
        raise AssertionError("K13 native runner log schema or 4096 vectors incorrect")
    return match.group(1)


def validate_trace(raw: str) -> None:
    if (not TRACE.search(raw) or
            "Running pass: VerifierPass on [module]" not in raw or
            "Running pass: BitcodeWriterPass on [module]" not in raw):
        raise AssertionError(
            "K13 actual LLVM19 CSEBreakPass on target plus verifier not demonstrated")


def native_macho(data: bytes) -> None:
    if len(data) < 32 or int.from_bytes(data[0:4], "little") != 0xFEEDFACF or (
            int.from_bytes(data[4:8], "little") not in
            (0x01000007, 0x0100000C)) or (
            int.from_bytes(data[12:16], "little") != 1):
        raise AssertionError("K13 native object not x86_64/arm64 MH_OBJECT")


def ios_macho(data: bytes) -> None:
    if len(data) < 32:
        raise AssertionError("K13 missing Mach-O arm64 object")
    if (int.from_bytes(data[0:4], "little") != 0xFEEDFACF or
            int.from_bytes(data[4:8], "little") != 0x0100000C or
            int.from_bytes(data[8:12], "little") != 0 or
            int.from_bytes(data[12:16], "little") != 1):
        raise AssertionError("K13 iOS must be arm64 subtype0 MH_OBJECT, not arm64e")


def run_cmd(args: list[str], log: Path, *, timeout: int = 90) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True,
                                check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        log.write_text("K13_COMMAND_TIMEOUT\n", encoding="utf-8")
        raise AssertionError("K13 command timed out: " + args[0]) from None
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise AssertionError(
            f"K13 tool exit={result.returncode} at {args[0]}: " +
            result.stderr[-700:])
    return result.stdout


def run(src: Path, llvm: Path, plugin: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    registry_file = src / "include/kagura/PassRegistry.def"
    license_file = src / "LICENSE"
    if not registry_file.is_file() or not license_file.is_file() or (
            not license_file.stat().st_size):
        raise AssertionError("K13 pinned upstream Kagura registry/license required")
    entry = validate_registry(registry_file.read_text(encoding="utf-8"))
    if sha(registry_file) != REGISTRY_SHA:
        raise AssertionError("K13 registry differs from real K12 pinned artifact")
    if not plugin.is_file() or not plugin.stat().st_size:
        raise AssertionError("K13 missing built pinned LLVM19 plugin")
    clang = llvm / "bin/clang"
    opt = llvm / "bin/opt"
    dis = llvm / "bin/llvm-dis"
    for tool in (clang, opt, dis):
        if not tool.is_file():
            raise AssertionError("K13 requires actual LLVM19 clang/opt/llvm-dis")
    fixture = ROOT / "scripts/custom_ollvm/kagura_k8/fixture.c"
    runner = ROOT / "scripts/custom_ollvm/kagura_k8/runner.c"
    if not fixture.is_file() or not runner.is_file():
        raise AssertionError("K13 uses frozen K8 public-data canary + native runner")
    (out / "pinned-registry.def").write_bytes(registry_file.read_bytes())
    (out / "pinned-LICENSE").write_bytes(license_file.read_bytes())

    sdk_paths = {}
    for label, sdk in (("macos", "macosx"), ("ios", "iphoneos")):
        sdk_path = run_cmd(
            ["xcrun", "--sdk", sdk, "--show-sdk-path"],
            out / (label + "-sdk.log")).strip()
        if not sdk_path or "\n" in sdk_path or not Path(sdk_path).is_dir():
            raise AssertionError("K13 invalid Apple SDK path for " + sdk)
        sdk_paths[label] = sdk_path

    runner_obj = out / "native-runner.o"
    run_cmd(["xcrun", "clang", "-O1", "-Wall", "-Wextra", "-Werror",
             "-std=c11", "-c", str(runner), "-o", str(runner_obj)],
            out / "native-runner-clang.log")
    records = {}
    for target in ("macos", "ios"):
        is_ios = target == "ios"
        args = (["-target", "arm64-apple-ios15.0"] if is_ios else [])
        base_bc = out / (target + "-baseline.bc")
        post_bc = out / (target + "-cse-break.bc")
        base_ll = out / (target + "-baseline.ll")
        post_ll = out / (target + "-cse-break.ll")
        base_obj = out / (target + "-baseline.o")
        post_obj = out / (target + "-cse-break.o")
        opts = [str(clang), "-O1", "-std=c11", "-Wall", "-Wextra",
                "-Werror", "-fno-builtin-strlen", *args,
                "-isysroot", sdk_paths[target]]
        run_cmd([*opts, "-emit-llvm", "-c", str(fixture), "-o",
                 str(base_bc)], out / (target + "-baseline-clang.log"))
        run_cmd([str(dis), str(base_bc), "-o", str(base_ll)],
                out / (target + "-baseline-llvm-dis.log"))
        run_cmd([str(opt), "--load-pass-plugin=" + str(plugin),
                 "-kagura-seed=82712", "-kagura-cse-break",
                 "-debug-pass-manager", "-passes=" + PIPELINE,
                 str(base_bc), "-o", str(post_bc)],
                out / (target + "-pass-manager.log"))
        run_cmd([str(dis), str(post_bc), "-o", str(post_ll)],
                out / (target + "-cse-break-llvm-dis.log"))
        trace = (out / (target + "-pass-manager.log")).read_text(
            encoding="utf-8")
        validate_trace(trace)
        before = base_ll.read_text(encoding="utf-8")
        after = post_ll.read_text(encoding="utf-8")
        if (not LLVM_SYMBOL.search(before) or
                not LLVM_SYMBOL.search(after) or
                normalized_ir_sha(base_ll) == normalized_ir_sha(post_ll)):
            raise AssertionError("K13 CSEBreak failed actual target IR delta/ABI")
        for bc, obj, label in ((base_bc, base_obj, "baseline"),
                               (post_bc, post_obj, "cse-break")):
            run_cmd([str(clang), "-O0", *args,
                     "-isysroot", sdk_paths[target],
                     "-c", str(bc), "-o", str(obj)],
                    out / (target + "-" + label + "-object-clang.log"))
            if not obj.is_file() or obj.stat().st_size < 32:
                raise AssertionError("K13 missing compiled object")
        if sha(base_obj) == sha(post_obj):
            raise AssertionError("K13 CSEBreak not present in native/iOS object")
        if is_ios:
            ios_macho(base_obj.read_bytes())
            ios_macho(post_obj.read_bytes())
            # Verify symbol truth from Mach-O rather than only IR declarations.
            for obj, label in ((base_obj, "baseline"), (post_obj, "cse-break")):
                symbols = run_cmd(["xcrun", "nm", "-gU", str(obj)],
                                  out / (target + "-" + label + "-nm-defined.log"))
                if not re.search(r"(?m)^\S+ [Tt] _dd_k8_evaluate$", symbols):
                    raise AssertionError("K13 Mach-O lost dd_k8_evaluate ABI")
                undefined = run_cmd(["xcrun", "nm", "-u", "-j", str(obj)],
                                    out / (target + "-" + label + "-nm-undefined.log"))
                if any(x.startswith("_kagura_") for x in undefined.splitlines()):
                    raise AssertionError("K13 unexpected Kagura runtime dependency in object")
        if not is_ios:
            native_macho(base_obj.read_bytes())
            native_macho(post_obj.read_bytes())
        rec = {
            "target": "IOS_ARM64_OBJECT_BUILD_ONLY" if is_ios else
                      "MACOS_NATIVE_4096_VECTOR_PARITY",
            "baseline_bitcode_sha256": sha(base_bc),
            "protected_bitcode_sha256": sha(post_bc),
            "baseline_ir_sha256": sha(base_ll),
            "protected_ir_sha256": sha(post_ll),
            "normalized_baseline_ir_sha256": normalized_ir_sha(base_ll),
            "normalized_protected_ir_sha256": normalized_ir_sha(post_ll),
            "baseline_object_sha256": sha(base_obj),
            "protected_object_sha256": sha(post_obj),
            "pass_manager_log_sha256": sha(out / (target + "-pass-manager.log")),
            "actual_pass_class": PASS_CLASS,
            "source_canary_abi": "dd_k8_evaluate",
            "real_ir_and_object_delta": True,
            "iphone_executed": False,
        }
        if not is_ios:
            checksums = []
            for obj, label in ((base_obj, "baseline"),
                               (post_obj, "cse-break")):
                exe = out / (target + "-" + label)
                run_cmd(["xcrun", "clang", str(obj), str(runner_obj),
                         "-o", str(exe)],
                        out / (target + "-" + label + "-link.log"))
                raw = run_cmd([str(exe)], out / (target + "-" + label + "-native.log"))
                checksums.append(validate_native(raw))
            if checksums[0] != checksums[1]:
                raise AssertionError("K13 4096-vector native parity mismatch")
            rec.update({"native_vectors": VECTORS,
                        "baseline_checksum": checksums[0],
                        "protected_checksum": checksums[1],
                        "native_parity": "PASS"})
        else:
            rec.update({"native_parity": "NOT_TESTED_ON_IOS_DEVICE",
                        "macho": "ARM64_SUBTYPE0_MH_OBJECT"})
        records[target] = rec

    report = {
        "schema": 1,
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pinned_commit": PIN,
        "pinned_registry_sha256": sha(out / "pinned-registry.def"),
        "k12_verified_registry_sha256": REGISTRY_SHA,
        "upstream_license_sha256": sha(out / "pinned-LICENSE"),
        "pass": PASS,
        "pass_kind": entry["kind"],
        "pass_enable_flag": entry["enable_flag"],
        "pass_class": PASS_CLASS,
        "pipeline": PIPELINE,
        "fixture_sha256": sha(fixture),
        "runner_sha256": sha(runner),
        "llvm_major": 19,
        "targets": records,
        "iphone_runtime_executed": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "security_strength_claim": False,
    }
    (out / "Kagura-K13-REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("K13_MACOS_CSE_BREAK_4096_PARITY_AND_IOS_ARM64_OBJECT_PASS: "
          "device/Crane/PAC NOT_TESTED")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("src", "llvm", "plugin", "out"):
        ap.add_argument("--" + name, type=Path, required=True)
    a = ap.parse_args()
    run(a.src, a.llvm, a.plugin, a.out)


if __name__ == "__main__":
    main()
