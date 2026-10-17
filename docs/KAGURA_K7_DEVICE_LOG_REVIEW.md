# Kagura K7 — Real iPhone device log review

Date: **2026-10-17**. Earlier user-pasted K7 text had damaged fields and a missing timing sample; this review retains that as a rejected transport sample, **but supersedes the unresolved device-text status** based on the new user-uploaded **unaltered `a.txt`**.

## New unmodified attachment accepted

- Attachment: `a.txt`, **809 bytes**, SHA-256
  `355ecf8be195c9c925ce8d56fe1b78dd63f9e1dc2aa7f543d67d4bfbfefbc763`.
  9 parity lines, exactly one blank separator, 14 performance lines,
  ASCII/LF, final newline; no truncated or duplicate fields.
- `DD_VM_IOS_SCHEMA=1`, `DD_VM_IOS_CONTEXT=IOS_DEVICE`,
  `DD_VM_IOS_ARCH=arm64:0x00000000`;
  `DD_VM_IOS_PIPELINE=KAGURA_VM_SELECTIVE`;
  `DD_VM_IOS_VECTORS_PASS=4096`, `DD_VM_IOS_COMPLETE=PASS`.
- `DD_VM_IOS_APP_UUID` and `DD_VM_IOS_PERF_APP_UUID` are **identical**:
  `15a45d46-f0da-37ff-855d-5e6ea078be8e` (digit zero). This matches
  the single LC_UUID in the *actual* K7 uploaded arm64 MH_EXECUTE,
  `KaguraVMLab-IPA-report.json` and
  `Kagura-K7-IPA-EVIDENCE.json` from the matching exact ZIP.
- Independently recomputed **4096 known-answer vectors** from public
  `vm_canary.c` arithmetic and `oracle.py`; exact parity checksum
  `9625f13d712f59c3` and guard checksum `09d9d53ddf189ce7`
  match both 16-digit device-text fields and expected CI evidence.
  Guard was not virtualized by the compiler (K7 IR proof remains valid).
- Confirmed the original CI artifact (25,808-byte ZIP, clean CRC), embedded
  unsigned arm64 IPA, real executable SHA-256 and one genuine LC_UUID
  against its two JSON reports; no values were invented to repair this text.
  IPA SHA-256:
  `ab5a6d21bd676e06585e95f61f9295207c55679a89502d8f2198df6dc605f6e5`.
  Executable SHA-256:
  `03d5aa93901cb03b5ffe7f8c3e754ee4bd21b13bb353bfb832d75e43bb40904d`.

## Real iPhone log performance (user-shared observational measurements)

Both sections declare `IOS_DEVICE`, `arm64:0x00000000` and identical
UUID. The log declares exactly **3 pairs × 1024 calls per variant**;
all six timing entries are present, integers greater than 0, and the
note is `OBSERVATIONAL_NOT_SECURITY_ATTESTATION` with benchmark PASS.

| Pair | Plain, ns/call | Kagura VM, ns/call | Paired VM / plain |
| --- | ---: | ---: | ---: |
| 0 | 46 | 3742 | 81.347826× |
| 1 | 32 | 1918 | 59.9375× |
| 2 | 30 | 2145 | 71.5× |

**Median of paired ratios = 71.5×**, not ratio of marginal medians.
Marginal medians are 32 ns/call plain and 2145 ns/call VM
(`2145/32 = 67.03125`), a different statistic. The paired-ratio median
is the correct comparison for these alternating groups. Only three
short benchmark pairs: no stable population estimate, device-to-device
generalization, distribution p95, thermal/cold-start claim, or security
strength inference. It confirms **substantial overhead** on this one
public pure-C K7 fixture; never enable it for hot Crane functions.

## Prior paste versus uploaded file

Prior pasted copy in chat contained `foda` (letter o), truncated pipeline,
parity and guard checksums, a split call count, truncated performance
note and an empty `PROTECTED_NS_2`. That paste remains
`REJECTED_MALFORMED_TRANSPORT_TEXT`. The new **original text file** fixes
every one of these problems without inference or normalization.

## Recorded outcome

- `K7 USER_SHARED_TEXT_PARITY_AND_PERF_VALIDATED_NOT_ATTESTED`.
- `K7 VALIDATED_EXACT_SCHEMA_UUID_CHECKSUM_VS_CI`.
- `K7 USER_SHARED_THREE_PAIRS_OBSERVATIONAL`.
- **CI artifact integrity:** SHA/UUID/compiler VM evidence verified.
- **Text integrity:** user-shared device text is internally consistent
  and claimed executable UUID matches exact K7 CI IPA; this **is not
  cryptographic proof** that it executed on the user's actual device.
- **Production:** Kagura VM stays disabled for Crane; K5/K7 known-good
  IPA binaries untouched; no arm64e/PAC runtime test.

Original parser:
`scripts/custom_ollvm/kagura_vm/ios_device_log_audit.py`.
The parser's paired-ratio fields and tests preserve observational
interpretation. Relevant CI evidence:
[K7 artifact review](KAGURA_K7_ARTIFACT_REVIEW.md).
