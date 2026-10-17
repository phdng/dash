# DuoDash K8 — kiểm chứng artifact LLVM19 thật (17/10/2026)

Đầu vào: tệp ZIP nguyên bản người dùng gửi,
`DuoDash-Kagura-K8-FIVE-ISOLATED-PASSES-LLVM19-EXPERIMENTAL.zip`.

- ZIP SHA-256:
  `a1bc3b5bf0057e082ff4109c93925e39758f7fd861fb336d3655ffe4c6049dea`.
- 74 entry; `zipfile.ZipFile.testzip()`: **không lỗi CRC**.
- Báo cáo `Kagura-K8-PASS-REPORT.json`: schema 1, năm mục
  `ibr,mvo,genc,fsplit,ci`, upstream Kagura SHA pin
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`.
- Đã đọc byte thật trong ZIP, **không chỉ tin JSON**: 92 phép đối chiếu
  độc lập gồm class pass, verifier trace, host/iOS IR delta,
  host/iOS object delta và SHA báo cáo, iOS Mach-O header,
  log 4.096 vector và dấu vết cấu trúc. **92/92 PASS**.
- Các hash `fixture.c`, `runner.c`, `mvo.ll` mà CI ghi trong
  báo cáo **khớp SHA-256 tính lại từ đúng source hiện tại của workspace**:
  - `fixture.c`: `39e0b833ab8574bf2e8abb2a66dc440d06424a82d6a0f371297e313bc91992fc`
  - `runner.c`: `4c1929802af256c6a7130e8f010e26f517f887a5b8dcbaad53434c6eb5bc2d6e`
  - `mvo.ll`: `abbe02b364571b77fb94fff673111bf381f694211cca148d18a73650a8343e50`

## Kết quả 5 pass chạy tách biệt trên macOS

| Pass | Native LLVM pass trace | IR/object thay đổi | 4.096 native vector | iOS arm64 |
|---|---|---|---|---|
| `ibr` | `kagura::IndirectBranchPass` | Có private global `__kagura_fptr_*` | `25a3318e3d7d6525` | `MH_OBJECT` build-only |
| `mvo` | `kagura::MemoryValueObfuscationPass` | XOR tại cả store `%mixed.mvo` và load `%value.mvo` | `64e61045bbc4a250` | `MH_OBJECT` build-only |
| `genc` | `kagura::GlobalEncryptionPass` | Có decrypt `.dec` | `25a3318e3d7d6525` | `MH_OBJECT` build-only |
| `fsplit` | `kagura::FunctionSplitPass` | Tạo **5** hàm `__kg_dd_k8_evaluate_bb*` | `25a3318e3d7d6525` | `MH_OBJECT` build-only |
| `ci` | `kagura::CallIndirectionPass` | Có `__kagura_thunk_table`, `kagura_init_thunk_table` và runtime resolver | `25a3318e3d7d6525` | `MH_OBJECT` build-only |

Cả năm `native.log` **giống từng byte** với file baseline phù hợp;
`DD_K8_SCHEMA=1`, `DD_K8_VECTORS=4096`,
`DD_K8_COMPLETE=PASS`. MVO có baseline riêng
`mvo-plain-native.log`, *không* dùng baseline từ `fixture.c`;
checksum `64e61045bbc4a250` còn khớp oracle Python độc lập
`mvo_expected_checksum()`. Dấu vết LLVM IR thật chứng minh lỗi
MVO no-op/Clang frontend trước đó đã được giải quyết trong fixture
IR thử nghiệm này. Việc MACOS native PASS không tự động chứng minh
tính đúng cho Objective-C/Crane hoặc mọi trường hợp biên.

Tất cả object iOS đã được giải mã Mach-O header độc lập:
`0xfeedfacf` / CPU `0x0100000c` / CPU subtype `0` /
filetype `MH_OBJECT (1)`; baseline cũng được kiểm.
**Không có app IPA, chạy runtime iOS, PAC arm64e hoặc device pass
trong artifact K8 này.**

## Kết luận và ranh giới

**K8 ISOLATED FIVE PASS LLVM19 macOS native: VERIFIED_FROM_USER_CI_ARTIFACT**.
Đây là **năm pass riêng**, không phải một pipeline kết hợp, và không
đồng nghĩa với toàn bộ Kagura/SLLVM proprietary pass inventory.
`ci` chỉ được kiểm trên external libc call canary; không thử hooks,
PAC pointer, ObjC selector, Substrate hoặc dylib Crane.
Không có thời gian benchmark K8 và không xác nhận security strength.

K9 **đã có macOS LLVM19 artifact riêng**, xác minh 179/179
phép kiểm độc lập: [KAGURA_K9_ARTIFACT_REVIEW.md](KAGURA_K9_ARTIFACT_REVIEW.md)
ghép hai fixture K8 vào một module, có IR/object delta và hai oracle
native sau mỗi pass trong một thứ tự chọn trước.
**K8 isolated và K9 composed là hai bằng chứng riêng**.
Chỉ sau khi kiểm tra pipeline phối hợp với gates IR/object/parity
tương tự mới xét pipeline chung; còn iOS runtime cần IPA lab mới, log
checksum/build UUID, trên thiết bị dự phòng. K5/K7 và Crane production
không thay đổi.
