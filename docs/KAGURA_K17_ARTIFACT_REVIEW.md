# K17 — kiểm chứng ZIP thực, Ed25519 TEST và K16 offline source replay

Ngày kiểm tra: **20/10/2026**. Trạng thái:
**REAL_CI_ED25519_TEST_KEY_SIGNATURE_AND_OFFLINE_MACHO_VERIFIED_NOT_SECURE_TRUST**.

Người dùng báo workflow K17 build xanh và ứng dụng có thể cài đặt,
hoạt động bình thường trên thiết bị. Đã kiểm tra **ZIP K17 thật được
người dùng cung cấp**, không dựa duy nhất vào báo cáo CI hoặc chữ
`PASS`. **Không có log thiết bị K17 được ký hay device attestation.**

## Kết quả bằng chứng thực tế

- ZIP: `DuoDash-Kagura-K17-EXTERNALLY-TRUSTED-ED25519-OFFLINE-EXPERIMENTAL.zip`
- ZIP SHA-256: `9b07e6a8e285102aa80671a6bdd70fe080d9424097632a7e87272f44b77d76db`
- **56 tệp**, tên duy nhất, CRC32 đều hợp lệ, không encrypted,
  traversal, symbolic link.
- **446/446 phép kiểm tra độc lập PASS** trên byte gốc: ZIP,
  Ed25519 detached chữ ký thật, reproducible receipt, K16 raw manifest,
  `LC_UUID`/`LC_SEGMENT_64`/`__TEXT,__text` của ba executable,
  K13 pinned source/bitcode/LLVM IR/object/pass manager/native log
  và IPA K14 nhúng trong ZIP.

### Chữ ký Ed25519

- Detached `Kagura-K17-K16-MANIFEST.ed25519`: đúng **64 bytes**.
- SHA-256 chữ ký: `8e82eef77b726f5412fff4a0e750fc4554915748ef44bbd97aa7be437637c892`.
- SHA-256 nguyên byte `Kagura-K16-OFFLINE-TEXT-MANIFEST.json`:
  `eb322412014ede1f4b5e0aa093e513b067670ac9866b33f1511c62269cfc1cd8`.
- Chữ ký có xác minh **PASS** trên message:
  `b"DuoDash/K17/K16/MachOTextOfflineEd25519/v1\\0" + raw_manifest_bytes`.
- Public key Ed25519 được dùng để xác minh là **khóa TEST đã
  được chia sẻ trong cuộc trò chuyện trước** (được cung cấp ngoài
  artifact); SHA-256 DER SPKI:
  `2e91a1403ffc97eb66c2c1717205eb054ce3c341898b6978b007cb5c56241f40`.
- JSON `Kagura-K17-SIGNATURE-RECEIPT.json` được tính lại chính xác,
  không chỉ dựa vào `offline_signature_checked=true` trong JSON.
- Không có file PEM chứa private key trong ZIP đã kiểm tra.

**Giới hạn bảo mật nghiêm ngặt:** private key TEST của bộ này từng
được hiển thị công khai trong chat trước đó; vì vậy **chữ ký hợp lệ
không chứng minh secret được bảo vệ hoặc ai là người ký**.
Kết quả chỉ chứng minh đúng tính toán Ed25519 và tính nhất quán
các byte artifact. Không được tuyên bố `secure independent trust anchor`.
Nếu chuyển sang sản xuất, phải **tạo cặp Ed25519 mới trong thiết bị/
môi trường tin cậy ngoài chat**, phê duyệt fingerprint trước qua
kênh riêng và thu hồi/rotate bộ TEST cũ.

### Ba Mach-O executable và IPA thật

| Executable | `__TEXT,__text` bytes | SHA-256 code |
| --- | ---: | --- |
| macOS baseline K13 | 728 | `9682fe57b5dc2e115f25745becc03f9eaa68f56e06f15d72f79a8c2630cef5f9` |
| macOS CSEBreak K13 | 840 | `2c8fd2006a6d636fb30c088585a9b093108b825c6032915aa1987abd0ee85186` |
| iOS arm64 CSEBreak K14 | 6312 | `dd41ee5339eb6fd2732e46f34b9a22ea62233611a4a6269b4088251a6824fd3e` |

Ba `MH_EXECUTE` là thin ARM64 subtype0, file offset/size/
`LC_UUID`/SHA `__TEXT,__text` đúng manifest K16. Hai executable
macOS khác mã máy thật. Binary IPA iOS là byte-for-byte cùng executable
đã đo. Mach-O iOS thực có defined external:
`_main`, `_dd_k14_ios_parity`, `_dd_k8_evaluate`.

- UUID iOS: `7c0cb853-77aa-3ccb-9f20-560e5f40e587`.
- SHA-256 binary: `584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7`.
- SHA-256 IPA unsigned:
  `8733e2f93001b6d1195581deea013688825a94aa1d4d29bbfb23814dd5f9716f`.
- K13 CSEBreakPass LLVM19 source commit pin
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`,
  registry SHA
  `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`.
  IR normalized và object thực đổi trên cả hai target;
  trace pass thật, 4096 native macOS vectors baseline/protected
  cùng checksum `25a3318e3d7d6525`.
- K15 weak-stub document SHA trong workspace trùng hash
  nguồn ghi trong manifest K16:
  `7575757feea78e124049fa3ec8621e64a39fd941e3d64322b539b3f6d05dcd32`.

## Giới hạn K17 và trạng thái thiết bị

**Đã xác minh:** file-backed Ed25519 TEST-key signature khớp manifest
raw và dữ liệu Mach-O thật; CI artifact chứa IPA arm64.
**Theo báo cáo người dùng:** app cài và hoạt động bình thường.

**Chưa được chứng thực độc lập:** K17 có runtime verifier chạy trên
iPhone, device attestation, code signing/Apple trust, per-basic-block
integrity, arm64e PAC, chống kẻ tấn công biết private TEST key.
K17 là bước **ký tham chiếu OFFLINE**, không sửa runtime IPA K14.

**K15 BBCheck vẫn bị chặn:** `runtime/core/bb_check.c`
weak stub luôn return `1`, không kiểm tra integrity thực.
Không tích hợp Crane production, không bật PAC/BBCheck.

Báo cáo JSON độc lập:
`Kagura-K17-Uploaded-Artifact-Review.json`.
