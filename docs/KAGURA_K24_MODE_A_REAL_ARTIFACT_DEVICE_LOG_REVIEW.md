# K24 Mode A — artifact macOS đối chiếu báo cáo runtime iPhone

Ngày ghi nhận: **26/10/2026**. Nguồn: ZIP người dùng cung cấp
`DuoDash-Kagura-K24-OWN-TEXT-EXTERNAL-SIGNATURE-LAB-EXPERIMENTAL.zip`.

## Kiểm chứng offline từ các byte thực

- ZIP **95.166 bytes**, SHA-256
  `5fd433a6c21defee780f65f25e21fe6d3593a44c7591c879f8314e53d9dc21d3`.
  **9/9 entries duy nhất, CRC toàn bộ PASS**.
- Unsigned IPA `KaguraK24SelfTextLab-TrollStore-arm64.ipa`,
  **45.644 bytes**, SHA-256
  `006a1d3ce1a61394f9e5f03e2c8a5f5e3d10c6a0b9eaf8f419a4cc070fbc5cd0`.
  Hai app entries: main executable và Info.plist, CRC PASS.
- Mach-O main executable **189.312 bytes**, SHA-256
  `79a4b05cdbc06a2a7aa6b2c471f909903b4d833859556b8a74bbdc5edaeb9e26`.
  Parse trực tiếp load commands: thin arm64 subtype 0,
  `MH_EXECUTE`, **40 load commands**, `LC_UUID`
  `825856f9-f710-38bd-a434-aaa983adbc5b`.
- Vùng `__TEXT,__text` **file offset 32768**, **45880 bytes**.
  SHA-256 tính lại trực tiếp từ byte executable:
  `5471f918a4fad5c7360c7f423d2ed8639c1a329b4a61a40eaaff63c017298b5b`.
  UUID/size/SHA đều trùng K24 report JSON và unsigned signing
  request của chính artifact; executable SHA và IPA SHA khớp report.
- `CFBundleIdentifier=com.duodash.research.kagurak24selftextlab`,
  `CFBundleVersion=1`, minimum iOS 15.
- `K24KeyConfig.json`: `public_key_b64=""`,
  `external_signature_gate_configured=false`.
  `K24Pinned.swift`: `keyConfigured = false`,
  `publicKey = []`. Không có private key hay chữ ký từ CI.

## Báo cáo iPhone từ người dùng

Người dùng chia sẻ trực tiếp một log K24 8 dòng có
`DD_K24_COMPLETE=MEASUREMENT_ONLY` với UUID, 45880 bytes và SHA-256
khớp **chính xác** với số đo post-link từ executable trong ZIP.
`DD_K24_EXTERNAL_KEY=NOT_CONFIGURED` và
`DD_K24_EXTERNAL_SIGNATURE=NOT_IMPORTED` phù hợp với config
tìm thấy trong ZIP.

**Kết luận chứng cứ:** K24 Mode A **user-reported runtime measurement
correlated with real post-linked executable artifact**. Đây là xác
nhận chức năng có liên hệ file thực; không phải cryptographic device
attestation. Chỉ có log người dùng dán trong hội thoại, chưa phải tệp
log gốc riêng để chạy tool `device_log_audit.py`.

**Không được nâng thành security PASS:** không có Ed25519 public key
trong app hiện tại, không có statement đã ký, không có kiểm soát
kẻ tấn công sửa cả executable/verifier, không có immutable hardware
trust anchor, anti-tamper, arm64e/PAC hay Crane production.

## Mốc triển khai tiếp theo

**K24 Mode B, cùng ứng dụng nghiên cứu, bản build mới:**
1. Tạo cặp Ed25519 ở máy tin cậy, **private PEM ngoài repo/CI**.
2. Đưa **chỉ raw public B64** vào GitHub repository Actions variable
   `K24_TRUSTED_ED25519_PUBLIC_KEY_B64`, lấy trước fingerprint
   SHA-256 SPKI ở nơi khác.
3. Dispatch GitHub workflow K24 với mode **require key** và nhập
   independently approved SPKI fingerprint; CI fail-closed khi thiếu
   key/fingerprint/không trùng. **Phải build IPA mới**: bản Mode A này
   không thể import JSON mà được PASS.
4. Sau build, đối chiếu IPA/request/report, dùng external_sign.py
   ngoài repository ký statement post-link, import JSON từ Files trên
   iPhone, yêu cầu `DD_K24_COMPLETE=PASS_LAB_ONLY`.
5. Thu full log và artifact mới; thử input sai chữ ký/khác build,
   luôn FAIL. Không đổi Crane production.

Hướng dẫn chi tiết:
`docs/KAGURA_K24_SELF_TEXT_EXTERNAL_SIGNATURE_LAB.md`.
