#!/usr/bin/env python3
"""K1 per-pass Kagura structural attribution, using REAL LLVM19 IR/native runs.

Each stage consumes previous stage's .bc. No stage may be recorded as
behavior-preserving unless native output matches the untouched baseline.
Pass invocation alone never counts as observable obfuscation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from audit import MARKER, verify_host

PASS_STAGES = (
    ("str", "kagura-str"),
    ("fla", "function(kagura-fla)"),
    ("bcf", "function(kagura-bcf)"),
    ("sub", "function(kagura-sub)"),
    ("co", "function(kagura-co)"),
    ("bbr", "function(kagura-bbr)"),
    ("bbs", "function(kagura-bbs)"),
)
MAIN_SYMBOL = "dd_kagura_critical"
RANDOM_SEED = "1234567"
SENTINEL_SYMBOL = "dd_kagura_unprotected_sentinel"


def defined_functions(ir: str) -> set[str]:
    """Reject extra pre-existing functions inside the protected module."""
    pattern = r'(?m)^define\b[^\n]*@(?:"([^"]+)"|([A-Za-z0-9_.$-]+))\('
    return {quoted or plain for quoted, plain in re.findall(pattern, ir)}


def scope_report(original: str, stage: str, pass_debug: str) -> dict:
    before = defined_functions(original)
    after = defined_functions(stage)
    if before != {MAIN_SYMBOL}:
        raise AssertionError("Kagura input includes non-allowlisted function")
    if MAIN_SYMBOL not in after or SENTINEL_SYMBOL in after:
        raise AssertionError("Protected module lost critical function or gained sentinel")
    generated = after - before
    if any(not name.startswith("kagura_decrypt_") for name in generated):
        raise AssertionError("Unexpected helper definition in protected module")
    if SENTINEL_SYMBOL in pass_debug:
        raise AssertionError("Kagura pass-manager attempted unprotected sentinel")
    return {
        "scope": "ISOLATED_TRANSLATION_UNIT_NOT_FUNCTION_PASS_ALLOWLIST",
        "protected_input_definitions": sorted(before),
        "generated_decryption_helpers": sorted(generated),
        "generated_helpers_may_receive_kagura_function_passes": True,
        "unprotected_sentinel_in_protected_ir": False,
        "unprotected_sentinel_pass_invoked": False,
        "strict_single_function_pass_filter_verified": False,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_body(text: str) -> str:
    match = re.search(
        r"(?ms)^define\s+[^\n]*@" + MAIN_SYMBOL +
        r"\([^\n]*\)[^\n]*\{(.*?)^\}", text
    )
    if not match:
        raise AssertionError("Critical C function missing in LLVM IR")
    return match.group(1)


def analyze_delta(previous_ir: str, candidate_ir: str, previous_obj: bytes,
                  candidate_obj: bytes, pass_name: str) -> dict:
    original = function_body(previous_ir)
    current = function_body(candidate_ir)
    ir_changed = original != current
    object_changed = previous_obj != candidate_obj
    blocks_before = len(re.findall(r"(?m)^\s*[A-Za-z0-9_.$-]+:\s*(?:;[^\n]*)?$",
                                   original))
    blocks_after = len(re.findall(r"(?m)^\s*[A-Za-z0-9_.$-]+:\s*(?:;[^\n]*)?$",
                                  current))
    if pass_name in ("bbr", "bbs") and not ir_changed:
        # A no-op on this particular function is not "pass ineffective in
        # general", but definitely cannot be counted as protection here.
        status = "NO_OBSERVED_IR_DELTA"
    elif ir_changed and object_changed:
        status = "IR_AND_OBJECT_DELTA"
    elif ir_changed:
        status = "IR_ONLY_DELTA"
    elif object_changed:
        status = "OBJECT_ONLY_DELTA_NOT_ATTRIBUTABLE"
    else:
        status = "NO_OBSERVED_DELTA"
    return {
        "pass": pass_name,
        "critical_function_ir_changed": ir_changed,
        "object_bytes_changed": object_changed,
        "critical_function_basic_blocks_before": blocks_before,
        "critical_function_basic_blocks_after": blocks_after,
        "classification": status,
        "canary_plaintext_in_stage_object": MARKER in candidate_obj,
        "no_obfuscation_strength_score": True,
    }


def checked(cmd: list[str], log: Path | None = None, *, output: Path | None = None) -> None:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            check=False)
    if log:
        log.write_bytes(result.stdout)
    if result.returncode:
        raise RuntimeError(f"Compiler failed ({result.returncode}): "
                           f"{' '.join(cmd[:3])}; {result.stdout[-1400:]!r}")
    if output is not None and not output.is_file():
        raise AssertionError(f"Missing expected compiler output {output}")


def build(*, llvm: Path, plugin: Path, plain_bc: Path, baseline_log: Path,
          runner_obj: Path, sentinel_obj: Path, benchmark_obj: Path,
          destination: Path) -> dict:
    for file in (plugin, plain_bc, baseline_log, runner_obj,
                 sentinel_obj, benchmark_obj):
        if not file.is_file():
            raise FileNotFoundError(file)
    opt = llvm / "bin" / "opt"
    clang = llvm / "bin" / "clang"
    llvm_dis = llvm / "bin" / "llvm-dis"
    for exe in (opt, clang, llvm_dis):
        if not exe.is_file():
            raise AssertionError(f"LLVM19 tool unavailable: {exe}")
    destination.mkdir(parents=True, exist_ok=True)
    baseline_ll = destination / "baseline.ll"
    checked([str(llvm_dis), str(plain_bc), "-o", str(baseline_ll)],
            output=baseline_ll)
    baseline_ir = baseline_ll.read_text(encoding="utf-8")
    if defined_functions(baseline_ir) != {MAIN_SYMBOL}:
        raise AssertionError("Protected module has extra pre-existing functions")
    sentinel_hash = sha(sentinel_obj)
    current_bc = plain_bc
    current_ll = baseline_ll
    # Compile original .bc using precisely the same LLVM19 clang flags
    # as all subsequent stages, to avoid misattributing backend changes.
    previous_object = destination / "stage00-baseline.o"
    checked([str(clang), "-O0", "-c", str(plain_bc), "-o", str(previous_object)],
            output=previous_object)
    # A real native sentinel object is never sent to opt, and is linked
    # unchanged into every candidate. This is TU isolation, NOT a true
    # Kagura per-function allowlist for compiler-generated helpers.
    baseline_bench = destination / "stage00-baseline-bench"
    baseline_bench_log = destination / "stage00-baseline-bench.log"
    checked(["xcrun", "clang", str(previous_object), str(sentinel_obj),
             str(benchmark_obj), "-o", str(baseline_bench)],
            output=baseline_bench)
    checked([str(baseline_bench)], baseline_bench_log)

    stages = []
    for index, (name, pipeline) in enumerate(PASS_STAGES, start=1):
        prefix = destination / f"stage{index:02d}-{name}"
        next_bc = prefix.with_suffix(".bc")
        next_ll = prefix.with_suffix(".ll")
        obj = prefix.with_suffix(".o")
        executable = destination / f"stage{index:02d}-{name}-runner"
        output_log = prefix.with_suffix(".log")
        pass_log = destination / f"stage{index:02d}-{name}-opt.log"
        checked([str(opt), f"--load-pass-plugin={plugin}",
                 f"-kagura-seed={RANDOM_SEED}", "-debug-pass-manager",
                 f"-passes={pipeline}", str(current_bc), "-o", str(next_bc)],
                pass_log, output=next_bc)
        if b"Running pass:" not in pass_log.read_bytes():
            raise AssertionError(f"{name}: cannot verify LLVM pass-manager execution")
        checked([str(llvm_dis), str(next_bc), "-o", str(next_ll)],
                output=next_ll)
        checked([str(clang), "-O0", "-c", str(next_bc), "-o", str(obj)],
                output=obj)
        checked(["xcrun", "clang", str(obj), str(sentinel_obj),
                 str(runner_obj), "-o", str(executable)], output=executable)
        with output_log.open("wb") as handle:
            subprocess.run([str(executable)], stdout=handle, check=True)
        parity = verify_host(baseline_log, output_log)
        stage_ir = next_ll.read_text(encoding="utf-8")
        delta = analyze_delta(current_ll.read_text(encoding="utf-8"),
                              stage_ir, previous_object.read_bytes(),
                              obj.read_bytes(), name)
        scope = scope_report(baseline_ir, stage_ir,
                             pass_log.read_text(encoding="utf-8"))
        if sha(sentinel_obj) != sentinel_hash:
            raise AssertionError("Unprotected sentinel object bytes changed")
        bench_executable = destination / f"stage{index:02d}-{name}-bench"
        bench_log = destination / f"stage{index:02d}-{name}-bench.log"
        checked(["xcrun", "clang", str(obj), str(sentinel_obj),
                 str(benchmark_obj), "-o", str(bench_executable)],
                output=bench_executable)
        checked([str(bench_executable)], bench_log)
        delta.update({"scope_evidence": scope,
                      "unprotected_sentinel_object_sha256": sentinel_hash,
                      "host_benchmark_log_sha256": sha(bench_log)})
        if index == 1 and MARKER in obj.read_bytes():
            raise AssertionError("Kagura string pass left plaintext in stage1 object")
        if MARKER in obj.read_bytes():
            raise AssertionError(f"{name} reintroduced plaintext")
        delta.update({
            "stage": index,
            "pipeline_invoked": pipeline,
            "native_host_vectors": 8192,
            "native_8192_parity": parity["macos_host"],
            "llvm_ir_sha256": sha(next_ll),
            "object_sha256": sha(obj),
            "object_bytes": obj.stat().st_size,
            "pass_debug_log_sha256": sha(pass_log),
        })
        stages.append(delta)
        current_bc, current_ll, previous_object = next_bc, next_ll, obj

    manifest = {
        "schema": 1,
        "experiment": "KAGURA_K1_STAGED_STRUCTURAL_LLVM19",
        "stages_attempted": [x[0] for x in PASS_STAGES],
        "stage_results": stages,
        "stage_count": len(stages),
        "validated_host_vectors_each": 8192,
        "first_stage_string_marker_removed": True,
        "llvm19_same_compiler_per_stage": True,
        "unprotected_sentinel_separate_object_sha256": sentinel_hash,
        "function_scope": "TU_ONLY_GENERATED_HELPERS_NOT_EXEMPT",
        "native_host_benchmarks": "STAGED_LOGS_REQUIRE_POST_RUN_AUDIT",
        "arm64_ios_device_runtime": "NOT_TESTED_IN_K1_WORKFLOW",
        "arm64e": "APPLE_CLANG_BUILD_ONLY_NO_KAGURA",
        "production_crane_unchanged": True,
        "static_analysis_impossibility_claim": False,
        "notes": "IR-only/no-op stages do not count as native protection contribution.",
    }
    report = destination / "kagura-k1-stage-report.json"
    report.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("KAGURA_K1_STAGE_AUDIT_PASS: 7 isolated incremental passes, "
          "8192 host vectors per stage; inspect delta classifications")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llvm", type=Path, required=True)
    parser.add_argument("--plugin", type=Path, required=True)
    parser.add_argument("--plain-bc", type=Path, required=True)
    parser.add_argument("--baseline-log", type=Path, required=True)
    parser.add_argument("--runner-obj", type=Path, required=True)
    parser.add_argument("--sentinel-obj", type=Path, required=True)
    parser.add_argument("--benchmark-obj", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(llvm=args.llvm, plugin=args.plugin, plain_bc=args.plain_bc,
          baseline_log=args.baseline_log, runner_obj=args.runner_obj,
          sentinel_obj=args.sentinel_obj, benchmark_obj=args.benchmark_obj,
          destination=args.out)


if __name__ == "__main__":
    main()
