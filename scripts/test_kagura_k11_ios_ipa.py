#!/usr/bin/env python3
"""K11 unsigned iOS arm64 five-pass lab IPA portable negative tests."""
from __future__ import annotations
import hashlib
import json
import plistlib
import stat
import struct
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_k11"
sys.path.insert(0, str(LAB))
import package_ipa as package
import device_log_audit as logaudit


def rejects(fn, why: str):
    try:
        fn()
    except (AssertionError, ValueError, UnicodeError, KeyError):
        return
    raise AssertionError("K11 fake IPA/device claims accepted: " + why)

MOCK_UUID = "6ee048f1-8e5a-46ff-b8de-bc6947ec21e6"
uuid_bytes = uuid.UUID(MOCK_UUID).bytes

def macho(*, subtype=0, kind=2, uuid_ok=True):
    commands = (struct.pack("<II", 0x1B, 24) +
                (uuid_bytes if uuid_ok else b"not-a-uuid-1234"))
    return (struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C,
                        subtype, kind, 1, len(commands), 0, 0) +
            commands + b"synthetic K11 executable for negative tests")

src_info = (LAB / "Info.plist").read_bytes()
metadata = plistlib.loads(src_info)
assert metadata["CFBundleIdentifier"] == package.BUNDLE
assert metadata["CFBundleIdentifier"] not in {
    "com.duodash.research.kaguravmlab",
    "com.duodash.research.kaguralab",
    "com.duodash.research.protectionlab",
}
assert metadata["CFBundleExecutable"] == "KaguraFiveLab"
assert metadata["MinimumOSVersion"] == "15.0"
assert metadata["UIDeviceFamily"] == [1]
assert "NSAppTransportSecurity" not in metadata
assert "UIBackgroundModes" not in metadata
assert package.executable_uuid(macho()) == MOCK_UUID
rejects(lambda: package.executable_uuid(macho(subtype=0x80000002)),
        "arm64e disguised as arm64")
rejects(lambda: package.executable_uuid(macho(kind=6)),
        "MH_DYLIB disguised as MH_EXECUTE")
rejects(lambda: package.executable_uuid(macho()[:41]), "truncated load command")
rejects(lambda: package.executable_uuid(macho(uuid_ok=False)),
        "malformed LC_UUID")
rejects(lambda: package.executable_uuid(macho().replace(
    struct.pack("<II", 0x1B, 24), struct.pack("<II", 0x1B, 20))),
    "fake short LC_UUID")

with tempfile.TemporaryDirectory(prefix="K11-synthetic-ipa-") as folder:
    base = Path(folder)
    app = base / "KaguraFiveLab.app"
    app.mkdir()
    (app / "Info.plist").write_bytes(src_info)
    (app / "KaguraFiveLab").write_bytes(macho())
    ipa = base / "lab.ipa"
    report = base / "ipa-report.json"
    result = package.package(app, ipa, report)
    assert package.verify_ipa(ipa) == result
    assert result["scope"] == "STANDALONE_K11_FIVE_PASS_LAB_IPA"
    assert result["macho_uuid"] == MOCK_UUID
    assert result["device_execution"] == "NOT_TESTED_BY_CI"
    assert result["signed_by_ci"] is False
    original = ipa.read_bytes()
    package.package(app, ipa, report)
    assert ipa.read_bytes() == original, "K11 ZIP not reproducible"
    (app / "KaguraFiveLab").write_bytes(macho(subtype=0x80000002))
    rejects(lambda: package.package(app, ipa, report), "arm64e app")
    (app / "KaguraFiveLab").write_bytes(macho())
    wrong = dict(metadata)
    wrong["CFBundleIdentifier"] = "com.duodash.research.kaguralab"
    (app / "Info.plist").write_bytes(plistlib.dumps(wrong))
    rejects(lambda: package.package(app, ipa, report), "K5 namespace collision")
    (app / "Info.plist").write_bytes(src_info)
    (app / "_CodeSignature").mkdir()
    rejects(lambda: package.package(app, ipa, report), "unexpected signature directory")
    (app / "_CodeSignature").rmdir()

    evidence = base / "K11.json"
    record = {
        "scope": "K11_FIVE_PASS_K10_STRICT_METADATA_TROLLSTORE_LAB_ONLY",
        "app_macho_uuid": MOCK_UUID,
        "ipa_sha256": result["ipa_sha256"],
        "app_binary_sha256": result["binary_sha256"],
        "five_pass_ios_object_verified": True,
        "resolver_symbol_present": True,
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "security_attestation": False,
    }
    evidence.write_text(json.dumps(record), encoding="utf-8")
    log = base / "device.log"
    raw = (
        "DD_K11_IOS_SCHEMA=1\n"
        "DD_K11_IOS_CONTEXT=IOS_DEVICE\n"
        "DD_K11_IOS_ARCH=arm64:0x00000000\n"
        f"DD_K11_IOS_APP_UUID={MOCK_UUID}\n"
        "DD_K11_IOS_PIPELINE=MVO_GENC_FSPLIT_IBR_CI\n"
        "DD_K11_IOS_VECTORS_PER_FUNCTION=4096\n"
        "DD_K11_IOS_C_CHECKSUM=25a3318e3d7d6525\n"
        "DD_K11_IOS_MVO_CHECKSUM=64e61045bbc4a250\n"
        "DD_K11_IOS_COMPLETE=PASS\n"
    )
    log.write_text(raw, encoding="ascii")
    checked = logaudit.validate(log, report, evidence)
    assert checked["ci_build_correlation"]["claimed_uuid_matches_ipa"] is True
    assert checked["device_execution_cryptographically_attested"] is False
    for why, bad in (
        ("wrong UUID", raw.replace(MOCK_UUID, "00000000-0000-0000-0000-000000000000")),
        ("missing terminator", raw[:-1]),
        ("wrong checksum", raw.replace("64e61045bbc4a250", "0" * 16)),
        ("less vectors", raw.replace("=4096", "=4095")),
        ("wrong context", raw.replace("IOS_DEVICE", "MACOS_HOST")),
        ("wrong pass order", raw.replace("MVO_GENC_FSPLIT_IBR_CI", "CI_IBR_FSPLIT_GENC_MVO")),
        ("device arm64e fake", raw.replace("arm64:0x00000000", "arm64e:0x80000002")),
        ("fabricated extra text", raw + "PASS\n"),
        ("partial UUID", raw.replace(MOCK_UUID, MOCK_UUID[:12])),
    ):
        log.write_text(bad, encoding="ascii")
        rejects(lambda: logaudit.validate(log, report, evidence), why)
    log.write_text(raw, encoding="ascii")
    evil = dict(record)
    evil["five_pass_ios_object_verified"] = False
    evidence.write_text(json.dumps(evil))
    rejects(lambda: logaudit.validate(log, report, evidence),
            "manufactured five-pass artifact proof")
    evidence.write_text(json.dumps(record))
    evil = dict(result)
    evil["binary_sha256"] = "0" * 64
    wrong_report = base / "wrong.json"
    wrong_report.write_text(json.dumps(evil))
    rejects(lambda: logaudit.validate(log, wrong_report, evidence),
            "IPA binary SHA contradiction")

# Regression: an upstream header/prototype/reference/comment must NOT
# count as a resolver definition. Previous K11 text-only scan matched them.
import ci_runtime_resolver as resolver
with tempfile.TemporaryDirectory(prefix="K11-resolver-selection-") as temp_root:
    upstream = Path(temp_root)
    (upstream / "LICENSE").write_text("upstream fixture only\n", encoding="utf-8")
    runtime = upstream / "runtime"
    runtime.mkdir()
    (runtime / "declaration.c").write_text(
        "extern void *kagura_rtld_default_handle(void);\n"
        "void *probe(void) { return kagura_rtld_default_handle(); }\n",
        encoding="utf-8")
    (runtime / "comment.c").write_text(
        "/* void *kagura_rtld_default_handle(void) { fake } */\n"
        'const char *note = "kagura_rtld_default_handle(void) { fake";\n',
        encoding="utf-8")
    actual = runtime / "real.c"
    actual.write_text(
        "void *kagura_rtld_default_handle(void) { return 0; }\n",
        encoding="utf-8")
    chosen = resolver.require_selected(upstream)
    assert chosen["selected_source"] == "runtime/real.c"
    assert chosen["source_files_scanned"] == 3
    assert chosen["function_definitions"] == ["runtime/real.c"]
    assert chosen["mention_candidates"] == [
        "runtime/comment.c", "runtime/declaration.c", "runtime/real.c"]
    assert chosen["selected_source_sha256"] == hashlib.sha256(
        actual.read_bytes()).hexdigest()
    (runtime / "another.c").write_text(
        "void* kagura_rtld_default_handle(void) { return 0; }\n",
        encoding="utf-8")
    rejects(lambda: resolver.require_selected(upstream),
            "multiple REAL upstream C definitions must fail")
    (runtime / "another.c").unlink()
    actual.write_text("void *another_function(void) { return 0; }\n",
                      encoding="utf-8")
    rejects(lambda: resolver.require_selected(upstream),
            "upstream mentions with NO definition must fail")

# K11 anti_debug link regression: on a pinned iOS runtime source tree,
# nm must resolve both undefined symbols from actual ARM64 definitions,
# even when one provider TU defines two names and another is a decoy.
import ci_runtime_closure as closure
# Original CI bug: Apple nm -u emits bare names, not "U _name".
assert closure.parse_undefined_names(
    "_kagura_image_list_contains\n_kagura_suspicious_image_patterns\n"
) == {"_kagura_image_list_contains", "_kagura_suspicious_image_patterns"}
assert closure.parse_undefined_names("    _kagura_image_list_contains   \n") == {
    "_kagura_image_list_contains"}
assert closure.parse_undefined_names("") == set()
rejects(lambda: closure.parse_undefined_names(
    "                 U _kagura_image_list_contains\n"),
    "nm -u -j should fail malformed typed output instead of silently empty")
rejects(lambda: closure.parse_undefined_names(
    "a-random-nm-header\n"), "unknown nm format must fail")
assert closure.parse_nm(
    "                 U _kagura_image_list_contains\n"
    "00000000 T _kagura_rtld_default_handle\n", defined=False
) == {"_kagura_image_list_contains"}
assert closure.parse_nm(
    "                 U _kagura_image_list_contains\n"
    "00000000 T _kagura_rtld_default_handle\n"
    "00000000 D _kagura_suspicious_image_patterns\n", defined=True
) == {"_kagura_rtld_default_handle", "_kagura_suspicious_image_patterns"}
assert closure.contains_token("int kagura_image_list_contains(void) { return 1; }",
                              "kagura_image_list_contains")
assert not closure.contains_token("kagura_image_list_contains2()",
                                  "kagura_image_list_contains")

with tempfile.TemporaryDirectory(prefix="K11-synthetic-link-closure-") as temp:
    srcdir = Path(temp) / "kagura"
    out = Path(temp) / "out"
    runtime = srcdir / "runtime"
    runtime.mkdir(parents=True)
    out.mkdir()
    (srcdir / "LICENSE").write_text("pinned fake upstream\n")
    (runtime / "anti_debug.c").write_text(
        "void *kagura_rtld_default_handle(void) {return 0;}\n")
    (runtime / "prototypes.c").write_text(
        "extern void kagura_image_list_contains(void);\n")
    (runtime / "provider.c").write_text(
        "int kagura_image_list_contains(void) { return 1; }\n"
        "const char *kagura_suspicious_image_patterns[] = {0};\n")
    ci = out / "05-ci"
    ci.mkdir()
    originals = [ci / "ios.o", out / "ios-kagura-rtld.o",
                 out / "ios-probe.o", out / "ios-app-main.o"]
    for obj in originals:
        obj.write_bytes(b"MOCK_IOS_ARM64_OBJECT_TEST_ONLY")
    nm_map = {
        str(originals[0]): (set(), {"_kagura_rtld_default_handle"}),
        str(originals[1]): (
            {"_kagura_rtld_default_handle"},
            {"_kagura_image_list_contains", "_kagura_suspicious_image_patterns"}),
        str(originals[2]): ({"_dd_k11_ios_parity"}, set()),
        str(originals[3]): (set(), set()),
    }
    genuine_run = closure.run
    recursive_probe = [False]
    def fake_run(args, *, log=None):
        if args[0:2] == ["xcrun", "clang"]:
            path = Path(args[args.index("-c") + 1])
            obj = Path(args[args.index("-o") + 1])
            obj.write_bytes(b"FAKE_CROSS_COMPILED_" + path.name.encode("ascii"))
            if path.name == "provider.c":
                nm_map[str(obj)] = (
                    {"_kagura_image_list_contains",
                     "_kagura_suspicious_image_patterns"},
                    {"_kagura_followup"} if recursive_probe[0] else set())
            elif path.name == "followup.c":
                nm_map[str(obj)] = ({"_kagura_followup"}, set())
            elif path.name == "duplicate.c":
                nm_map[str(obj)] = ({"_kagura_image_list_contains"}, set())
            else:
                nm_map[str(obj)] = (set(), set())
            if log is not None:
                log.write_text("")
            return ""
        if args[0:2] == ["xcrun", "nm"]:
            queried = str(Path(args[-1]))
            if Path(queried).name.startswith("ios-kagura-dependency-"):
                is_followup = b"followup.c" in Path(queried).read_bytes()
                nm_map[queried] = (
                    {"_kagura_followup"} if is_followup else
                    {"_kagura_image_list_contains",
                     "_kagura_suspicious_image_patterns"},
                    set() if is_followup or not recursive_probe[0] else
                    {"_kagura_followup"})
            defs, undefs = nm_map[queried]
            if args[2] == "-gU":
                return "".join(
                    "00000000 " +
                    ("D" if x == "_kagura_suspicious_image_patterns" else "T") +
                    " " + x + "\n" for x in sorted(defs))
            assert args[2:4] == ["-u", "-j"], args
            return "".join(x + "\n" for x in sorted(undefs))
        raise AssertionError("synthetic nm/clang argv unexpected")
    closure.run = fake_run
    try:
        verified = closure.make_closure(
            srcdir, out, "/fake/iPhoneOS.sdk", originals,
            "runtime/anti_debug.c")
        assert verified["final_unresolved_kagura_symbols"] == []
        assert verified["providers_by_undefined_symbol"] == {
            "_kagura_image_list_contains": "runtime/provider.c",
            "_kagura_suspicious_image_patterns": "runtime/provider.c",
        }
        assert len(verified["selected_provider_sources"]) == 1
        assert (out / "ios-runtime-initial-nm.json").is_file()
        raw_samples = json.loads(
            (out / "ios-runtime-initial-nm.json").read_text())
        assert raw_samples["ios-kagura-rtld.o"]["parsed_kagura_symbols"] == [
            "_kagura_image_list_contains", "_kagura_suspicious_image_patterns"]
        assert (out / "ios-runtime-closure.json").is_file()
        assert len((out / "ios-runtime-extra-objects.txt").read_text().splitlines()) == 1
        recursive_probe[0] = True
        (runtime / "followup.c").write_text(
            "int kagura_followup(void) { return 3; }\n")
        (runtime / "provider.c").write_text(
            "extern int kagura_followup(void);\n"
            "int kagura_image_list_contains(void) {return kagura_followup();}\n"
            "const char *kagura_suspicious_image_patterns[] = {0};\n")
        recursive = closure.make_closure(
            srcdir, out, "/fake/iPhoneOS.sdk", originals,
            "runtime/anti_debug.c")
        assert recursive["providers_by_undefined_symbol"]["_kagura_followup"] == "runtime/followup.c"
        assert len(recursive["selected_provider_sources"]) == 2
        (runtime / "duplicate.c").write_text(
            "int kagura_image_list_contains(void) {return 2;}\n")
        rejects(lambda: closure.make_closure(
            srcdir, out, "/fake/iPhoneOS.sdk", originals,
            "runtime/anti_debug.c"), "duplicate pinned C definition")
    finally:
        closure.run = genuine_run

workflow = (ROOT / ".github/workflows/kagura-k11-ios-ipa.yml").read_text()
build = (LAB / "build_ipa.sh").read_text()
src = (LAB / "ios_probe.c").read_text()
ui = (LAB / "ios_app_main.m").read_text()
evidence_source = (LAB / "ipa_evidence.py").read_text()
for required in (
    "workflow_dispatch:", "runs-on: macos-14",
    "scripts/test_kagura_k11_ios_ipa.py",
    "scripts/custom_ollvm/kagura_k10/pilot.py",
    "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
    "bash scripts/custom_ollvm/kagura_k11/build_ipa.sh",
    "DuoDash-Kagura-K11-FIVE-COMPOSED-PASSES-IOS-ARM64-IPA-EXPERIMENTAL",
    "if: always()",
):
    assert required in workflow, required
for required in (
    "05-ci/ios.o", "kagura_rtld_default_handle",
    "ci_runtime_resolver.py", "ios-rtld-discovery.json",
    "K11_FIND_REAL_UPSTREAM_CI_RESOLVER",
    "K11_COMPILE_UPSTREAM_IOS_RESOLVER",
    "Kagura-K11-BUILD-FAILURE.txt",
    "ios-kagura-rtld-compile.log", "ipa-link.log",
    "_kagura_rtld_default_handle",
    "-target arm64-apple-ios15.0",
    "ios-kagura-rtld.o", "ios_app_main.m", "ios_probe.c",
    "KaguraFiveLab-TrollStore-arm64.ipa",
    "package_ipa.py", "ipa_evidence.py",
):
    assert required in build, required
assert workflow.index("Preflight real Kagura CI runtime resolver definition") < workflow.index("Rebuild K10 exact five sequential passes")
assert "ios-rtld-discovery.json" in workflow
assert "Kagura-K11-BUILD-FAILURE.txt" in build
assert "ci_runtime_closure.py" in build
assert "ios-runtime-closure.json" in build
assert "ios-runtime-extra-objects.txt" in build
assert "K11_RESOLVE_PINNED_IOS_RUNTIME_C_DEPENDENCY_CLOSURE" in build
assert "while IFS= read -r object_path; do" in build
assert "mapfile -t" not in build
assert '"${runtime_extra_objects[@]}"' in build
assert "runtime_closure.required_symbols(inputs)" in evidence_source
assert "runtime_closure.defined_of(obj)" in evidence_source
assert "-Wl,-undefined,error" not in build
assert "ios_runtime_closure_sha256" in evidence_source
assert "_kagura_image_list_contains" in evidence_source
assert "_kagura_suspicious_image_patterns" in evidence_source
assert "ios-kagura-rtld-symbols.txt" in build
assert " [Tt] _kagura_rtld_default_handle$" in build
assert "kagura-k9-build/runtime/libkagura_runtime.a" not in build
assert "kagura_vm" not in build
assert "05-ci/ios.o" in evidence_source
assert "k10.verify_report(report, out)" in evidence_source
assert "ios-rtld-discovery.json" in evidence_source
assert "ios-kagura-rtld-symbols.txt" in evidence_source
assert "ios_upstream_resolver_source_sha256" in evidence_source
for required in (
    "dd_k8_evaluate(n, salt)", "dd_k9_mvo_probe(n, salt)",
    "i < 4096U", "0x25a3318e3d7d6525", "0x64e61045bbc4a250",
    "DD_K11_IOS_PIPELINE=MVO_GENC_FSPLIT_IBR_CI",
):
    assert required in src, required
for required in (
    "UIApplicationMain", "LC_UUID", "_dyld_get_image_header(0)",
    "dd_k11_ios_parity", "UIActivityViewController",
    "TARGET_OS_SIMULATOR", "__arm64e__",
):
    assert required in ui, required
for content in (src, ui, build, workflow):
    for forbidden in (
        "MSHook", "ptrauth_strip", "make clean package", "codesign -s",
        "devicectl device install", "ldid -S", "THEOS_PACKAGE_SCHEME",
        "identifierForVendor", "re/RECONSTRUCTION",
    ):
        assert forbidden.lower() not in content.lower(), forbidden
for prod in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k11" not in (ROOT / prod).read_text(encoding="utf-8")
print("KAGURA_K11_PORTABLE_IPA_PASS: standalone arm64 MH_EXECUTE UUID/SHA, "
      "two 4096-vector source oracles, strict device log synthetic negatives, "
      "K10 source link contract; real macOS K11 IPA/iPhone NOT TESTED")
