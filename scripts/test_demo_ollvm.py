#!/usr/bin/env python3
"""Cross-platform guards for the isolated demo/Crane OLLVM GitHub Actions job."""
import importlib.util
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "scripts/demo_ollvm"
DEMO = ROOT / "demo/reconstruction"
CI = ROOT / ".github/workflows/demo-ollvm-evaluation.yml"

assert (DEMO / "Makefile").is_file(), "User-supplied demo source must be present"
assert (DEMO / "sources/prefs/CRCredits.m").is_file()
credits = (DEMO / "sources/prefs/CRCredits.m").read_text(encoding="utf-8")
for function in ("CRCreditsOpenTwitter", "CRCreditsLocalizedRows"):
    assert re.search(r"\b" + function + r"\s*\(", credits)
assert "CranePrefs_CFLAGS" in (DEMO / "sources/prefs/Makefile").read_text()
assert "SUBPROJECTS +=" in (DEMO / "Makefile").read_text()

pol = json.loads((DIR / "policy.json").read_text(encoding="utf-8"))
assert set(pol) == {"policy_map", "policies"}
assert len(pol["policies"]) == 1
assert pol["policy_map"] == {
    "credits_ui_eval": {
        "enable_split": True, "split_n": 2,
        "enable_bcf": True, "bcf_prob": 30, "bcf_times": 1,
        "enable_fla": True,
        "enable_sub": True, "sub_times": 1,
    }
}
rule = pol["policies"][0]
assert rule["policy"] == "credits_ui_eval"
assert re.fullmatch(rule["module"], "sources/prefs/CRCredits.m")
assert re.fullmatch(rule["module"], "CRCredits.m")
for function in ("CRCreditsOpenTwitter", "CRCreditsLocalizedRows"):
    assert re.fullmatch(rule["func"], function)
for name in ("CRMainDylib", "CRReportRuntimeInjection", "CRBadgeQueueSet",
             "CRRequestAuthentication", "CRCreditsOpenURL"):
    assert not re.fullmatch(rule["func"], name)

workflow = CI.read_text(encoding="utf-8")
assert "workflow_dispatch:" in workflow
assert not re.search(r"(?m)^  (push|pull_request):", workflow)
assert "waruhachi/theos-action@v2.6.3" in workflow
# macos-14 may have Theos's dm.pl packager but not the dpkg-deb extractor.
assert "name: Install Debian package inspection tool" in workflow
assert "brew install dpkg" in workflow
assert "dpkg-deb --version" in workflow
assert workflow.count("command -v dpkg-deb") == 3
assert workflow.count('dpkg-deb -x "$deb"') == 2
# -x extracts data only; the verifier also requires postinst from control.tar.
assert workflow.count('dpkg-deb -e "$deb"') == 2
for variant in ("plain", "ollvm"):
    assert f'dpkg-deb -e "$deb" "$RUNNER_TEMP/demo-control-{variant}"' in workflow
    assert f'test -f "$RUNNER_TEMP/demo-control-{variant}/postinst"' in workflow
    assert (
        '"$RUNNER_TEMP/demo-expanded-' + variant + '" '
        '"$RUNNER_TEMP/demo-control-' + variant + '"'
    ) in workflow
    extract = workflow.index(f'dpkg-deb -x "$deb" "$RUNNER_TEMP/demo-expanded-{variant}"')
    control = workflow.index(f'dpkg-deb -e "$deb" "$RUNNER_TEMP/demo-control-{variant}"')
    verify = workflow.index(
        f'"$RUNNER_TEMP/demo-expanded-{variant}" "$RUNNER_TEMP/demo-control-{variant}"',
        control,
    )
    assert extract < control < verify
verifier_source = (DEMO / "tools/verify_package_layout.py").read_text(encoding="utf-8")
assert "postinst = pathlib.Path(control_arg) / \"postinst\"" in verifier_source
assert "postinst.read_bytes() != original.read_bytes()" in verifier_source
assert "postinst.stat().st_mode & 0o777 != 0o755" in verifier_source
assert workflow.index("name: Install Debian package inspection tool") < workflow.index(
    "name: Prepare and build unmodified demo baseline"
)
assert "demo/reconstruction" in workflow
assert "CRANEPREFS" not in workflow
assert workflow.count("make clean package FINALPACKAGE=1") == 2
assert "llvm@19" in workflow and "592f215f852e3957da01b2b15024dc63713a462e" in workflow
assert 'TARGET_CC="$compiler"' in workflow
assert 'compiler="$GITHUB_WORKSPACE/scripts/demo_ollvm/compiler_select.py"' in workflow
assert 'chmod +x "$compiler"' in workflow
assert 'TARGET_CXX="$(xcrun --find clang++)"' in workflow
assert "DEMO_OLLVM_SELECTED: CRCredits.m (arm64) -> LLVM19" in workflow
assert "DEMO_OLLVM_BYPASS: CRCredits.m (arm64e) -> Apple Clang" in workflow
assert 'if [ "$selected" -ne 1 ] || [ "$bypassed" -ne 1 ]; then' in workflow
assert 'TARGET_CC="$DEMO_OLLVM_CLANG"' not in workflow
assert "-fmodules-cache-path=\"$RUNNER_TEMP/demo-ollvm-llvm19-modules\"" in workflow
assert "-print-resource-dir" in workflow
assert "__stddef_max_align_t.h" in workflow
assert workflow.index("name: Preflight LLVM19 resource headers for Objective-C") < workflow.index(
    "name: Build demo with OLLVM scoped only to CranePrefs credits"
)
assert "CranePrefs_CFLAGS += -O1 -fpass-plugin=" not in workflow
assert "CraneDemo-Baseline-EXPERIMENTAL" in workflow
assert "CraneDemo-OLLVM-EXPERIMENTAL" in workflow
assert workflow.index("name: Upload clean demo baseline") < workflow.index(
    "name: Build demo with OLLVM scoped only to CranePrefs credits"
)
assert "verify_architectures.py" in workflow
assert "verify_package_layout.py" in workflow
assert "scripts/demo_ollvm/verify.py" in workflow
assert "NOT-FOR-PRODUCTION.txt" in workflow
assert "Build Reconstruction" not in workflow
assert "demo-ollvm-evaluation.yml" not in (
    ROOT / ".github/workflows/build.yml"
).read_text(encoding="utf-8")

def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

prepare = load("demo_prepare", DIR / "prepare.py")
check = load("demo_verify", DIR / "verify.py")
select = load("demo_compiler_select", DIR / "compiler_select.py")
assert select.is_selected_compile(["-c", "CRCredits.m", "-arch", "arm64"])
assert not select.is_selected_compile(["-c", "../prefs/CRCredits.m", "-arch", "arm64e"])
assert select.compile_architecture(["-c", "CRCredits.m", "-target", "arm64-apple-ios11.0"]) == "arm64"
assert select.compile_architecture(["-c", "CRCredits.m", "-target=arm64e-apple-ios11.0"]) == "arm64e"
assert select.compile_architecture(["-c", "CRCredits.m", "-arch", "arm64e"]) == "arm64e"
for invalid in (["-c", "CRCredits.m"], ["-c", "CRCredits.m", "-arch", "arm64", "-target", "arm64e-apple-ios11.0"]):
    try:
        select.compile_architecture(invalid)
    except RuntimeError:
        pass
    else:
        raise AssertionError(f"Ambiguous/missing architecture must fail closed: {invalid!r}")
for command in (
    ["-c", "../common/CRCommon.m", "-arch", "arm64e"],
    ["-c", "CRPreferences.m"],
    ["-c", "CRMainDylib.m"],
    ["-o", "CranePrefs", "CRCredits.m"],
    ["-c", "Prefix.pch"],
):
    assert not select.is_selected_compile(command), command
assert set(check.PASSES) == {"split", "bcf", "fla", "sub"}
assert set(check.FUNCTIONS) == {"CRCreditsOpenTwitter", "CRCreditsLocalizedRows"}

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    template = tmp / "source"
    makefiles = {
        "Makefile": "ROOT_CFLAGS=1\n",
        "sources/prefs/Makefile": "CranePrefs_CFLAGS = -fobjc-arc\ninclude $(THEOS_MAKE_PATH)/bundle.mk\n",
        "sources/prefs/CRCredits.m": credits,
        "sources/maindylib/Makefile": "main\n",
        "sources/cranesb/Makefile": "sb\n",
    }
    for path, content in makefiles.items():
        full = template / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    plug = tmp / "Obfuscator.dylib"
    plug.write_bytes(b"fixture plugin")

    plain = tmp / "plain"
    obf = tmp / "obf"
    prepare.prepare(template, plain, "baseline", None)
    prepare.prepare(template, obf, "ollvm", plug)
    assert (plain / "sources/prefs/Makefile").read_text() == makefiles["sources/prefs/Makefile"]
    assert "fpass-plugin=" not in (plain / "sources/prefs/Makefile").read_text()
    assert "fpass-plugin=" not in (obf / "sources/prefs/Makefile").read_text()
    assert (obf / "sources/prefs/Makefile").read_bytes() == (
        template / "sources/prefs/Makefile"
    ).read_bytes()
    resource = tmp / "llvm19" / "lib" / "clang" / "19"
    (resource / "include").mkdir(parents=True)
    (resource / "include/stddef.h").write_text("mock", encoding="utf-8")
    values = {
        "DEMO_APPLE_CLANG": "/opt/apple/clang",
        "DEMO_OLLVM_CLANG": "/opt/llvm19/clang",
        "DEMO_OLLVM_PLUGIN": str(plug),
        "DEMO_OLLVM_RESOURCE_DIR": str(resource),
        "DEMO_OLLVM_MODULE_CACHE": str(tmp / "llvm19-cache"),
    }
    source_args = ["-c", "CRCredits.m", "-arch", "arm64"]
    selected = select.command_for(source_args, values)
    assert selected[0] == values["DEMO_OLLVM_CLANG"]
    assert selected[-2:] == ["-resource-dir", str(resource)]
    assert f"-fpass-plugin={plug}" in selected
    assert any(flag.startswith("-fmodules-cache-path=") for flag in selected)
    non_selected = select.command_for(["-c", "../common/CRCommon.m"], values)
    assert non_selected == ["/opt/apple/clang", "-c", "../common/CRCommon.m"]
    arm64e_args = ["-c", "../prefs/CRCredits.m", "-arch", "arm64e"]
    assert select.command_for(arm64e_args, values) == [values["DEMO_APPLE_CLANG"], *arm64e_args]
    assert "-fpass-plugin" not in " ".join(select.command_for(arm64e_args, values))
    try:
        select.command_for(["-c", "CRCredits.m"], values)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Missing CRCredits architecture must fail closed")
    try:
        select.command_for(source_args, {"DEMO_APPLE_CLANG": "/opt/apple/clang"})
    except RuntimeError:
        pass
    else:
        raise AssertionError("No LLVM toolchain must fail selected compilation")
    assert (obf / "sources/maindylib/Makefile").read_text() == makefiles["sources/maindylib/Makefile"]
    assert (obf / "sources/cranesb/Makefile").read_text() == makefiles["sources/cranesb/Makefile"]
    assert (obf / "policy.json").read_bytes() == (obf / "sources/prefs/policy.json").read_bytes()
    try:
        prepare.prepare(template, obf, "ollvm", plug)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Sandbox preparation must refuse an overwrite")

    expanded_plain = tmp / "plain_pkg"
    expanded_obf = tmp / "obf_pkg"
    expected = check.PREFS_EXECUTABLE
    first = b"header" + b"".join(check.REQUIRED_CLASSES) + b"plain"
    second = b"header" + b"".join(check.REQUIRED_CLASSES) + b"protected"
    for root, binary in ((expanded_plain, first), (expanded_obf, second)):
        dest = root / expected
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(binary)
        (root / "Library/a.plist").write_text("same", encoding="utf-8")
    info = check.verify_packages(expanded_plain, expanded_obf)
    assert info["files"] == 2
    assert info["baseline_sha"] != info["obf_sha"]
    (expanded_obf / "Library/a.plist").unlink()
    try:
        check.verify_packages(expanded_plain, expanded_obf)
    except AssertionError:
        pass
    else:
        raise AssertionError("Package path mismatch must fail")

good_log = "\n".join(
    f">>>> run {pas} on {name}"
    for name in check.FUNCTIONS for pas in check.PASSES
)
assert all(count == 1 for count in check.verify_passes(good_log).values())
routing_log = (
    "DEMO_OLLVM_SELECTED: CRCredits.m (arm64) -> LLVM19; resource_dir=/tmp/llvm19\n"
    "DEMO_OLLVM_BYPASS: CRCredits.m (arm64e) -> Apple Clang; reason=LLVM19-arm64e.old"
)
check.verify_compiler_routes(routing_log)
for invalid_route in (
    routing_log.splitlines()[0],
    routing_log + "\nDEMO_OLLVM_SELECTED: CRCredits.m (arm64) -> LLVM19; duplicate",
    routing_log.replace("(arm64e)", "(arm64)"),
):
    try:
        check.verify_compiler_routes(invalid_route)
    except AssertionError:
        pass
    else:
        raise AssertionError("Missing/extra/invalid compiler routes must fail")
for broken in (
    good_log.splitlines()[1],
    good_log + "\n>>>> run fla on CRReportRuntimeInjection",
    good_log + "\n>>>> run fla on CRCreditsOpenTwitter",
):
    try:
        check.verify_passes(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError("Missing or unexpected pass must fail")

print("Crane demo OLLVM scoped CI, two pass-targets and strict package audit: PASS")
