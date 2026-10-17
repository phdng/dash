#!/usr/bin/env python3
"""K8 isolated REAL Kagura LLVM19 pass coverage; only macOS CI can verify native.

Named module/function passes are checked against the actual PINNED upstream
PassRegistry.def. Fail closed if a candidate is invoked but produces no
observable IR/object delta or changes the 4096-vector native behavior.
iOS arm64 is cross-compiled OBJECT ONLY; no device or iOS runtime claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PIN = "ac2136ee0408677cf7cdee55307e9b16edd5f4d5"
SEED = "82712"
# Type and pass class are checked against the frozen upstream registry.
CANDIDATES = {
    "ibr": ("FN", "IndirectBranchPass", "function(kagura-ibr)"),
    "mvo": ("FN", "MemoryValueObfuscationPass", "function(kagura-mvo)"),
    "genc": ("MOD", "GlobalEncryptionPass", "kagura-genc"),
    "fsplit": ("MOD", "FunctionSplitPass", "kagura-fsplit"),
    "ci": ("MOD", "CallIndirectionPass", "kagura-ci"),
}
VECTORS = 4096
LOG_RE = re.compile(
    r"\ADD_K8_SCHEMA=1\nDD_K8_VECTORS=4096\n"
    r"DD_K8_CHECKSUM=([0-9a-f]{16})\nDD_K8_COMPLETE=PASS\n\Z"
)
FN_RE = re.compile(r"(?m)^define\s+[^\n]*?@(?:\"([^\"]+)\"|([\w.$-]+))\(")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_registry(text: str) -> None:
    for name, (kind, _cls, _pipeline) in CANDIDATES.items():
        pat = rf'(?m)^KAGURA_{kind}_PASS\(\s*\w+\s*,\s*"kagura-{name}"\s*,'
        if len(re.findall(pat, text)) != 1:
            raise AssertionError(f"K8 {name} registry missing, duplicated or wrong module/function type")
    if "kagura-vm" not in text:
        raise AssertionError("Pinned Kagura registry lacks the previously verified VM")


def validate_trace(name: str, trace: str) -> None:
    if name not in CANDIDATES:
        raise AssertionError("Unexpected pass")
    cls = CANDIDATES[name][1]
    if not re.search(r"(?m)^Running pass: (?:kagura::)?" + cls + r" on ", trace):
        raise AssertionError(f"K8 {name}: pass manager did not execute exact {cls}")


def functions(ir: str) -> set[str]:
    return {q or p for q, p in FN_RE.findall(ir)}


def validate_delta(name: str, before_ir: str, after_ir: str,
                   before_object: bytes, after_object: bytes, trace: str) -> dict:
    validate_trace(name, trace)
    if before_ir == after_ir or before_object == after_object:
        raise AssertionError(f"K8 {name}: invoked pass but no real IR/object delta")
    if "dd_k8_evaluate" not in functions(before_ir) or (
        "dd_k8_evaluate" not in functions(after_ir)):
        raise AssertionError(f"K8 {name}: public ABI symbol removed")
    if name == "ibr":
        if "@__kagura_fptr_" not in after_ir:
            raise AssertionError("K8 IBR lacks indirect function-pointer global")
    elif name == "ci":
        if "@__kagura_thunk_table" not in after_ir or (
                "kagura_rtld_default_handle" not in after_ir):
            raise AssertionError("K8 CI lacks runtime-resolved call thunk")
    elif name == "mvo":
        if ".mvo" not in after_ir or "store volatile" not in before_ir:
            raise AssertionError("K8 MVO needs real volatile alloca XOR")
    elif name == "genc":
        validate_genc_input_ir(before_ir)
        if ".dec" not in after_ir:
            raise AssertionError("K8 GENC did not decode encrypted constant")
    elif name == "fsplit":
        if len(functions(after_ir) - functions(before_ir)) < 1:
            raise AssertionError("K8 FSPLIT did not outline a new function")
    return {"new_functions": sorted(functions(after_ir) - functions(before_ir))}


def validate_mvo_input_ir(ir: str) -> None:
    """Require a direct integer alloca with only load/store users.

    The pinned MVO transform skips escaped pointers (including ones passed
    to llvm.lifetime). A lifetime intrinsic on an *unrelated* alloca is not
    a reason to reject the entire module. This is a preflight; LLVM's pass
    remains the final authority and IR + object deltas must still be real.
    """
    if "optnone" in ir:
        raise AssertionError("K8 MVO O0 fixture accidentally has optnone")
    lines = ir.splitlines()
    allocas = re.findall(
        r"(?m)^\s*(%[A-Za-z0-9_.$-]+) = alloca i64(?:,|$)", ir)
    for ptr in allocas:
        # Check uses of this exact alloca, not text from unrelated locals.
        reference = re.compile(
            r"(?<![A-Za-z0-9_.$-])" + re.escape(ptr) +
            r"(?![A-Za-z0-9_.$-])")
        definition = re.compile(
            r"^\s*" + re.escape(ptr) + r" = alloca i64(?:,|$)")
        store = re.compile(
            r"^\s*store volatile i64 .+, ptr " +
            re.escape(ptr) + r"(?:,|$)")
        load = re.compile(
            r"^\s*%[A-Za-z0-9_.$-]+ = load volatile i64, ptr " +
            re.escape(ptr) + r"(?:,|$)")
        stores = 0
        loads = 0
        escaped = False
        for line in lines:
            if definition.match(line) or not reference.search(line):
                continue
            if store.match(line):
                stores += 1
            elif load.match(line):
                loads += 1
            else:
                escaped = True  # call/lifetime, GEP, alias or storing pointer
                break
        if stores and loads and not escaped:
            return
    raise AssertionError(
        "K8 MVO input lacks eligible direct volatile i64 alloca/load/store; "
        "no-op pass is not accepted")


def validate_genc_input_ir(ir: str) -> None:
    """GENC pinned compiler only finds a direct load of a private constant.

    Runtime-indexed array GEPs at O1 can bypass the upstream
    hasLoadUseInFunction() filter even if the array exists and is used.
    A scalar read via a volatile-qualified lvalue guarantees a LoadInst
    whose pointer operand is the constant global itself.
    """
    if not re.search(
        r"(?m)^@dd_k8_genc_scalar = (?:private|internal)[^\n]*\bconstant i64\b",
        ir
    ) or not re.search(
        r"(?m)^\s*%[A-Za-z0-9_.$-]+ = load volatile i64, "
        r"ptr @dd_k8_genc_scalar(?:,|$)",
        ir
    ):
        raise AssertionError(
            "K8 GENC input lacks direct volatile LoadInst of private "
            "constant integer global; no-op pass is not accepted")


def validate_native_output(raw: str) -> str:
    m = LOG_RE.fullmatch(raw)
    if m is None:
        raise AssertionError("K8 native 4096-vector schema/checksum invalid")
    return m.group(1)


def command(args: list[str], *, log: Path | None = None) -> str:
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, check=False)
    if log is not None:
        log.write_text(p.stdout + p.stderr, encoding="utf-8")
    if p.returncode != 0:
        raise RuntimeError(f"K8 command failed exit={p.returncode}: {args[0]} "
                           f"({p.stderr[-900:]})")
    return p.stdout + p.stderr


def verify_apple_arm64_object(data: bytes) -> None:
    # A Mach-O 64-bit relocatable object, CPU_TYPE_ARM64=0x0100000c,
    # subtype=0 (never arm64e). Both before & after must satisfy this.
    if len(data) < 32 or int.from_bytes(data[:4], "little") != 0xFEEDFACF:
        raise AssertionError("K8 iOS object not Mach-O 64-bit")
    if (int.from_bytes(data[4:8], "little") != 0x0100000C or
            int.from_bytes(data[8:12], "little") != 0 or
            int.from_bytes(data[12:16], "little") != 1):
        raise AssertionError("K8 iOS object wrong CPU/subtype/filetype")


def run(*, llvm: Path, plugin: Path, src: Path, out: Path) -> dict:
    registry = src / "include/kagura/PassRegistry.def"
    if not registry.is_file():
        raise AssertionError("Missing pinned upstream registry")
    validate_registry(registry.read_text(encoding="utf-8"))
    if not plugin.is_file():
        raise AssertionError("Kagura LLVM19 plugin binary missing")
    license_path = src / "LICENSE"
    if not license_path.is_file() or not license_path.read_bytes():
        raise AssertionError("Pinned Kagura MIT license missing")
    clang = str(llvm / "bin/clang")
    opt = str(llvm / "bin/opt")
    dis = str(llvm / "bin/llvm-dis")
    sdk_mac = command(["xcrun", "--sdk", "macosx", "--show-sdk-path"]).strip()
    sdk_ios = command(["xcrun", "--sdk", "iphoneos", "--show-sdk-path"]).strip()
    # CI is the ONLY candidate that imports the resolver from runtime.
    runtime = src.parent / "kagura-k8-build/runtime/libkagura_runtime.a"
    if not runtime.is_file():
        raise AssertionError("Missing exact pinned runtime lib for CI")
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(license_path, out / "KAGURA-UPSTREAM-LICENSE")
    fixture = str(HERE / "fixture.c")
    fixture_opts = ["-O1", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-fno-builtin-strlen"]
    runner_obj = out / "runner.o"
    command(["xcrun", "clang", "-O1", "-std=c11", "-Wall",
             "-Wextra", "-Werror", "-c", str(HERE / "runner.c"),
             "-o", str(runner_obj)])
    def emit_native(bc: Path, obj: Path) -> None:
        command([clang, "-O0", "-c", str(bc), "-o", str(obj)])
    plain_bc = out / "plain.bc"
    plain_ir = out / "plain.ll"
    plain_obj = out / "plain.o"
    command([clang, *fixture_opts, "-isysroot", sdk_mac,
             "-emit-llvm", "-c", fixture, "-o", str(plain_bc)])
    command([dis, str(plain_bc), "-o", str(plain_ir)])
    emit_native(plain_bc, plain_obj)
    plain_exe = out / "plain"
    command(["xcrun", "clang", str(plain_obj), str(runner_obj),
             "-o", str(plain_exe)])
    plain_log = out / "plain-native.log"
    plain_log.write_text(command([str(plain_exe)]), encoding="ascii")
    digest = validate_native_output(plain_log.read_text(encoding="ascii"))
    plain_text = plain_ir.read_text(encoding="utf-8")
    validate_genc_input_ir(plain_text)
    ios_plain_bc = out / "ios-plain.bc"
    ios_plain_obj = out / "ios-plain.o"
    command([clang, *fixture_opts, "-target", "arm64-apple-ios15.0",
             "-isysroot", sdk_ios, "-emit-llvm", "-c", fixture,
             "-o", str(ios_plain_bc)])
    command([clang, "-O0", "-target", "arm64-apple-ios15.0",
             "-isysroot", sdk_ios, "-c", str(ios_plain_bc),
             "-o", str(ios_plain_obj)])
    verify_apple_arm64_object(ios_plain_obj.read_bytes())
    ios_plain_ir = out / "ios-plain.ll"
    command([dis, str(ios_plain_bc), "-o", str(ios_plain_ir)])
    validate_genc_input_ir(ios_plain_ir.read_text(encoding="utf-8"))

    # MVO needs *direct* integer alloca users (load/store only). LLVM -O1
    # can promote/remove that alloca or retain lifetime intrinsics that the
    # pinned upstream conservatively treats as escaping the pointer.
    # Compile only this fixture again at O0 with optnone explicitly disabled.
    # Both MVO baseline and transformed module use identical LLVM19 flags.
    mvo_flags = ["-O0", "-Xclang", "-disable-O0-optnone",
                 *fixture_opts[1:]]
    mvo_host_bc = out / "mvo-plain.bc"
    mvo_host_ir = out / "mvo-plain.ll"
    mvo_host_obj = out / "mvo-plain.o"
    command([clang, *mvo_flags, "-isysroot", sdk_mac,
             "-emit-llvm", "-c", fixture, "-o", str(mvo_host_bc)])
    command([dis, str(mvo_host_bc), "-o", str(mvo_host_ir)])
    mvo_text = mvo_host_ir.read_text(encoding="utf-8")
    validate_mvo_input_ir(mvo_text)
    emit_native(mvo_host_bc, mvo_host_obj)
    mvo_host_exe = out / "mvo-plain"
    command(["xcrun", "clang", str(mvo_host_obj), str(runner_obj),
             "-o", str(mvo_host_exe)])
    mvo_host_log = out / "mvo-plain-native.log"
    mvo_host_log.write_text(command([str(mvo_host_exe)]), encoding="ascii")
    if mvo_host_log.read_bytes() != plain_log.read_bytes():
        raise AssertionError("K8 MVO O0 baseline mismatches O1 reference")

    mvo_ios_bc = out / "mvo-ios-plain.bc"
    mvo_ios_ir = out / "mvo-ios-plain.ll"
    mvo_ios_obj = out / "mvo-ios-plain.o"
    command([clang, *mvo_flags, "-target", "arm64-apple-ios15.0",
             "-isysroot", sdk_ios, "-emit-llvm", "-c", fixture,
             "-o", str(mvo_ios_bc)])
    command([dis, str(mvo_ios_bc), "-o", str(mvo_ios_ir)])
    validate_mvo_input_ir(mvo_ios_ir.read_text(encoding="utf-8"))
    command([clang, "-O0", "-target", "arm64-apple-ios15.0",
             "-isysroot", sdk_ios, "-c", str(mvo_ios_bc),
             "-o", str(mvo_ios_obj)])
    verify_apple_arm64_object(mvo_ios_obj.read_bytes())
    report = {
        "schema": 1, "scope": "K8_PINNED_KAGURA_FIVE_PASS_ISOLATED_CI",
        "pinned_commit": PIN, "pass_count": len(CANDIDATES),
        "upstream_pass_registry_sha256": sha(registry),
        "upstream_license_sha256": sha(license_path),
        "fixture_sha256": sha(HERE / "fixture.c"),
        "runner_sha256": sha(HERE / "runner.c"),
        "host_vectors_per_pass": VECTORS, "host_digest": digest,
        "baseline_object_sha256": sha(plain_obj),
        "ios_baseline_object_sha256": sha(ios_plain_obj),
        "mvo_baseline_profile": "O0_DISABLE_OPTNONE_DIRECT_INTEGER_ALLOCA",
        "mvo_baseline_object_sha256": sha(mvo_host_obj),
        "mvo_ios_baseline_object_sha256": sha(mvo_ios_obj),
        "mvo_baseline_parity_with_o1": "PASS",
        "iphone_runtime_executed": False, "arm64e_executed": False,
        "crane_production_modified": False,
        "performance_evaluated": False,
        "candidate_results": {},
    }
    for name, (kind, cls, pipeline) in CANDIDATES.items():
        # All candidate comparisons are against their *own same-flags*
        # plain module/object. Never compare transformed -O0 to plain -O1:
        # that would fabricate an "IR/object changed" pass result.
        host_input = mvo_host_bc if name == "mvo" else plain_bc
        host_before_ir = mvo_text if name == "mvo" else plain_text
        host_before_obj = mvo_host_obj if name == "mvo" else plain_obj
        ios_input = mvo_ios_bc if name == "mvo" else ios_plain_bc
        ios_before_ir = mvo_ios_ir if name == "mvo" else ios_plain_ir
        ios_before_obj = mvo_ios_obj if name == "mvo" else ios_plain_obj
        stage = out / name
        stage.mkdir(exist_ok=True)
        candidate_bc = stage / "protected.bc"
        candidate_ir = stage / "protected.ll"
        candidate_obj = stage / "protected.o"
        trace = stage / "opt.log"
        command([opt, f"--load-pass-plugin={plugin}", f"-kagura-seed={SEED}",
                 f"-kagura-{name}", "-debug-pass-manager", f"-passes={pipeline},verify",
                 str(host_input), "-o", str(candidate_bc)], log=trace)
        command([dis, str(candidate_bc), "-o", str(candidate_ir)])
        emit_native(candidate_bc, candidate_obj)
        ir = candidate_ir.read_text(encoding="utf-8")
        change = validate_delta(name, host_before_ir, ir,
                                host_before_obj.read_bytes(),
                                candidate_obj.read_bytes(), trace.read_text("utf-8"))
        exe = stage / "protected"
        link = ["xcrun", "clang", str(candidate_obj), str(runner_obj)]
        if name == "ci":
            link.append(str(runtime))
        command([*link, "-o", str(exe)], log=stage / "native-link.log")
        host_log = stage / "native.log"
        host_log.write_text(command([str(exe)]), encoding="ascii")
        if host_log.read_bytes() != plain_log.read_bytes():
            raise AssertionError(f"K8 {name}: native 4096-vector parity mismatch")
        ios_bc = stage / "ios-protected.bc"
        ios_ir = stage / "ios-protected.ll"
        ios_obj = stage / "ios-protected.o"
        ios_trace = stage / "ios-opt.log"
        command([opt, f"--load-pass-plugin={plugin}", f"-kagura-seed={SEED}",
                 f"-kagura-{name}", "-debug-pass-manager", f"-passes={pipeline},verify",
                 str(ios_input), "-o", str(ios_bc)], log=ios_trace)
        command([dis, str(ios_bc), "-o", str(ios_ir)])
        command([clang, "-O0", "-target", "arm64-apple-ios15.0",
                 "-isysroot", sdk_ios, "-c", str(ios_bc), "-o", str(ios_obj)])
        verify_apple_arm64_object(ios_obj.read_bytes())
        validate_delta(name,
                       ios_before_ir.read_text("utf-8"),
                       ios_ir.read_text("utf-8"), ios_before_obj.read_bytes(),
                       ios_obj.read_bytes(), ios_trace.read_text("utf-8"))
        report["candidate_results"][name] = {
            "registered_kind": kind, "llvm_pass_class": cls,
            "opt_pipeline": pipeline, "pass_invoked": True,
            "baseline_compiler_profile": (
                "O0_DISABLE_OPTNONE_DIRECT_INTEGER_ALLOCA"
                if name == "mvo" else "O1"),
            "baseline_host_object_sha256": sha(host_before_obj),
            "baseline_ios_object_sha256": sha(ios_before_obj),
            "ir_and_native_object_changed": True,
            "native_4096_vector_parity": "PASS",
            "native_digest": digest,
            "ios_arm64_object": "BUILD_ONLY_NOT_EXECUTED",
            "host_object_sha256": sha(candidate_obj),
            "ios_object_sha256": sha(ios_obj),
            "host_opt_log_sha256": sha(trace),
            "ios_opt_log_sha256": sha(ios_trace),
            **change,
        }
        (out / "Kagura-K8-PASS-REPORT.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--llvm", type=Path, required=True)
    p.add_argument("--plugin", type=Path, required=True)
    p.add_argument("--src", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = run(llvm=a.llvm, plugin=a.plugin, src=a.src, out=a.out)
    assert set(result["candidate_results"]) == set(CANDIDATES)
    print("KAGURA_K8_MACOS_NATIVE_FIVE_PASS_PARITY_AND_ARM64_OBJECTS_PASS")


if __name__ == "__main__":
    main()
