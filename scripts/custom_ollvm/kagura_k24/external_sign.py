#!/usr/bin/env python3
"""K24 detached Ed25519 signature. PRIVATE KEY NEVER IN REPO OR CI.

Externally pre-approved Ed25519 SPKI SHA256 pins the public key. Sign
the exact post-linked K24 __TEXT,__text measurement, never a bundled K14
specimen. The app imports the signed JSON envelope from Files. Public
key bundled in a repackageable app is NOT a tamper-proof trust root.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import sys
import zipfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import package as k24


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def outside(root: Path, p: Path, purpose: str) -> None:
    if p.resolve().is_relative_to(root.resolve()):
        raise AssertionError("K24 " + purpose + " must be kept outside " + str(root))


def trusted(pem: Path, expected: str) -> ed25519.Ed25519PublicKey:
    if not k24.HEX64.fullmatch(expected):
        raise AssertionError("K24 requires separately known SPKI SHA256")
    if not pem.is_file() or pem.is_symlink():
        raise AssertionError("K24 trusted public PEM absent/unsafe")
    src = pem.read_bytes()
    if not (64 <= len(src) <= 4096):
        raise AssertionError("K24 trusted PEM size invalid")
    try:
        pub = serialization.load_pem_public_key(src)
    except (ValueError, TypeError) as exc:
        raise AssertionError("K24 failed to parse trusted public PEM") from exc
    if not isinstance(pub, ed25519.Ed25519PublicKey):
        raise AssertionError("K24 only permits Ed25519")
    der = pub.public_bytes(encoding=serialization.Encoding.DER,
                           format=serialization.PublicFormat.SubjectPublicKeyInfo)
    if not hmac.compare_digest(sha(der), expected):
        raise AssertionError("K24 trusted SPKI fingerprint does not match independent approval")
    return pub


def replay(out: Path) -> tuple[bytes, dict]:
    report, canonical = k24.collect(out)
    if not report["public_key_pinned_into_compiled_app"]:
        raise AssertionError("K24 unsigned measurement-only build: no trusted public key")
    requestp = out / k24.REQUEST
    reportp = out / k24.REPORT
    ipap = out / k24.IPA
    if any(not p.is_file() or p.is_symlink() for p in (requestp, reportp, ipap)):
        raise AssertionError("K24 needs original IPA/report/request")
    saved = json.loads(requestp.read_text(encoding="utf-8"))
    if requestp.read_bytes() != canonical:
        raise AssertionError("K24 signing request drifted from actual executable")
    claims = json.loads(reportp.read_text(encoding="utf-8"))
    if (claims != report | {
        "ipa_sha256": sha(ipap.read_bytes()),
        "signing_request_sha256": sha(canonical)
    }):
        raise AssertionError("K24 signing report not replayable")
    with zipfile.ZipFile(ipap) as z:
        if (len(z.infolist()) != 2 or
            {m.filename for m in z.infolist()} !=
            {k24.PREFIX + k24.APP, k24.PREFIX + "Info.plist"} or
            z.testzip() is not None or
            any(m.flag_bits & 1 for m in z.infolist()) or
            z.read(k24.PREFIX + k24.APP) !=
            (out / (k24.APP + ".app") / k24.APP).read_bytes() or
            z.read(k24.PREFIX + "Info.plist") !=
            (out / (k24.APP + ".app") / "Info.plist").read_bytes()):
            raise AssertionError("K24 mismatched unsigned IPA executable/plist")
    payload = base64.b64decode(saved["payload_b64"], validate=True)
    expected = k24.payload({
        "uuid": report["app_executable_uuid"],
        "text_size": report["self_text_size"],
        "text_sha256": report["self_text_sha256"]
    })
    if payload != expected or saved["expected_text_sha256"] != report["self_text_sha256"]:
        raise AssertionError("K24 signed payload source incorrect")
    return payload, report


def envelope(payload: bytes, sig: bytes) -> bytes:
    if len(sig) != 64:
        raise AssertionError("K24 Ed25519 signature must be 64 bytes")
    return (json.dumps({
        "payload_b64": base64.b64encode(payload).decode("ascii"),
        "signature_b64": base64.b64encode(sig).decode("ascii"),
    }, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def verify(artifact: Path, source: Path, public: Path, fingerprint: str) -> dict:
    outside(artifact, source, "envelope")
    outside(artifact, public, "trusted PEM")
    pub = trusted(public, fingerprint)
    payload, report = replay(artifact)
    cfg = json.loads((artifact / k24.KEY_CONFIG).read_text(encoding="utf-8"))
    pinned = k24.public_key(cfg["public_key_b64"])
    expected_raw = pub.public_bytes(encoding=serialization.Encoding.Raw,
                                    format=serialization.PublicFormat.Raw)
    if not hmac.compare_digest(pinned, expected_raw):
        raise AssertionError("K24 running app public key is not externally trusted one")
    raw = source.read_bytes()
    if not (source.is_file() and not source.is_symlink() and 160 <= len(raw) <= 4096):
        raise AssertionError("K24 external envelope invalid size/source")
    try:
        obj = json.loads(raw.decode("ascii"))
        if type(obj) is not dict or set(obj) != {"payload_b64", "signature_b64"}:
            raise AssertionError("K24 external envelope wrong fields")
        data = base64.b64decode(obj["payload_b64"], validate=True)
        sig = base64.b64decode(obj["signature_b64"], validate=True)
    except (ValueError, UnicodeDecodeError, KeyError, TypeError) as exc:
        raise AssertionError("K24 cannot decode external envelope") from exc
    if raw != envelope(data, sig) or data != payload:
        raise AssertionError("K24 envelope bytes differ from measured signed payload")
    try:
        pub.verify(sig, k24.DOMAIN + payload)
    except InvalidSignature as exc:
        raise AssertionError("K24 Ed25519 signature mismatch") from exc
    tampered = bytearray(payload)
    tampered[-2] ^= 1
    try:
        pub.verify(sig, k24.DOMAIN + tampered)
    except InvalidSignature:
        pass
    else:
        raise AssertionError("K24 signature accepted changed payload")
    return {
        "schema": 1, "scope": "K24_USER_SUPPLIED_OFFLINE_SIGNATURE_VERIFICATION_NOT_DEVICE",
        "trusted_external_spki_sha256": fingerprint,
        "measured_app_uuid": report["app_executable_uuid"],
        "signed_payload_sha256": sha(payload),
        "signature_sha256": sha(sig),
        "external_signature_valid_offline": True,
        "runtime_self_security_proven": False,
        "device_runtime_verified": False,
        "immutable_on_device_root_proven": False,
        "arm64e_pac_proven": False,
        "crane_production_modified": False,
    }


def sign(artifact: Path, private: Path, public: Path, fingerprint: str, output: Path) -> dict:
    repo = HERE.parents[2]
    for p, label in ((private, "PRIVATE KEY"), (public, "trusted PEM"),
                     (output, "envelope")):
        outside(repo, p, label)
        outside(artifact, p, label)
    if output.exists() or output.is_symlink():
        raise AssertionError("K24 external envelope output already exists")
    pub = trusted(public, fingerprint)
    payload, report = replay(artifact)
    expected_raw = pub.public_bytes(encoding=serialization.Encoding.Raw,
                                    format=serialization.PublicFormat.Raw)
    cfg = json.loads((artifact / k24.KEY_CONFIG).read_text(encoding="utf-8"))
    if not hmac.compare_digest(k24.public_key(cfg["public_key_b64"]), expected_raw):
        raise AssertionError("K24 compiled public key differs from externally approved PEM")
    if not private.is_file() or private.is_symlink():
        raise AssertionError("K24 external Ed25519 private key missing")
    try:
        sk = serialization.load_pem_private_key(private.read_bytes(), password=None)
    except (ValueError, TypeError) as exc:
        raise AssertionError("K24 invalid external private key format") from exc
    if not isinstance(sk, ed25519.Ed25519PrivateKey):
        raise AssertionError("K24 expected Ed25519 private key")
    if not hmac.compare_digest(sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    ), expected_raw):
        raise AssertionError("K24 external private key does not match trusted PEM")
    sig = sk.sign(k24.DOMAIN + payload)
    output.write_bytes(envelope(payload, sig))
    result = verify(artifact, output, public, fingerprint)
    print("K24_EXTERNAL_ED25519_SIGN_PASS: user-held private key, no app security claims")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("sign", "verify"))
    p.add_argument("--artifact-dir", type=Path, required=True)
    p.add_argument("--trusted-public-key", type=Path, required=True)
    p.add_argument("--expected-spki-sha256", required=True)
    p.add_argument("--private-key", type=Path)
    p.add_argument("--envelope", type=Path, required=True)
    o = p.parse_args()
    if o.mode == "sign":
        if o.private_key is None:
            p.error("sign requires --private-key outside repo and artifacts")
        sign(o.artifact_dir, o.private_key, o.trusted_public_key,
             o.expected_spki_sha256, o.envelope)
    else:
        if o.private_key is not None:
            p.error("verification cannot accept private key")
        verify(o.artifact_dir, o.envelope, o.trusted_public_key, o.expected_spki_sha256)
        print("K24_EXTERNAL_ED25519_OFFLINE_VERIFY_PASS: no iPhone attestation")


if __name__ == "__main__":
    main()
