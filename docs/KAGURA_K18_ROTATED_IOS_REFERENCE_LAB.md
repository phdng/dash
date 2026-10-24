# K18 — iOS CryptoKit Ed25519 lab: xác minh K14 specimen read-only

Ngày triển khai mã: **20/10/2026**. Theo yêu cầu **24/10/2026**, trạng thái:
**SKIPPED_BY_USER_NO_MACOS_OR_DEVICE_VERIFICATION**.
K18 được bỏ qua trên đường triển khai K19. Đây là **skip**, không phải
CI/IPA/iPhone PASS. Mã K18 vẫn giữ nguyên để xem lại sau khi cần.

**K17 đã có CI artifact thực và 446/446 phép kiểm tra raw PASS**;
IPA K14 được người dùng báo cài/chạy bình thường. Nhưng private
key TEST K17 từng được chia sẻ trong chat; **không được reuse** khóa
này để chứng minh secure trust. BBCheck gốc K15 là weak stub luôn
return 1; K18 không sử dụng hoặc sửa BBCheck.

## Phạm vi thực tế

K18 biên dịch một **IPA thử nghiệm RIÊNG** bằng Swift/Swift CryptoKit
cho iOS arm64 15+. Nó chạy on-device **nếu cài được IPA**, nhưng chỉ
xác minh một **file mẫu K14 Mach-O được đóng trong bundle để đọc-only**.
Nó KHÔNG kiểm tra executable K18 đang chạy, KHÔNG đo vùng code in-memory,
không xác thực Apple code-signing và không chạy pass BBCheck.

Quy trình xác minh khi bấm *Verify bundled K14 reference*:
1. Đọc Ed25519 **public raw 32 bytes** và fingerprint SPKI
   SHA-256 từ `KaguraK18Trust.plist` trong chính IPA.
   Kiểm tra fingerprint và từ chối fingerprint TEST K17 đã công khai
   `2e91a1403ffc97eb66c2c1717205eb054ce3c341898b6978b007cb5c56241f40`.
2. Dùng **CryptoKit `Curve25519.Signing.PublicKey`** xác minh
   detached Ed25519 64 bytes trên đúng
   `b"DuoDash/K17/K16/MachOTextOfflineEd25519/v1\\0" + raw K16 manifest`.
3. Kiểm phạm vi manifest K16, trong đó `metadata_authenticated=false`,
   `runtime_verifier_implemented=false`, anti-tamper=false và
   `BLOCKED_K15_WEAK_ALWAYS_PASS_STUB`; không cho manifest tự
   quảng bá security PASS.
4. Đọc file mẫu `KaguraCSEBreakLab.reference` (Mach-O executable
   của K14 **đã link sẵn**, không chạy file này trong app K18);
   hash SHA-256 toàn file; parse real Mach-O `LC_UUID`,
   `LC_SEGMENT_64`, section `__TEXT,__text` và tính SHA-256
   code vùng file; đối chiếu offset/size/UUID/SHA với reference
   đã ký. Không thay thế bằng JSON `PASS`.
5. Nếu TẤT CẢ pass, app in đúng log text để chia sẻ;
   nếu bất kỳ điều kiện nào fail thì chỉ in `COMPLETE=FAIL`.

10 dòng log trên thiết bị khi bấm nút thành công:

```text
DD_K18_SCHEMA=1
DD_K18_CONTEXT=IOS_DEVICE_USER_INITIATED
DD_K18_SCOPE=BUNDLED_REFERENCE_ONLY
DD_K18_ARCH=arm64:0x00000000
DD_K18_REFERENCE_UUID=<LC_UUID of archived K14>
DD_K18_TRUST_SPKI_SHA256=<approved new public-key DER SPKI SHA256>
DD_K18_SIGNATURE=PASS
DD_K18_REFERENCE_MACHO_TEXT=PASS
DD_K18_SELF_INTEGRITY=NOT_IMPLEMENTED
DD_K18_COMPLETE=PASS
```

Các dòng trên là **văn bản do app tự báo**, chưa phải remote
attestation. `scripts/custom_ollvm/kagura_k18/device_log_audit.py`
đối chiếu **đúng 10 dòng** theo thứ tự với
`Kagura-K18-IPA-REPORT.json` và fingerprint phê duyệt qua kênh
độc lập, từ chối UUID, fingerprint, checksum trạng thái hay scope
bị thay, hoặc log thêm dòng; kết quả vẫn ghi
`on_device_execution_cryptographically_attested=false`.
Ví dụ sau khi có log thiết bị thực:

```sh
python scripts/custom_ollvm/kagura_k18/device_log_audit.py \\
  --device-log /path/to/k18-device-log.txt \\
  --k18-report /path/to/Kagura-K18-IPA-REPORT.json \\
  --approved-spki-sha256 <fingerprint-da-phê-duyệt-ngoài-artifact>
```

Không tự tạo log giả hay coi văn bản khớp là chứng thực thiết bị.

## Khóa K18 MỚI — khác khóa K17 TEST

Cần 3 giá trị GitHub Actions mới, **tạo trên máy do người dùng kiểm soát
ngoài chat**. Không gửi/commit private PEM:
- Repository Secret `K18_ED25519_PRIVATE_KEY_PEM`
- Repository Secret hoặc Variable `K18_ED25519_PUBLIC_KEY_PEM`
- Repository Secret hoặc Variable
  `K18_ED25519_PUBLIC_KEY_SPKI_SHA256`

Phải lưu fingerprint phê duyệt **ngoài GitHub artifact và chat**;
cặp private/public phải thực sự khớp. Workflow K18 fail-closed
nếu thiếu, trùng fingerprint TEST K17 cũ, hoặc Secret/Variable xung
đột. CI không sinh khóa mới tự phong trust. Có thể dùng lệnh OpenSSL
và Python DER-SPKI SHA-256 đã hướng dẫn ở
[K17](KAGURA_K17_ED25519_OFFLINE_REFERENCE.md), nhưng tạo khóa
**mới** riêng K18.

Lưu ý quan trọng: key được nhúng dưới dạng **public** trong IPA chỉ
là tiện ích chức năng. Nếu đối thủ có thể repack IPA/thay code và key,
họ có thể khiến ứng dụng của họ báo PASS. **Không có immutability,
Apple attestation, out-of-app trust-root hoặc anti-repackaging được
chứng minh**. Chủ sở hữu cần so fingerprint từ log + manifest
đối chiếu với fingerprint đã phê duyệt độc lập.

## Workflow thủ công và artifact

`.github/workflows/kagura-k18-rotated-reference-ipa.yml`

Tên: `Kagura K18 - Rotated Ed25519 iOS Reference Verifier Lab (Experimental)`

- Môi trường `macos-14` với LLVM19, Swift, CryptoKit và
  `cryptography==50.0.2`.
- Portable K18/K17/K16/K15/K14/K13 gates, custom matrix/audit.
- Rebuild đúng Kagura pinned commit
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`,
  registry SHA
  `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`.
- Rebuild K13 macOS 4096 native parity và iOS object, K14 IPA
  độc lập, K16 raw Mach-O manifest. Ký manifest bằng khóa mới,
  K17 verify offline trước khi đóng app K18.
- Swift compile **chỉ app K18 mới**, bundle ID
  `com.duodash.research.kagurak18referencelab`; K14 executable
  được chứa như **data resource**, không ghép code K14/Crane/K11
  vào executable K18.
- Script `scripts/custom_ollvm/kagura_k18/package.py` verify
  Ed25519/manifest/public key, SHA/UUID/section Mach-O và
  IPA ZIP CRC/permission/6 tệp hợp lệ, xuất
  `KaguraK18ReferenceLab-TrollStore-arm64.ipa` (unsigned),
  `Kagura-K18-IPA-REPORT.json`. K18 không có code-signing
  tự động, không cài app từ CI.
- Artifact ngay cả khi lỗi:
  `DuoDash-Kagura-K18-ROTATED-ED25519-IOS-REFERENCE-IPA-EXPERIMENTAL`.
  Private key chỉ ở `RUNNER_TEMP` **ngoài artifact** và
  bị xóa trên nhánh thành công; runner ephemeral được dọn sau job.

## Verification và giới hạn

Trên Windows Workspace, `scripts/test_kagura_k18_reference_lab.py`
dùng **khóa Ed25519 tạm chỉ để fixture tests**, fake Mach-O
có byte thật, negative tests cho sai chữ ký/binary/bundle/fingerprint.
**K18 Swift chưa thể biên dịch thực ở Windows**. Chỉ GitHub macOS
build artifact mới xác nhận iOS cross-compile/IPA packaging;
sau đó chỉ log người dùng gửi từ thiết bị mới cung cấp device
functional evidence, **không phải cryptographic device attestation**.

K18 không can thiệp iOS PAC/arm64e, Crane production, K5/K7, K11–K17.
Không đưa BBCheck weak always-pass stub vào production.
