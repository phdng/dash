#!/usr/bin/env python3
"""Prepare two isolated Crane demos using a real Theos package scheme.

Package architecture is a Debian control property, NOT an arm64 CPU subtype:
rootless -> iphoneos-arm64, roothide -> iphoneos-arm64e.
Sandbox-only layout changes are necessary because demo is originally
rootful/roothide-oriented and its postinst contains absolute paths.
"""
from __future__ import annotations

import argparse
import json
import plistlib
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY = HERE / "policy.json"
BUNDLE_INCLUDE = "include $(THEOS_MAKE_PATH)/bundle.mk"
DEPENDS_ORIGINAL = (
    "Depends: mobilesubstrate, ellekit, libhooker, firmware, "
    "altlist, activator, choicy"
)
DEPENDS_MINIMAL = "Depends: mobilesubstrate, firmware"
ROOTLESS_PREFIX = "/var/jb"


def guarded_replace(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(old) != 1:
        raise ValueError(f"Unexpected source layout for {path}: expected exact marker {old!r}")
    path.write_text(content.replace(old, new), encoding="utf-8")


def adapt_package_scheme(destination: Path, scheme: str) -> None:
    """Change only disposable sandbox files; do not rewrite DEB architecture."""
    if scheme == "rootful":
        return
    if scheme not in ("rootless", "roothide"):
        raise ValueError(f"Unsupported Theos scheme: {scheme}")

    guarded_replace(destination / "control", DEPENDS_ORIGINAL, DEPENDS_MINIMAL)
    if scheme == "roothide":
        # Theos roothide automatically chooses iphoneos-arm64e metadata and
        # virtual package paths. The original demo Makefile has a roothide
        # feature flag and avoids unused AltList linking for that scheme.
        return

    # Standard rootless uses iphoneos-arm64 metadata and /var/jb staging.
    # Unlike roothide, rootless has no virtual root path translation.
    master = destination / "Makefile"
    old_stage = '$(THEOS_STAGING_DIR)/Library/MobileSubstrate/DynamicLibraries'
    master_text = master.read_text(encoding="utf-8")
    if master_text.count(old_stage) != 8:
        raise ValueError("Unexpected main Makefile staging rules for rootless")
    master_text = master_text.replace(
        old_stage, '$(THEOS_STAGING_DIR)/var/jb/Library/MobileSubstrate/DynamicLibraries'
    )
    # Normal Theos staging can place the compiled Crane.dylib in the
    # unprefixed tree even though our reconstructed filter-plist overrides
    # target /var/jb. Repair only that exact known filename BEFORE dm.pl.
    # Do not weaken the post-package path/content audit.
    hook = (
        "\n# Isolated rootless staging preflight: preserve the recovered leading space.\n"
        "before-package::\n"
        "\t@python3 \"$(THEOS_PROJECT_DIR)/tools/normalize_rootless_stage.py\" "
        "\"$(THEOS_STAGING_DIR)\"\n"
    )
    if "normalize_rootless_stage.py" in master_text:
        raise ValueError("Unexpected rootless Makefile layout; refusing duplicate hook")
    separator = "" if master_text.endswith("\n") else "\n"
    master.write_text(master_text + separator + hook, encoding="utf-8")
    target_helper = destination / "tools/normalize_rootless_stage.py"
    if target_helper.exists():
        raise ValueError("Rootless staging normalizer already present in sandbox")
    shutil.copyfile(HERE / "normalize_rootless_stage.py", target_helper)
    # The credits UI does not call AltList symbols, so do not link an unused
    # optional framework into the rootless build. Theos handles rootless rpaths.
    guarded_replace(
        destination / "sources/prefs/Makefile",
        "ifneq ($(THEOS_PACKAGE_SCHEME),roothide)",
        "ifeq ($(THEOS_PACKAGE_SCHEME),rootful)",
    )
    postinst = destination / "layout/DEBIAN/postinst"
    guarded_replace(
        postinst,
        "plist=/Library/LaunchDaemons/com.opa334.cranehelperd.plist",
        "plist=/var/jb/Library/LaunchDaemons/com.opa334.cranehelperd.plist",
    )
    guarded_replace(
        postinst,
        "binary=/usr/local/libexec/cranehelperd",
        "binary=/var/jb/usr/local/libexec/cranehelperd",
    )
    launchd = destination / "layout/Library/LaunchDaemons/com.opa334.cranehelperd.plist"
    configuration = plistlib.loads(launchd.read_bytes())
    if configuration.get("Program") != "/usr/local/libexec/cranehelperd":
        raise ValueError("Unexpected launchd Program path: cannot adapt rootless safely")
    configuration["Program"] = "/var/jb/usr/local/libexec/cranehelperd"
    launchd.write_bytes(plistlib.dumps(configuration, sort_keys=False))


def prepare(source: Path, destination: Path, variant: str, plugin: Path | None,
            scheme: str = "rootful") -> None:
    if variant not in ("baseline", "ollvm"):
        raise ValueError("Unknown build variant")
    if scheme not in ("rootful", "rootless", "roothide"):
        raise ValueError("Unknown package scheme")
    if not (source / "Makefile").is_file() or not (
        source / "sources/prefs/CRCredits.m"
    ).is_file():
        raise ValueError("demo/reconstruction/Makefile and CRCredits.m are required")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing sandbox: {destination}")
    shutil.copytree(
        source, destination,
        ignore=shutil.ignore_patterns(".theos", "packages", "obj", "build.log", "*.deb"),
    )
    adapt_package_scheme(destination, scheme)
    if variant == "baseline":
        return
    if plugin is None or not plugin.is_file() or not plugin.is_absolute():
        raise ValueError("OLLVM variant requires a compiled absolute plugin path")
    if any(c.isspace() for c in str(plugin)):
        raise ValueError("Plugin path must not contain whitespace")

    configuration = json.loads(POLICY.read_text(encoding="utf-8"))
    if set(configuration) != {"policy_map", "policies"}:
        raise ValueError("Unexpected OLLVM policy shape")
    # The pass reads policy.json from the compiler's current working directory.
    content = POLICY.read_text(encoding="utf-8")
    for directory in (destination, destination / "sources/prefs"):
        (directory / "policy.json").write_text(content, encoding="utf-8")
    makefile = destination / "sources/prefs/Makefile"
    if makefile.read_text(encoding="utf-8").count(BUNDLE_INCLUDE) != 1:
        raise ValueError("Unexpected CranePrefs Makefile layout")

    # Only the scheme-specific sandbox adapter can change package files.
    for rel in ("sources/maindylib/Makefile", "sources/cranesb/Makefile"):
        assert (destination / rel).read_bytes() == (source / rel).read_bytes()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--variant", choices=("baseline", "ollvm"), required=True)
    parser.add_argument("--scheme", choices=("rootful", "rootless", "roothide"), default="rootful")
    parser.add_argument("--plugin", type=Path)
    args = parser.parse_args()
    prepare(args.source.resolve(), args.dest.resolve(), args.variant,
            args.plugin.resolve() if args.plugin is not None else None, args.scheme)
    print(f"Demo {args.variant} / {args.scheme} sandbox: {args.dest} (original untouched)")
