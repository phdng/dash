# K21 — đo opcode-word pattern AArch64 từ Mach-O đã kiểm chứng K20 (offline)

Ngày đưa mã vào workspace: **25/10/2026**.
Trạng thái sau review ZIP thực: **REAL_MACOS_OFFLINE_AARCH64_WORD_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY**.
SHA-256 artifact `1991f38f5af55f310352e0f23d6e2a566eec8dba5d0a35ee6c8c2d91fffe40aa`; **57 entries, 785/785 kiểm tra file-backed PASS**. Chi tiết:
[KAGURA_K21_ARTIFACT_REVIEW.md](KAGURA_K21_ARTIFACT_REVIEW.md).

## Mục tiêu

K20 đã đối chiếu 4 *khoảng địa chỉ symbol* K19 với danh sách `LC_FUNCTION_STARTS` thực trên Mach-O macOS/iOS; K20 artifact review: 56 entries và 190/190 checks PASS. K21 tiến thêm đúng **một phép đo byte tĩnh**: đọc từng word little-endian 32 bit trong bốn interval đã được K20 replay và thống kê một số *mẫu bit opcode* của ISA AArch64.

Không xác định số lượng CFG edges, destination thực, basic-block ID, kích thước hàm đúng, entropy/độ khó reverse, hoặc cơ chế bảo mật. Nếu interval nlist chứa padding hoặc code khác thì tất cả word vẫn được đếm; thống kê không phải disassembler và không tự chứng minh các word đều là instruction có thể thực thi.

## Mã và cổng fail-closed

- `scripts/custom_ollvm/kagura_k21/opcode_inventory.py` gọi `k20.verify(out)`; chuỗi này replay nguồn K19/K16 và K13/K14. Không dùng JSON PASS thay byte executable.
- Yêu cầu file Mach-O thật có SHA nguyên file trùng K20. Với mỗi symbol target: `file_offset`, `length`, SHA-256 byte phải khớp vùng đã đối chiếu K20; kiểm tra 4-byte-aligned, giới hạn interval tối đa 8 MiB.
- Thống kê 10 nhóm *encoding patterns* (không decode operands): `bl_imm`, `b_imm`, `b_cond`, `cbz_cbnz`, `tbz_tbnz`, `ret_reg`, `br_reg`, `blr_reg`, `nop`, `other`. `other` không có nghĩa là invalid.
- Ghi SHA vùng bytes, số word, word đầu/cuối, histogram và metadata liên kết K20 vào `Kagura-K21-STATIC-OPCODE-INVENTORY.json`. Bản ghi **unsigned**, không ghi đè; `--verify` tính lại từ nguồn và từ chối khác biệt.
- Baseline `_dd_k8_evaluate` và CSEBreak `_dd_k8_evaluate` phải có **SHA code khác nhau**, nhưng histogram *có thể trùng nhau*. Histogram không được diễn giải là chứng cứ bảo vệ tốt hơn.
- Test portable `scripts/test_kagura_k21_opcode_inventory.py`: tất cả 10 encoding groups, range hỏng, thay byte Mach-O, thay đổi JSON, claim bảo mật giả và điều kiện workflow.

## Workflow GitHub Actions

`.github/workflows/kagura-k21-static-opcodes.yml` có tên
**Kagura K21 - Static AArch64 Word Inventory Offline (Experimental)**.

- Chạy **workflow_dispatch** thủ công trên `macos-14`, LLVM19 và upstream Kagura pinned giống K13–K20.
- Build K13 native parity, K14 standalone IPA, đo và replay K16/K19/K20, sau đó ghi và replay K21.
- Bằng chứng khi chạy thật: artifact `DuoDash-Kagura-K21-STATIC-OPCODE-INVENTORY-OFFLINE-EXPERIMENTAL` (upload kể cả lỗi).
- Artifact K21 thực đã được người dùng cung cấp và review byte-backed; 57 entries, 785/785 checks. Đánh dấu **verified macOS artifact OFFLINE**; chưa có iPhone K21/runtime integrity/CFG/PAC/Crane security. K22 được tách riêng làm cổng tái lập hai build; K22 hiện NOT_TESTED.

## Ranh giới an toàn

K18 **SKIPPED_BY_USER**, không yêu cầu khóa của K18. Không gọi runtime BBCheck K15 (weak always-pass). Không ký IPA, không chạy thiết bị iPhone, không thay Makefile production/Crane, không PAC/arm64e và không có trust anchor. Đo lường K21 chỉ có ý nghĩa *offline research* đối với các executable đã liên kết, không phải anti-tamper/anti-reversing production.

Tài liệu liên quan: [KAGURA_K20_ARTIFACT_REVIEW.md](KAGURA_K20_ARTIFACT_REVIEW.md), [KAGURA_K20_FUNCTION_STARTS_CROSSCHECK.md](KAGURA_K20_FUNCTION_STARTS_CROSSCHECK.md).
