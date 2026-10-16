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
    "credits_ui_strong_eval": {
        "enable_split": True, "split_n": 4,
        "enable_bcf": True, "bcf_prob": 100, "bcf_times": 2,
        "enable_fla": True,
        "enable_sub": True, "sub_times": 3,
    }
}
rule = pol["policies"][0]
assert rule["policy"] == "credits_ui_strong_eval"
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
assert "CraneDemo-OLLVM-STRONG-${{ matrix.variant }}-EXPERIMENTAL" in workflow
assert "CRCredits-llvm19-no-pass-arm64.o" in workflow
assert "CRCredits-ollvm-strong-arm64.o" in workflow
assert "CranePrefs-ollvm-strong-arm64" in workflow
assert "lipo -thin arm64" in workflow
assert "cmp -s" in workflow
assert "CRCredits-arm64.diff" in workflow
assert "scripts/demo_ollvm/analyze_binary.py" in workflow
assert 'if [ "$selected" -ne 1 ] || [ "$bypassed" -ne 1 ]; then' in workflow
assert 'TARGET_CC="$DEMO_OLLVM_CLANG"' not in workflow
assert "-fmodules-cache-path=\"$RUNNER_TEMP/demo-ollvm-llvm19-modules\"" in workflow
assert "-print-resource-dir" in workflow
assert "__stddef_max_align_t.h" in workflow
assert workflow.index("name: Preflight LLVM19 resource headers for Objective-C") < workflow.index(
    "name: Build demo with OLLVM scoped only to CranePrefs credits"
)
assert "CranePrefs_CFLAGS += -O1 -fpass-plugin=" not in workflow
assert "CraneDemo-Baseline-${{ matrix.variant }}-EXPERIMENTAL" in workflow
assert "CraneDemo-OLLVM-STRONG-${{ matrix.variant }}-EXPERIMENTAL" in workflow
assert "CraneDemo-OLLVM-STRONG-${{ matrix.variant }}-Diagnostics" in workflow
assert "Crane-demo-${{ matrix.variant }}-ollvm-strong.deb" in workflow
assert 'DEMO_OLLVM_CONTROL_OBJECT="$RUNNER_TEMP/demo-comparison/CRCredits-llvm19-no-pass-arm64.o"' in workflow
assert 'test -s "$DEMO_OLLVM_CONTROL_OBJECT"' in workflow
assert 'scripts/demo_ollvm/analyze_binary.py' in workflow
assert 'llvm-objdump' in workflow
for file in ("CRCredits-disassembly-report.md", "CRCredits-llvm19-no-pass-arm64.asm",
             "CRCredits-ollvm-strong-arm64.asm", "CRCredits-arm64.diff"):
    assert file in workflow
assert workflow.index('scripts/demo_ollvm/analyze_binary.py') < workflow.index(
    'Crane-demo-${{ matrix.variant }}-ollvm-strong.deb'
)
for scheme, repo, arch in (
    ("rootless", "theos/theos", "iphoneos-arm64"),
    ("roothide", "roothide/theos", "iphoneos-arm64e"),
):
    assert f"scheme: {scheme}" in workflow
    assert f"theos_repo: {repo}" in workflow
    assert f"deb_arch: {arch}" in workflow
assert "theos-src: ${{ matrix.theos_repo }}" in workflow
assert workflow.count('THEOS_PACKAGE_SCHEME="${{ matrix.scheme }}"') == 2
assert workflow.count('test "$(dpkg-deb -f "$deb" Architecture)" = "${{ matrix.deb_arch }}"') == 2
assert workflow.count("scripts/demo_ollvm/verify_install.py") == 2
assert workflow.count(' --scheme "${{ matrix.scheme }}"') >= 3
assert workflow.count("verify_helper_entitlements.py") == 2
assert "--report \"$RUNNER_TEMP/demo-comparison/report.md\" --scheme \"${{ matrix.scheme }}\"" in workflow
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
install = load("demo_install_verify", DIR / "verify_install.py")
# Device runtime remains a manual, separately recorded gate after successful
# CI and package installation. Never silently treat package audit as UI PASS.
device_plan = (ROOT / "docs/CRANE_ROOTHIDE_DEVICE_TEST.md").read_text(encoding="utf-8")
assert "iPhone 6s" in device_plan and "15.8.8" in device_plan
assert "Installation PASS" in device_plan and "Runtime Credits STRONG PASS" in device_plan
assert "CHƯA TEST" in device_plan
for case in range(1, 10):
    assert f"D{case:02d}" in device_plan
assert "docs/CRANE_ROOTHIDE_DEVICE_TEST.md" in (
    DIR / "verify.py"
).read_text(encoding="utf-8")
assert "Device validation" in (DIR / "verify.py").read_text(encoding="utf-8")
assert "CRANE_ROOTHIDE_DEVICE_TEST.md" in (
    ROOT / "docs/DEMO_OLLVM.md"
).read_text(encoding="utf-8")
select = load("demo_compiler_select", DIR / "compiler_select.py")
audit = load("demo_assembly_audit", DIR / "analyze_binary.py")
assert audit.ARM64_CPU == 0x0100000C
sample_assembly = ("_CRCreditsOpenTwitter:\n"
                   "    stp x29, x30, [sp, #-0x10]!\n"
                   "    b.eq L1\n"
                   "    cbnz x0, L2\n"
                   "    ret\n")
assert len(audit.instructions(sample_assembly)) == 4
assert audit.conditional_count(audit.instructions(sample_assembly)) == 2
assert audit.instructions("__text:\n00000: 01 02 03 04  .word 0\n") == []
assert "STRONG" in (ROOT / "docs/DEMO_OLLVM.md").read_text(encoding="utf-8")
assert "không phải mã hóa" in (ROOT / "docs/DEMO_OLLVM.md").read_text(encoding="utf-8")
assert install.SCHEMES == {
    "rootless": ("iphoneos-arm64", "var/jb"),
    "roothide": ("iphoneos-arm64e", ""),
}
assert check.PACKAGING_PREFIXES["rootless"].as_posix() == "var/jb"
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
    plain_args = select.plain_control_command(
        selected + ["-o", str(tmp / "protected.o"), "-MF", str(tmp / "protected.d")],
        tmp / "control.o",
    )
    assert "-fpass-plugin=" not in " ".join(plain_args)
    assert plain_args[0] == selected[0]
    assert plain_args[plain_args.index("-o") + 1] == str(tmp / "control.o")
    assert plain_args[plain_args.index("-MF") + 1] == str(tmp / "control.d")
    assert plain_args[-2:] == ["-MF", str(tmp / "control.d")]
    assert [a for a in selected if a.startswith("-fpass-plugin=")] == [f"-fpass-plugin={plug}"]
    # Exactly the same flags/compiler except plugin removal and output files.
    assert plain_args == [
        arg for arg in selected if not arg.startswith("-fpass-plugin=")
    ] + ["-o", str(tmp / "control.o"), "-MF", str(tmp / "control.d")]
    try:
        select.plain_control_command(selected, tmp / "control.o")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Control compile must require a known -o path")
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
    # Exercise scheme adaptation on a real, complete demo source tree.
    rootless = tmp / "rootless"
    roothide = tmp / "roothide"
    prepare.prepare(DEMO, rootless, "baseline", None, "rootless")
    prepare.prepare(DEMO, roothide, "baseline", None, "roothide")
    original_postinst = (DEMO / "layout/DEBIAN/postinst").read_bytes()
    original_make = (DEMO / "Makefile").read_bytes()
    assert original_postinst == (roothide / "layout/DEBIAN/postinst").read_bytes()
    assert original_make == (roothide / "Makefile").read_bytes()
    assert "THEOS_STAGING_DIR)/var/jb/Library/" in (rootless / "Makefile").read_text()
    assert "plist=/var/jb/Library/LaunchDaemons" in (
        rootless / "layout/DEBIAN/postinst"
    ).read_text()
    import plistlib
    assert plistlib.loads((rootless / "layout/Library/LaunchDaemons/com.opa334.cranehelperd.plist").read_bytes())["Program"] == "/var/jb/usr/local/libexec/cranehelperd"
    assert "ifneq ($(THEOS_PACKAGE_SCHEME),roothide)" in (roothide / "sources/prefs/Makefile").read_text()
    assert "ifeq ($(THEOS_PACKAGE_SCHEME),rootful)" in (rootless / "sources/prefs/Makefile").read_text()
    assert "Depends: mobilesubstrate, firmware" in (rootless / "control").read_text()
    assert "Depends: mobilesubstrate, firmware" in (roothide / "control").read_text()
    assert (DEMO / "Makefile").read_bytes() == original_make
    assert (DEMO / "layout/DEBIAN/postinst").read_bytes() == original_postinst
    # Synthetic files verify the artifact's package architecture, install
    # prefix and postinst guards without needing a macOS toolchain.
    import shutil
    import os
    from contextlib import nullcontext
    from unittest.mock import patch

    def synthetic_mode_context(mode: int):
        # Windows NTFS does not preserve POSIX executable mode bits.
        return (patch.object(install.stat, "S_IMODE", return_value=mode)
                if os.name == "nt" else nullcontext())

    for scheme, sandbox in (("rootless", rootless), ("roothide", roothide)):
        payload = tmp / f"{scheme}-payload"
        control_dir = tmp / f"{scheme}-control"
        control_dir.mkdir()
        arch, prefix_str = install.SCHEMES[scheme]
        base = payload / prefix_str
        for f in (sandbox / "layout").rglob("*"):
            if f.is_file() and f.relative_to(sandbox / "layout").parts[0] != "DEBIAN":
                target = base / f.relative_to(sandbox / "layout")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, target)
        for rel in install.REQUIRED_FILES:
            file = base / rel
            if not file.is_file():
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b"mock Mach-O binary")
        (control_dir / "postinst").write_bytes((sandbox / "layout/DEBIAN/postinst").read_bytes())
        (control_dir / "postinst").chmod(0o755)
        control_text = (
            f"Package: com.opa334.cranereconstruction\nArchitecture: {arch}\n"
            "Depends: mobilesubstrate, firmware\n"
        )
        (control_dir / "control").write_text(control_text, encoding="utf-8")
        with synthetic_mode_context(0o755):
            install.verify(sandbox, payload, control_dir, scheme)
        (control_dir / "control").write_text(control_text.replace(arch, "iphoneos-arm"), encoding="utf-8")
        try:
            with synthetic_mode_context(0o755):
                install.verify(sandbox, payload, control_dir, scheme)
        except AssertionError:
            pass
        else:
            raise AssertionError("Wrong DEB architecture must fail")
        (control_dir / "control").write_text(control_text, encoding="utf-8")
        if scheme == "rootless":
            leaked = payload / "Library/unsafe-rootful-file"
            leaked.parent.mkdir(parents=True, exist_ok=True)
            leaked.write_text("bad", encoding="utf-8")
            try:
                with synthetic_mode_context(0o755):
                    install.verify(sandbox, payload, control_dir, scheme)
            except AssertionError:
                pass
            else:
                raise AssertionError("Rootless root-path leak must fail")
            leaked.unlink()
        (control_dir / "postinst").chmod(0o644)
        try:
            with synthetic_mode_context(0o644):
                install.verify(sandbox, payload, control_dir, scheme)
        except AssertionError:
            pass
        else:
            raise AssertionError("Wrong postinst permissions must fail")
    try:
        prepare.prepare(template, obf, "ollvm", plug)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Sandbox preparation must refuse an overwrite")

    # Offline Mach-O fixture for the same-compiler disassembly audit.
    import struct
    from unittest.mock import patch as mock_patch
    hdr = struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0, 1, 0, 0, 0, 0)
    control_obj = tmp / "mock-control.o"
    protected_obj = tmp / "mock-protected.o"
    control_obj.write_bytes(hdr + b"no-pass" * 20)
    protected_obj.write_bytes(hdr + b"obfuscated" * 20)
    control_asm = "_CRCreditsOpenTwitter:\n" + "    cmp x0, x1\n" * 20 + "    b.eq L1\n"
    strong_asm = "_CRCreditsOpenTwitter:\n" + "    cmp x0, x1\n" * 38 + "    cbnz x0, L2\n"
    with mock_patch.object(audit, "disassemble", side_effect=[control_asm, strong_asm]):
        report = audit.analyze(control_obj, protected_obj, "fake-llvm-objdump", tmp / "disasm")
    assert "1.86x" in report
    assert "no-pass vs OLLVM" in report
    assert (tmp / "disasm/CRCredits-arm64.diff").is_file()
    assert (tmp / "disasm/CRCredits-llvm19-no-pass-arm64.asm").is_file()
    assert (tmp / "disasm/CRCredits-ollvm-strong-arm64.asm").is_file()
    try:
        audit.verify_arm64_object(tmp / "disasm/CRCredits-arm64.diff")
    except AssertionError:
        pass
    else:
        raise AssertionError("Non Mach-O audit input must fail")
    with mock_patch.object(audit, "disassemble", side_effect=[control_asm, control_asm]):
        try:
            audit.analyze(control_obj, protected_obj, "fake-llvm-objdump", tmp / "sameasm")
        except AssertionError:
            pass
        else:
            raise AssertionError("Identical disassembly must fail")
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
    prefix = Path("var/jb")
    rootless_plain = tmp / "rootless_plain_pkg"
    rootless_obf = tmp / "rootless_obf_pkg"
    for src, dest in ((expanded_plain, rootless_plain), (expanded_obf, rootless_obf)):
        target = dest / prefix / expected
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((src / expected).read_bytes())
    assert check.verify_packages(rootless_plain, rootless_obf, "rootless")["files"] == 1
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
