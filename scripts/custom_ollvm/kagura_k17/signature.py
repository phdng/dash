#!/usr/bin/env python3
"""K17 independently trusted Ed25519 OFFLINE signature for K16 raw manifest.

Never treat a key bundled alongside the artifact as an independent trust
anchor. The trusted Ed25519 SPKI SHA256 must be supplied separately. Never
include private key material in artifacts. Neither code-signing, on-device
integrity nor secure-enclave attestation is established by these signatures.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import re
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kagura_k16"))
import macho_measure as k16  # noqa: E402

DOMAIN = b"DuoDash/K17/K16/MachOTextOfflineEd25519/v1\0"
SCOPE = "K17_EXTERNAL_TRUST_ANCHOR_ED25519_K16_OFFLINE_MANIFEST_ONLY"
SIGNATURE_FILE = "Kagura-K17-K16-MANIFEST.ed25519"
RECEIPT_FILE = "Kagura-K17-SIGNATURE-RECEIPT.json"
HEX64 = re.compile(r"[a-f0-9]{64}\Z")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def spki_der(key: ed25519.Ed25519PublicKey) -> bytes:
    return key.public_bytes(encoding=serialization.Encoding.DER,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo)


def load_trusted(public_pem: Path, expected_sha: str) -> tuple[ed25519.Ed25519PublicKey, str]:
    if not HEX64.fullmatch(expected_sha):
        raise AssertionError("K17 requires literal expected SHA-256, separately approved")
    if not public_pem.is_file() or public_pem.is_symlink():
        raise AssertionError("K17 trusted public PEM file missing or symlinked")
    raw = public_pem.read_bytes()
    if not (64 <= len(raw) <= 4096):
        raise AssertionError("K17 trusted public key PEM size invalid")
    try:
        key = serialization.load_pem_public_key(raw)
    except (ValueError, TypeError) as exc:
        raise AssertionError("K17 failed to parse trusted PEM key") from exc
    if not isinstance(key, ed25519.Ed25519PublicKey):
        raise AssertionError("K17 only supports Ed25519 public trust anchors")
    actual = digest(spki_der(key))
    if not hmac.compare_digest(actual, expected_sha):
        raise AssertionError("K17 public key SPKI SHA256 != independently approved fingerprint")
    return key, actual


def replay_manifest(out: Path) -> bytes:
    """Reconstruct from K13/K14 REAL original file hashes before signing."""
    p = out / k16.MANIFEST
    if not p.is_file() or p.is_symlink():
        raise AssertionError("K17 missing original K16 offline manifest")
    raw = p.read_bytes()
    if not 100 <= len(raw) <= 512 * 1024:
        raise AssertionError("K17 unreasonable offline manifest size")
    k16.replay(out)
    manifest = json.loads(raw)
    if (manifest.get("reference_kind") != "UNSIGNED_OFFLINE_POST_LINK_MEASUREMENT" or
            manifest.get("metadata_authenticated") is not False or
            manifest.get("runtime_verifier_implemented") is not False or
            manifest.get("per_basic_block_identity_and_hashing") is not False or
            manifest.get("adversarial_tamper_protection_proven") is not False or
            manifest.get("iphone_device_executed_for_k16") is not False or
            manifest.get("arm64e_pac_tested") is not False or
            manifest.get("crane_production_modified") is not False):
        raise AssertionError("K17 K16 manifest scope improperly upgraded")
    return raw


def claims(manifest: bytes, signed_bytes: bytes, fp: str) -> dict:
    return {
        "schema": 1,
        "scope": SCOPE,
        "algorithm": "Ed25519",
        "domain": DOMAIN[:-1].decode("ascii"),
        "signature_file": SIGNATURE_FILE,
        "payload_file": k16.MANIFEST,
        "payload_sha256": digest(manifest),
        "signed_message_sha256": digest(signed_bytes),
        "signature_sha256": None,  # actual verified below, not signed receipt itself
        "trusted_external_ed25519_spki_sha256": fp,
        "k16_offline_manifest_replayed": True,
        "signed_reference_key_supplied_separately": True,
        "offline_signature_checked": True,
        "code_signature_or_device_attestation": False,
        "k15_bbcheck_fixed": False,
        "runtime_verifier_implemented": False,
        "on_device_integrity_proven": False,
        "per_basic_block_integrity_proven": False,
        "anti_tamper_strength_proven": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
    }


def outside(reference: Path, path: Path, label: str) -> None:
    if path.resolve().is_relative_to(reference.resolve()):
        raise AssertionError("K17 " + label + " must be supplied outside artifact directory")


def verified(out: Path, public: Path, expected: str) -> dict:
    outside(out, public, "trusted public key")
    key, fp = load_trusted(public, expected)
    manifest = replay_manifest(out)
    signed = DOMAIN + manifest
    sig_file = out / SIGNATURE_FILE
    receipt_file = out / RECEIPT_FILE
    if (not sig_file.is_file() or sig_file.is_symlink() or
            not receipt_file.is_file() or receipt_file.is_symlink()):
        raise AssertionError("K17 missing original detached signature or receipt")
    sig = sig_file.read_bytes()
    if len(sig) != 64:
        raise AssertionError("K17 Ed25519 signature must be exactly 64 bytes")
    try:
        key.verify(sig, signed)
    except InvalidSignature as exc:
        raise AssertionError("K17 Ed25519 signature invalid for raw K16 manifest") from exc
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    expect = claims(manifest, signed, fp)
    expect["signature_sha256"] = digest(sig)
    if type(receipt) is not dict or receipt != expect:
        raise AssertionError("K17 signature receipt not reproducible from trusted key + file bytes")
    print("K17_INDEPENDENT_EXTERNAL_TRUST_ANCHOR_ED25519_OFFLINE_REPLAY_PASS: "
          "signature + raw Mach-O K16 source matches, no runtime/PAC/Crane")
    return expect


def sign(out: Path, private: Path, public: Path, expected: str) -> dict:
    outside(out, public, "trusted public key")
    outside(out, private, "private signing key")
    outside(HERE.parents[2], private, "private signing key from repository")
    key, fp = load_trusted(public, expected)
    if not private.is_file() or private.is_symlink():
        raise AssertionError("K17 private signing key must be an external regular file")
    # fail CLOSED before reading private material when signature output already exists.
    if (out / SIGNATURE_FILE).exists() or (out / RECEIPT_FILE).exists():
        raise AssertionError("K17 refuses to overwrite detached signature/receipt")
    raw_key = private.read_bytes()
    try:
        signing_key = serialization.load_pem_private_key(raw_key, password=None)
    except (TypeError, ValueError) as exc:
        raise AssertionError("K17 invalid unencrypted Ed25519 external private key") from exc
    if not isinstance(signing_key, ed25519.Ed25519PrivateKey):
        raise AssertionError("K17 private signing key must be Ed25519")
    if not hmac.compare_digest(spki_der(signing_key.public_key()), spki_der(key)):
        raise AssertionError("K17 signer private key does not match pre-approved trusted public key")
    manifest = replay_manifest(out)
    signed = DOMAIN + manifest
    sig = signing_key.sign(signed)
    receipt = claims(manifest, signed, fp)
    receipt["signature_sha256"] = digest(sig)
    (out / SIGNATURE_FILE).write_bytes(sig)
    (out / RECEIPT_FILE).write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    # Mandatory independent round-trip with the independent public key.
    verified(out, public, expected)
    print("K17_OFFLINE_DETACHED_SIGNED_REFERENCE_CREATED: external trust root required; "
          "no private key included in artifact")
    return receipt


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("sign", "verify"))
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--trusted-public-key", required=True, type=Path)
    p.add_argument("--expected-spki-sha256", required=True)
    p.add_argument("--private-key", type=Path)
    a = p.parse_args()
    if a.mode == "sign":
        if a.private_key is None:
            p.error("sign requires --private-key supplied outside the artifact")
        sign(a.out, a.private_key, a.trusted_public_key, a.expected_spki_sha256)
    else:
        if a.private_key is not None:
            p.error("verification must not accept any private key")
        verified(a.out, a.trusted_public_key, a.expected_spki_sha256)


if __name__ == "__main__":
    main()
