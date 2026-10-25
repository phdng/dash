# Kagura K20 — đối chiếu artifact Mach-O macOS thực

Ngày ghi nhận: **25/10/2026**. Trạng thái: **REAL_MACOS_OFFLINE_FUNCTION_STARTS_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY**.

## Nguồn bằng chứng

Artifact người dùng cung cấp: `DuoDash-Kagura-K20-FUNCTION-STARTS-DUAL-SOURCE-OFFLINE-EXPERIMENTAL.zip`.

SHA-256 ZIP: `235e1d4ea16437807d1920e236bb65942ef580bf021734d9093a81e73884b214`.

Phiên kiểm tra trước ghi nhận **56 mục tên duy nhất, CRC sạch** và **190/190 phép đối chiếu file-backed PASS** (157 phép đối chiếu cấu trúc/load commands/ULEB128/nlist/UUID/hash + 33 phép đối chiếu bổ sung của IPA, K13 source/IR/object và log native). Các số kiểm tra là số lượng *assertions trên artifact*, không phải số lượng kiểm thử bảo mật hay chứng cứ attestation. Bản ZIP không được nhập vào Git repo này; các số liệu lưu ở đây là bản ghi của lần đối chiếu artifact người dùng chia sẻ, không đại diện cho một lần build/replay lại bằng máy Windows hiện tại.

| Mach-O liên kết | Số LC_FUNCTION_STARTS | Target và kích thước interval nlist |
| --- | ---: | --- |
| macOS baseline K13 | 3 | `_dd_k8_evaluate`: 460 byte |
| macOS CSEBreak K13 | 3 | `_dd_k8_evaluate`: 544 byte |
| iOS standalone K14 | 30 | `_dd_k14_ios_parity`: 484 byte; `_dd_k8_evaluate`: 544 byte |

Các đầu và cuối của **4 interval nlist** đều được đối chiếu với `LC_FUNCTION_STARTS` giải mã ULEB128 trên Mach-O thật. Dữ liệu raw/executable/section SHA-256, UUID, SHA-256 LC_FUNCTION_STARTS và báo cáo K19/K20 được đối chiếu; native macOS K13 có 4.096 vector và cùng checksum `25a3318e3d7d6525` ở baseline/protected. IPA K14 vẫn unsigned và executable đóng gói khớp byte đầu vào.

## Ý nghĩa và giới hạn

- Đây là **real macOS post-link offline artifact review**. Không có bằng chứng K20 tự chạy trên iPhone, không có bằng chứng thực thi verifier trong bộ nhớ, không đo per-basic-block.
- Hai metadata `LC_FUNCTION_STARTS` và `LC_SYMTAB` đều thuộc *cùng executable*, không tạo hai trust anchors độc lập, không chứng minh kích thước thật của hàm.
- SHA-256 trong manifest không ký có thể được tạo lại cùng executable đã thay đổi: **không xác thực chống sửa đổi có chủ đích**.
- Không có run ID/console log GitHub Actions đầy đủ trong ZIP. Thành công ở đây là **xác minh bytes của artifact**, không phải xác nhận trực tiếp trạng thái job UI.
- K18 được **SKIPPED_BY_USER_NO_MACOS_OR_DEVICE_VERIFICATION**; K15 BBCheck weak-stub blocked. Không thay đổi Crane production, arm64e/PAC hoặc thiết bị.
- K21 là một thử nghiệm mới về thống kê bit pattern AArch64 trên cùng intervals: không suy ra instruction semantics, CFG hoặc chức năng bảo mật.

Tham khảo: [KAGURA_K20_FUNCTION_STARTS_CROSSCHECK.md](KAGURA_K20_FUNCTION_STARTS_CROSSCHECK.md).
