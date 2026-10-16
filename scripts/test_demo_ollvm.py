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
assert 'TARGET_CC="$DEMO_OLLVM_CLANG"' in workflow
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
    assert "fpass-plugin=" in (obf / "sources/prefs/Makefile").read_text()
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
for broken in (
    good_log.splitlines()[1],
    good_log + "\n>>>> run fla on CRReportRuntimeInjection",
):
    try:
        check.verify_passes(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError("Missing or unexpected pass must fail")

print("Crane demo OLLVM scoped CI, two pass-targets and strict package audit: PASS")
