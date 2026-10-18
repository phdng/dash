# K15 — Đối chiếu ZIP thật, runtime BBCheck có weak always-pass stub

Ngày kiểm tra: 18/10/2026. Trạng thái: **MACOS_IOS_PROVIDER_ARTIFACT_VERIFIED_WEAK_ALWAYS_PASS_STUB_NOT_NATIVE_OR_SECURITY_PASS**.

Báo cáo nguồn từ ZIP GitHub Actions K15 thật do người dùng tải lên. Đối chiếu trực tiếp SHA-256, dữ liệu LLVM IR, Mach-O LC_SYMTAB/nlist và 22 source C upstream archive; KHÔNG suy luận hiệu lực bảo mật từ báo cáo PASS.

## Provenance ZIP và pass

- ZIP: DuoDash-Kagura-K15-BBCHECK-RUNTIME-PROVIDER-RESEARCH-EXPERIMENTAL.zip.
- SHA-256 ZIP: 1f19d3d9eb58a87a9798d11082f3eaf4652e70987100084eb2c292d543bbd336.
- **231 entries**, không có trùng tên, CRC32 hợp lệ, không encrypted/path traversal/symlink.
- **2.609/2.609 điều kiện file-backed PASS** trên ZIP thật, bao gồm hash file nguồn, nm log và object Mach-O, không phải native hoặc security PASS.
- Git commit upstream theo report: ac2136ee0408677cf7cdee55307e9b16edd5f4d5.
- SHA nguyên bytes pinned-registry.def: 6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa; khớp K12–K14.
- Pass: kagura-bbcheck, kind FN, enable flag BBCheck, class kagura::BasicBlockChecksumPass; pipeline function(kagura-bbcheck),verify.
- Trên macOS arm64 và iOS arm64 subtype 0: normalized LLVM IR và Mach-O object đều có delta; object import cả hai symbol runtime thật.

## Runtime C provider — duy nhất trên cả 2 target

| Required undefined symbol | Provider C từ đúng upstream pin |
| --- | --- |
| _kagura_bb_check | runtime/core/bb_check.c |
| _kagura_on_tamper_detected | runtime/core/tamper_response.c |

Có **22/22 candidate source C compile thành công trên macOS và 22/22 trên iOS arm64**. Hai provider duy nhất được chọn có ZERO transitive Kagura unresolved dependencies; các file khác có thể phát sinh dependency và không được tự động link. Object iOS provider có imports hệ thống _abort và _sleep ở nhánh tamper.

- SHA source bb_check.c: 2a87f559f2427c2de5217502c4d62abb1165fba34f5e1702982785dfacb24345.
- SHA source tamper_response.c: 976cea2786438241b88f84c5c745f59aa669b683037ba81d7c09690339df5377.
- **Hai external definition trong Mach-O LC_SYMTAB đều mang n_desc=0x0080 (N_WEAK_DEF)** trên macOS và iOS arm64: _kagura_bb_check và _kagura_on_tamper_detected. Đây là proof từ nlist thật, không chỉ nm output text.

## Phát hiện chặn triển khai — Không có integrity enforcement

**runtime/core/bb_check.c là weak stub luôn trả về 1.** Nó bỏ qua block_id và expected, rồi return 1. Chính comment nguồn gọi đây là ALWAYS-PASSING STUB. Nguồn giải thích expected là hash LLVM IR opcode trước codegen, không thể tính lại từ machine code runtime; block_id lại bắt đầu từ 1 ở mỗi function nên không định danh duy nhất.

Theo IR pass: nonzero là block hợp lệ; zero mới gọi kagura_on_tamper_detected(). Với provider gốc luôn trả 1, **không có kiểm tra thực sự mã machine-code bị sửa đổi**. Không được quảng bá là anti-tamper/integrity verified hoặc native security PASS.

runtime/core/tamper_response.c định nghĩa weak kagura_on_tamper_detected() mặc định gọi abort() trên macOS/iOS; strong noreturn kagura_tamper_detected() có fallback sleep()/abort() nếu hook trả về. K15 **chỉ biên dịch object**, không chạy callback. Weak definition có thể bị thay trong link khác, nhưng không có bằng chứng app đã override nó.

## Giới hạn và quyết định

- Được kiểm tra độc lập: artifact, raw source, LLVM IR/object delta, 22 providers candidates mỗi target, unique exported definitions và zero Kagura transitive unresolved trong hai provider được chọn.
- **Chưa chạy** native 4096 parity BBCheck, chưa có IPA K15, chưa có iPhone BBCheck, arm64e/PAC, Crane production hoặc chứng thực thiết bị.
- **Không nâng K15 thành Native/iPhone/Security PASS. Không bật BBCheck production.** Trước K16 cần thiết kế integrity metadata cho post-codegen machine code, có unique block identifiers, review tamper fail policy và thử nghiệm isolated có rollback. Không chấp nhận giả hash, đổi luôn-return stub thành cơ chế giả, tắt tamper callback hoặc tự merge vào Crane.

Bản review JSON độc lập: Kagura-K15-BBCheck-Runtime-Artifact-Review.json.
