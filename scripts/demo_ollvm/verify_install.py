#!/usr/bin/env python3
"""Fail-closed install-layout and metadata checks for rootless/Roothide demo DEBs.

Do not rewrite a DEB's control Architecture to match a device: use the
corresponding Theos scheme and inspect its actual produced package.
"""
from __future__ import annotations

import argparse
import plistlib
import stat
from pathlib import Path

SCHEMES = {
    "rootless": ("iphoneos-arm64", "var/jb"),
    "roothide": ("iphoneos-arm64e", ""),
}
EXPECTED_DEPENDS = "mobilesubstrate, firmware"
REQUIRED_FILES = (
    "Library/MobileSubstrate/DynamicLibraries/ Crane.dylib",
    "Library/MobileSubstrate/DynamicLibraries/ Crane.plist",
    "Library/MobileSubstrate/DynamicLibraries/CraneSB.dylib",
    "Library/MobileSubstrate/DynamicLibraries/CraneSupport.dylib",
    "Library/PreferenceBundles/CranePrefs.bundle/CranePrefs",
    "Library/LaunchDaemons/com.opa334.cranehelperd.plist",
    "usr/lib/libcrane.dylib",
    "usr/local/libexec/cranehelperd",
    "usr/local/bin/cranehelperd_start",
)


def read_control(control_root: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in (control_root / "control").read_text(encoding="utf-8").splitlines():
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            fields[key] = value.strip()
    return fields


def verify(source_sandbox: Path, payload: Path, control: Path, scheme: str) -> None:
    if scheme not in SCHEMES:
        raise ValueError(f"Unsupported package scheme: {scheme}")
    arch, prefix = SCHEMES[scheme]
    meta = read_control(control)
    if meta.get("Architecture") != arch:
        raise AssertionError(
            f"{scheme}: expected Architecture: {arch}, got {meta.get('Architecture')!r}"
        )
    if meta.get("Depends") != EXPECTED_DEPENDS:
        raise AssertionError(f"{scheme}: unexpected package Depends: {meta.get('Depends')!r}")
    if meta.get("Package") != "com.opa334.cranereconstruction":
        raise AssertionError("Unexpected package identity")

    reviewed_script = source_sandbox / "layout/DEBIAN/postinst"
    postinst = control / "postinst"
    if not postinst.is_file() or postinst.read_bytes() != reviewed_script.read_bytes():
        raise AssertionError("Packaged postinst differs from scheme-specific reviewed sandbox")
    if stat.S_IMODE(postinst.stat().st_mode) != 0o755:
        raise AssertionError("postinst must be mode 0755")
    if (payload / "DEBIAN").exists():
        raise AssertionError("DEBIAN control archive leaked into data payload")

    base = payload / prefix
    layout = source_sandbox / "layout"
    expected = {
        item.relative_to(layout).as_posix()
        for item in layout.rglob("*")
        if item.is_file() and item.relative_to(layout).parts[0] != "DEBIAN"
    }
    expected.update(REQUIRED_FILES)
    for rel in sorted(expected):
        if not (base / rel).is_file():
            raise AssertionError(f"{scheme}: required package data missing: {prefix}/{rel}")

    if scheme == "rootless":
        # Theos rootless must install all tweak files into /var/jb.
        # A rootful path accidentally left outside the prefix can affect /.
        outside = [
            str(p.relative_to(payload))
            for p in payload.rglob("*")
            if p.is_file() and not p.relative_to(payload).as_posix().startswith("var/jb/")
        ]
        if outside:
            raise AssertionError(f"Rootless payload outside /var/jb: {outside[:8]}")
        script = postinst.read_text(encoding="utf-8")
        for marker in (
            "plist=/var/jb/Library/LaunchDaemons/com.opa334.cranehelperd.plist",
            "binary=/var/jb/usr/local/libexec/cranehelperd",
        ):
            if marker not in script:
                raise AssertionError(f"Rootless postinst missing prefixed path: {marker}")
        launchd = plistlib.loads(
            (base / "Library/LaunchDaemons/com.opa334.cranehelperd.plist").read_bytes()
        )
        if launchd.get("Program") != "/var/jb/usr/local/libexec/cranehelperd":
            raise AssertionError("Rootless launchd Program must use /var/jb path")
    else:
        script = postinst.read_text(encoding="utf-8")
        if "plist=/var/jb/" in script or "binary=/var/jb/" in script:
            raise AssertionError("Roothide must use bootstrap's virtual root paths")

    print(
        f"{scheme} install metadata PASS: Architecture={arch}, "
        f"Depends={EXPECTED_DEPENDS}, {len(expected)} payload paths, "
        "postinst content/mode verified"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--scheme", choices=SCHEMES, required=True)
    args = parser.parse_args()
    verify(args.sandbox, args.payload, args.control, args.scheme)
