#!/usr/bin/env python3
"""K24 workflow gate: require an explicitly approved Ed25519 public key in Mode B.

Only public material is inspected. This is NOT an immutable on-device
trust anchor; the separately approved fingerprint is typed by the user
at workflow_dispatch, independent of the repository's public-key variable.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

import package as k24


def validate(mode: str, public_b64: str, trusted_spki_sha256: str) -> str:
    if mode == "false":
        if trusted_spki_sha256:
            raise AssertionError("K24 Mode A must not receive a signed-mode SPKI fingerprint")
        return "K24_MODE_A_MEASUREMENT_ONLY: compiled key intentionally disabled"
    if mode != "true":
        raise AssertionError("K24 explicit boolean require_signed_mode input missing/invalid")
    if not re.fullmatch(r"[a-f0-9]{64}", trusted_spki_sha256):
        raise AssertionError("K24 Mode B needs separately approved 64-hex SPKI SHA256")
    raw = k24.public_key(public_b64)
    if len(raw) != 32:
        raise AssertionError("K24 Mode B missing repository public Ed25519 key B64")
    try:
        key = Ed25519PublicKey.from_public_bytes(raw)
        der = key.public_bytes(serialization.Encoding.DER,
                               serialization.PublicFormat.SubjectPublicKeyInfo)
    except (ValueError, TypeError) as exc:
        raise AssertionError("K24 Mode B invalid Ed25519 public raw key") from exc
    digest = hashlib.sha256(der).hexdigest()
    if not hmac.compare_digest(digest, trusted_spki_sha256):
        raise AssertionError("K24 Mode B SPKI fingerprint mismatch: not externally approved key")
    return "K24_MODE_B_PUBLIC_KEY_APPROVED: Ed25519 public only; private outside CI"


def main() -> None:
    print(validate(os.environ.get("K24_REQUIRE_SIGNED_MODE", ""),
                   os.environ.get("K24_TRUSTED_ED25519_PUBLIC_KEY_B64", ""),
                   os.environ.get("K24_EXPECTED_SPKI_SHA256", "")))


if __name__ == "__main__":
    main()
