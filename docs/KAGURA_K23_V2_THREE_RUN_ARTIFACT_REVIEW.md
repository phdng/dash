# K23 v2 — xác minh artifact thực và ba lượt iPhone do người dùng báo PASS

Ngày ghi nhận: **26/10/2026**. Đây là mốc nghiệm thu **chức năng
bundled K14 reference verification**, không phải self-integrity.

## 1. Đối chiếu ZIP/IPA K23 v2 tải lên

Artifact: `DuoDash-Kagura-K23-IOS-RUNTIME-REFERENCE-LAB-EXPERIMENTAL (3).zip`.
Đã đọc ZIP người dùng tải lên và kiểm **65 tên duy nhất, CRC toàn bộ
hợp lệ**, tệp IPA thực cùng báo cáo và nguồn Swift sinh tại CI.

| Mục | Kết quả từ byte thực |
|---|---|
| ZIP SHA-256 | `7fbea5d7d52dec575011143dea7cacecbdbacc985ce63aedc29e83d2ecd16cf1` |
| ZIP entries | 65, CRC PASS |
| IPA SHA-256 | `c92c030048162f3a1c4182688045af301346aeb78cafca45d4b79fd0fac1452b` |
| IPA entries | 3: executable, Info.plist, reference Base64 |
| K23 app executable SHA-256 | `5e6fee5912451552279464731894f67c05d5a3eb7e1e441851c2017a0d158abe` |
| Info.plist | `CFBundleVersion=2`, Bundle ID độc lập K23 |
| Transport bytes | 123313, ASCII header + Base64 canonical |
| Transport SHA-256 | `060497b06ad64f5d38525251a5051535dc8616e4f151d9c79cfccf117386e907` |
| Decoded K14 Mach-O bytes | 92456, byte-identical K14 executable cùng artifact |
| Decoded K14 SHA-256 | `584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7` |
| K14 UUID | `7c0cb853-77aa-3ccb-9f20-560e5f40e587` |
| Thin arm64 Mach-O | MH_EXECUTE, 22 load commands, tổng 2976 byte |
| K14 `_dd_k14_ios_parity` | offset 21588, 484 byte; SHA `10b05c44f7e87b150a453fe7dc7c64b2fd00ff672c0f747c709650d4271f1e0a` |
| K14 `_dd_k8_evaluate` | offset 22072, 544 byte; SHA `81cba0a6201a018c0b48198aa3331ba0a265e45e3c12206b62ea9a5bec98ba97` |

Hai code-interval hashes tính lại trực tiếp từ executable K14 decode,
không tin riêng vào dòng PASS trong report. Các digest, offset, length,
UUID và reference size trong `K23Expected.swift` khớp report và IPA.
Ba entry của IPA byte-identical với các app resource trong artifact ZIP.

## 2. Ba lượt chạy thiết bị

Người dùng thông báo đã thực hiện cả **ba lượt test** theo hướng dẫn
và cả ba trả **cùng chuỗi 10 dòng PASS**:
- `DD_K23_SCHEMA=1`
- `DD_K23_CONTEXT=IOS_DEVICE_USER_INITIATED`
- `DD_K23_SCOPE=BUNDLED_REFERENCE_ONLY`
- `DD_K23_REFERENCE_UUID=7c0cb853-77aa-3ccb-9f20-560e5f40e587`
- `DD_K23_REFERENCE_SHA256=PASS`
- `DD_K23_CODE_INTERVALS=2`
- `DD_K23_MUTATED_CODE=REJECTED`
- `DD_K23_TRUNCATED_REFERENCE=REJECTED`
- `DD_K23_SELF_INTEGRITY=NOT_IMPLEMENTED`
- `DD_K23_COMPLETE=PASS`

**Chấp nhận nghiệm thu chức năng theo lời báo cáo người dùng: 3/3
lượt PASS, mỗi lượt cùng mẫu 10/10 dòng.** Các log không có mã thời
gian/nonce; việc giống nhau giữa các lượt là đúng như thiết kế khi
mẫu tham chiếu cố định. Nó không chứng minh ba lần thực hiện độc lập.

**Chưa đạt cổng strict device_qa.py:** ZIP chỉ có build logs, IPA và
report; không có `01-fresh.txt`, `02-relaunch.txt`,
`03-reinstall.txt` từ ứng dụng thiết bị. Người dùng chỉ dán **một
chuỗi 10 dòng** và khẳng định cả 3 lần giống nhau. Vì vậy không tạo
ba file log giả từ một chuỗi để ép cổng QA PASS, không in artifact
`K23-QA-REVIEW.json` như thể đã đối chiếu ba file thật.

## 3. Ranh giới bằng chứng và bước tiếp

- ZIP v2 và nguồn build: **PASS kiểm chứng offline**.
- Người dùng báo iPhone K23 v2 fresh/relaunch/reinstall:
  **3/3 chức năng PASS (user-reported)**.
- Đối chiếu 3 log file gốc do thiết bị chia sẻ + script:
  **PENDING_SOURCE_LOG_FILES**, không phải FAIL chức năng.
- Cryptographic device attestation, running-app self-integrity,
  anti-tamper, arm64e/PAC, Crane production:
  **NOT_IMPLEMENTED/NOT_PROVEN**.

Có thể dừng vòng QA chức năng K23 tại đây. Nếu cần nâng cấp cấp độ
chứng cứ có thể dùng `docs/KAGURA_K23_IPHONE_QA_RUNBOOK.md` để xuất
**ba file log gốc** và chạy `device_qa.py` cùng artifact v2, nhưng
**không cần lặp lại thử nghiệm chỉ để thêm chuỗi PASS giống nhau**.

Mốc tiếp theo (chưa triển khai): threat model và trust root độc lập
cho verifier mã đang thực thi; không được coi Base64/hash nhúng trong
cùng unsigned IPA là chống can thiệp, không bật BBCheck K15 weak
always-pass hoặc tự ý đưa vào Crane production.
