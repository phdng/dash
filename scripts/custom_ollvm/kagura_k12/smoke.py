#!/usr/bin/env python3
"""K12 opt-only PROBE for every newly discovered upstream named pass.

Each candidate runs alone on isolated K8 C fixture for macOS and iOS IR.
This is a diagnostic parser/transform screening ONLY: no executable is
linked, no host native parity, no iPhone execution, no Crane production.
An IR delta never upgrades a pass to "verified" without independent gates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from inventory import PIN, sha, verify, normalized_ir_sha

MAX_UNVERIFIED = 64
TIMEOUT_SEC = 75


def command(args: list[str], *, stdout_log: Path | None = None) -> tuple[bool, str]:
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, check=False, timeout=TIMEOUT_SEC)
        output = result.stdout + result.stderr
        if stdout_log is not None:
            stdout_log.write_text(output, encoding="utf-8")
        return result.returncode == 0, output[-3000:]
    except subprocess.TimeoutExpired:
        if stdout_log is not None:
            stdout_log.write_text("K12_OPT_TIMEOUT\n", encoding="ascii")
        return False, "K12_OPT_TIMEOUT"


def run(*, src: Path, llvm: Path, plugin: Path, out: Path) -> dict:
    original = verify(out)
    if original["pinned_commit"] != PIN or not plugin.is_file():
        raise AssertionError("K12 pinned Kagura source or LLVM19 plugin missing")
    if len(original["remaining_registered_unverified"]) > MAX_UNVERIFIED:
        raise AssertionError("K12 too many unverified pass candidates to auto-probe")
    clang = llvm / "bin/clang"
    opt = llvm / "bin/opt"
    dis = llvm / "bin/llvm-dis"
    if not clang.is_file() or not opt.is_file() or not dis.is_file():
        raise AssertionError("K12 requires genuine LLVM19 Clang, opt and llvm-dis")
    fixture = Path(__file__).resolve().parents[1] / "kagura_k8/fixture.c"
    if not fixture.is_file():
        raise AssertionError("K12 frozen K8 C fixture missing")
    sdk_hosts = {
        "macos": "macosx",
        "ios-arm64-build-only": "iphoneos",
    }
    baselines = {}
    for label, sdk in sdk_hosts.items():
        ok, path = command(["xcrun", "--sdk", sdk, "--show-sdk-path"])
        if not ok:
            raise AssertionError("K12 Apple SDK unavailable: " + sdk + " " + path)
        # xcrun SDK path is normally the only stdout, no warning output.
        sdk_path = path.strip()
        if "\n" in sdk_path or not sdk_path or not Path(sdk_path).is_dir():
            raise AssertionError("K12 iOS/macOS SDK path invalid")
        bc = out / (label + "-baseline.bc")
        target = ["-target", "arm64-apple-ios15.0"] if label.startswith("ios") else []
        args = [str(clang), "-std=c11", "-O1", "-Wall", "-Wextra", "-Werror",
                "-fno-builtin-strlen", *target, "-isysroot", sdk_path,
                "-emit-llvm", "-c", str(fixture), "-o", str(bc)]
        ok, diag = command(args, stdout_log=out / (label + "-clang.log"))
        if not ok or not bc.is_file():
            raise AssertionError("K12 baseline C LLVM19 bitcode unavailable: " + diag)
        plain_ir = out / (label + "-baseline.ll")
        ok, dis_diag = command(
            [str(dis), str(bc), "-o", str(plain_ir)],
            stdout_log=out / (label + "-llvm-dis.log"))
        if not ok or not plain_ir.is_file() or not plain_ir.stat().st_size:
            raise AssertionError("K12 could not disassemble baseline real LLVM19 IR: " +
                                 dis_diag)
        baselines[label] = (bc, plain_ir)
    results = []
    for idx, row in enumerate(original["remaining_registered_unverified"], 1):
        stage = out / f"probe-{idx:02d}-{row['name']}"
        stage.mkdir(parents=True, exist_ok=True)
        if row["kind"] == "INFRA":
            results.append({**row, "screening": "SKIPPED_INFRA_NOT_AUTO_RUN",
                            "native_parity": "NOT_TESTED",
                            "ios_device": "NOT_TESTED", "targets": {}})
            continue
        if row["kind"] not in ("FN", "MOD"):
            raise AssertionError("K12 unknown upstream pass kind")
        pipeline = ("function(" + row["name"] + "),verify"
                    if row["kind"] == "FN" else row["name"] + ",verify")
        target_results = {}
        for label, (input_bc, input_ir) in baselines.items():
            candidate = stage / (label + "-post-opt.bc")
            after_ir = stage / (label + "-post-opt.ll")
            dis_log = stage / (label + "-llvm-dis.log")
            log = stage / (label + "-opt.log")
            flag = "-" + row["name"]
            # Prevent rerun from silently reusing a stale output artifact.
            # A failed command must not be interpreted as a current delta.
            if candidate.exists() or after_ir.exists():
                raise AssertionError("K12 refusing contaminated preexisting pass outputs")
            args = [str(opt), "--load-pass-plugin=" + str(plugin),
                    "-kagura-seed=82712", flag, "-debug-pass-manager",
                    "-passes=" + pipeline, str(input_bc), "-o", str(candidate)]
            ok, tail = command(args, stdout_log=log)
            if ok and (not candidate.is_file() or not candidate.stat().st_size):
                raise AssertionError("K12 opt returned success without real LLVM bitcode")
            dis_ok = False
            dis_tail = ""
            if ok:
                dis_ok, dis_tail = command(
                    [str(dis), str(candidate), "-o", str(after_ir)],
                    stdout_log=dis_log)
            if ok and dis_ok and (
                    not after_ir.is_file() or not after_ir.stat().st_size):
                raise AssertionError("K12 llvm-dis returned success but no real IR")
            # Byte-level delta is diagnostic only; the actual named "IR"
            # delta is based on disassembled LLVM IR, not bitcode serialization.
            screened = ok and dis_ok
            ir_changed = screened and normalized_ir_sha(after_ir) != normalized_ir_sha(input_ir)
            target_results[label] = {
                "screening": ("OPT_EXECUTED_IR_DELTA_UNVERIFIED" if ir_changed else
                              "OPT_EXECUTED_NO_IR_DELTA_UNVERIFIED" if screened else
                              "OPT_INVALID_BITCODE_UNVERIFIED" if ok else
                              "OPT_FAILED_UNVERIFIED"),
                "input_sha256": sha(input_bc),
                "input_ir_sha256": sha(input_ir),
                "normalized_input_ir_sha256": normalized_ir_sha(input_ir),
                "output_sha256": sha(candidate) if ok else None,
                "output_ir_sha256": sha(after_ir) if screened else None,
                "normalized_output_ir_sha256": (
                    normalized_ir_sha(after_ir) if screened else None),
                "bitcode_byte_delta_only": (
                    sha(candidate) != sha(input_bc) if ok else False),
                "opt_log_sha256": sha(log),
                "llvm_dis_log_sha256": sha(dis_log) if ok else None,
                "error_tail": tail if not ok else dis_tail if not dis_ok else "",
                "native_parity": "NOT_TESTED",
                "iphone_runtime": "NOT_TESTED",
            }
        results.append({**row, "screening": "LLVM19_OPT_ONLY_NOT_PASS_VALIDATION",
                        "opt_pipeline": pipeline, "targets": target_results,
                        "native_parity": "NOT_TESTED", "ios_device": "NOT_TESTED"})
    report = {
        "schema": 1,
        "scope": "K12_OPT_DIAGNOSTIC_ONLY_NOT_NATIVE_PASS_VALIDATION",
        "pinned_commit": PIN,
        "source_inventory_sha256": sha(
            out / "Kagura-K12-REMAINING-PASS-INVENTORY.json"),
        "fixture_sha256": sha(fixture),
        "clang19_ir_disassembly_comparison": True,
        "ir_delta_ignores_llvm_dis_moduleid_comment": True,
        "candidate_count": len(results),
        "results": results,
        "native_parity_proven": False,
        "ios_device_runtime_proven": False,
        "arm64e_pac_proven": False,
        "crane_production_modified": False,
    }
    (out / "Kagura-K12-REMAINING-OPT-SCREEN.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    print("K12_OPT_SCREEN_COMPLETE_NOT_NATIVE_PASS_VERIFICATION: candidates=" +
          str(len(results)))
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for item in ("src", "llvm", "plugin", "out"):
        p.add_argument("--" + item, type=Path, required=True)
    args = p.parse_args()
    run(src=args.src, llvm=args.llvm, plugin=args.plugin, out=args.out)


if __name__ == "__main__":
    main()
