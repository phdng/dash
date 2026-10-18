# K16 — kiểm chứng ZIP thật: Mach-O post-link `__TEXT,__text` offline

Ngày đối chiếu: **18/10/2026**. Trạng thái:
**REAL_MACOS_OFFLINE_TEXT_ARTIFACT_REPLAY_VERIFIED_NOT_RUNTIME_SECURITY**.

Đây là kiểm tra từ ZIP K16 GitHub Actions **thật** do người dùng cung cấp,
không phải fixture synthetic. Đã đọc trực tiếp byte Mach-O arm64 từ ZIP
và IPA nhúng, thực hiện SHA-256 độc lập của section `__TEXT,__text`,
`LC_UUID`, toàn bộ executable, raw source report, LLVM IR/object và
log native. **Đo được code sau linker không chứng minh cơ chế bảo vệ runtime.**

## Artifact gốc

- ZIP: `DuoDash-Kagura-K16-OFFLINE-MACHO-TEXT-FEASIBILITY-EXPERIMENTAL.zip`.
- SHA-256: `521934d99ce952f74b0471cdd259d92e147eee718479a3863b49251b11eb79c4`.
- **54 thành phần tên duy nhất**, CRC sạch, không encrypted,
  traversal hay symlink.
- **276/276 phép kiểm tra file-backed độc lập PASS** trên dữ liệu
  gốc: từ outer ZIP, Mach-O/section code, file và IR/object K13,
  log K13 native, báo cáo/IPA K14 đến nguồn tài liệu K15.
  Đây là chỉ số kiểm tra bằng chứng, **không phải số kiểm thử security**.

| Executable Mach-O arm64 subtype 0 `MH_EXECUTE` | `__TEXT,__text` file offset | Số byte code | SHA-256 `__TEXT,__text` |
| --- | ---: | ---: | --- |
| `macos-baseline` | 15376 | 728 | `9682fe57b5dc2e115f25745becc03f9eaa68f56e06f15d72f79a8c2630cef5f9` |
| `macos-cse-break` | 15264 | 840 | `2c8fd2006a6d636fb30c088585a9b093108b825c6032915aa1987abd0ee85186` |
| `KaguraCSEBreakLab.app/KaguraCSEBreakLab` | 16384 | 6312 | `dd41ee5339eb6fd2732e46f34b9a22ea62233611a4a6269b4088251a6824fd3e` |

Các offset, size và digest trên được tính lại từ **raw load command
`LC_SEGMENT_64` và `section_64`**, trùng manifest K16, không chỉ
đọc từ JSON. Hai vùng code macOS baseline/CSEBreak có
**size/hash khác nhau thật**. Mỗi Mach-O có đúng một `LC_UUID` và
một `__TEXT,__text` tại địa chỉ file hợp lệ.

SHA-256 executable:
- macOS baseline: `88458349074925e15cb7098e295267ef77f9d71f187c64d6bad38d529a72aafb`
- macOS CSEBreak: `c4a9cb9d36fc4bfc0bc3fdca8cce3c96b24026554c680034aad9bd189060f42f`
- iOS K14 CSEBreak: `584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7`

## Đối chiếu bằng chứng K13/K14 và log người dùng

Manifest K16 tham chiếu các báo cáo K13/K14 với SHA-256 thực và tất cả
đều khớp file thô từ ZIP:
- K13 report: `41dcc508a7b484022655b33f2e5819928bea1c66c0a3b5fa981ffd45d0e6ca55`.
- K14 IPA report: `1a02b0aebb4a789e023ba4d147839bf01398aaf084baf0d59b13e2d2d0d590d3`.
- K14 evidence: `eaacbc76d2f619b47d0b051fca99abb5d6f1c88845470fd8948f360f7db975d2`.
- K15 weak-stub review tài liệu **trong Workspace**:
  `7575757feea78e124049fa3ec8621e64a39fd941e3d64322b539b3f6d05dcd32`,
  trùng manifest.

Trace LLVM19 của K13 trong ZIP xác nhận
`kagura::CSEBreakPass` và `VerifierPass` thực trên canary.
Raw `.bc`, `.ll` và `.o` khớp SHA của report;
trừ dòng `ModuleID` của llvm-dis, IR CSEBreak có normalized SHA
khác baseline và xuất hiện các lệnh `cse.mask`,
`cse.break`, `cse.unmask` chỉ trong bản protected.
Hai log native macOS của K13 đều ghi đúng **4096 vector**,
checksum `25a3318e3d7d6525`, `DD_K8_COMPLETE=PASS`.

K14 IPA unsigned bên trong ZIP có SHA:
`8733e2f93001b6d1195581deea013688825a94aa1d4d29bbfb23814dd5f9716f`;
CRC ZIP lồng sạch, đúng hai file `Info.plist` + executable,
binary bên trong IPA trùng **byte-for-byte** với executable K14
K16 đã đo. `LC_UUID` executable là:
`7c0cb853-77aa-3ccb-9f20-560e5f40e587`.

**Log 8 dòng K14 được người dùng chia sẻ lại trong cùng lượt này**
có UUID đúng bằng `LC_UUID`, schema K14, `CSE_BREAK`, 4096 vector,
checksum `25a3318e3d7d6525`, COMPLETE=PASS.
Đây là **văn bản K14 tương quan đúng với IPA**; không phải log
K16 độc lập, không chứng minh K16 chạy trên thiết bị và không phải
device attestation.

## Giới hạn bắt buộc

- K16 đã xác minh **offline SHA-256 và ranh giới `__TEXT,__text`
  trên các Mach-O sau linker** từ CI macOS thực.
- **Manifest không ký và không có trust anchor**. Ai kiểm soát
  cả executable lẫn manifest đều có thể tính lại hash; do đó không
  thể tuyên bố phát hiện sửa đổi có chủ đích trước đối thủ.
- Chưa tạo per-basic-block ID/digest, chưa có runtime verifier,
  chưa đo in-memory dưới ASLR/dyld/code-signing và chưa có
  K16 iPhone execution.
- **BBCheck K15 vẫn bị chặn**: provider weak always-return-1
  không kiểm tra code integrity. K16 đo vùng code của K13/K14,
  **không sửa BBCheck hoặc thực thi callback tamper**.
- Không thử arm64e/PAC, Objective-C hooks và không thay đổi
  Crane production hay kết quả K11–K14 trước đó.

Bản JSON review độc lập được tạo cho người dùng:
`Kagura-K16-Uploaded-Artifact-Review.json`.
