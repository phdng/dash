# K16 — đo SHA-256 của Mach-O sau linker (offline, không chạy BBCheck)

Ngày triển khai: **18/10/2026**. Trạng thái:
**STAGED_MANUAL_OFFLINE_POST_LINK_MACHO_TEXT_NOT_MACOS_VERIFIED**.

[K15 artifact review](KAGURA_K15_ARTIFACT_REVIEW.md) xác định nguồn Kagura
pinned có `runtime/core/bb_check.c` là **weak always-passing stub**,
bỏ qua `block_id` và `expected`, trả `1` bất kể code bị thay đổi.
**KHÔNG** dùng BBCheck gốc để tuyên bố code integrity/anti-tamper;
không gọi hoặc thay thế `kagura_on_tamper_detected`.

## Mục đích hẹp của K16

Thử nghiệm khả năng thu được **byte máy đã qua linker** từ Mach-O
`arm64 subtype0 MH_EXECUTE` và tạo dữ liệu tham chiếu *offline*.
Đây là bài toán khác hoàn toàn với pass K15/BBCheck:

- K15 cho thấy *LLVM-IR opcode expected checksum* không được runtime
  kiểm chứng trên machine code.
- K16 chỉ đo **file bytes** của section `__TEXT,__text` từ Mach-O đã
  link: `file offset`, `size`, SHA-256, UUID và SHA-256 cả binary.
- Dùng các specimen an toàn **đã có bằng chứng trước đó**:
  `macos-baseline`, `macos-cse-break` native K13 và executable
  `KaguraCSEBreakLab.app/KaguraCSEBreakLab` iOS arm64 K14.
  Đảm bảo hai executable macOS khác SHA code thực và iOS binary
  trùng SHA/LC_UUID với báo cáo K14, không dựng file giả làm proof.
- **Không chạy** pass BBCheck, không lập bản đồ từng basic block,
  không lấy hash lúc runtime, không cài app, không link bất kỳ
  provider weak nào của BBCheck, không đổi Crane production.

## Workflow manual

`.github/workflows/kagura-k16-offline-macho-text.yml`:

**Kagura K16 - Offline Mach-O Text Section Feasibility (Experimental)**.

1. Portable fail-closed test K16/K15/K14/K13, registry/matrix audit.
2. Trên runner macOS-14, pin upstream Kagura commit
   `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`, source registry SHA
   `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`.
3. Build LLVM19 plugin riêng; chạy lại K13 `pilot.py`/`audit.py`
   với checksum native 4096-vector đúng oracle `25a3318e3d7d6525`;
   chạy K14 `build_ipa.sh`, xác minh actual protected iOS object,
   app binary SHA/UUID và IPA unsigned trước khi đo.
4. `scripts/custom_ollvm/kagura_k16/macho_measure.py` đọc raw Mach-O:
   yêu cầu `MH_MAGIC_64`, `CPU_TYPE_ARM64`, subtype0,
   `MH_EXECUTE`; parser chặn corrupt load commands, duplicate UUID
   hoặc `__TEXT,__text`, section tràn file / vùng command / segment,
   sai mapping file offset/vmaddr. Băm SHA-256 code section **sau linker**.
5. Lưu `Kagura-K16-OFFLINE-TEXT-MANIFEST.json` với hash cả binary,
   hash code section, offset/size, UUID, hash report K13/K14 và
   cờ **runtime_verifier_implemented=false**. Replay từ file gốc
   phải hoàn toàn trùng manifest. Test portable thay byte code hoặc
   trường manifest phải FAIL.

Artifact, kể cả lúc lỗi:
`DuoDash-Kagura-K16-OFFLINE-MACHO-TEXT-FEASIBILITY-EXPERIMENTAL`.

## Điều K16 tuyệt đối không chứng minh

**Manifest không được ký và không có trust anchor.** Nếu đối thủ
sửa được cả binary và manifest, họ có thể tạo lại SHA khớp.
Vì thế đây chỉ là **file-byte comparison offline**, không phải
bảo vệ chống giả mạo, self-integrity, code signing hoặc bảo vệ
chống reverse. ASLR, code-signing, relocation, dyld fixups và
quyền W^X cần thiết kế riêng nếu một ngày đo in-memory, không
dùng offset file làm địa chỉ runtime.

K16 cũng **không chứng minh integrity per-basic-block**:
parser đo nguyên section `__TEXT,__text`, không cung cấp unique
block IDs, boundaries, provenance và runtime fail policy. Để
phát triển thực tế tiếp theo cần secure manifest/authenticated
reference, cách đo in-memory hợp lệ theo ABI/pointer-auth/code-signing,
đánh giá hash đo và dữ liệu được đo cùng một trust boundary,
đánh giá overhead và thử nghiệm isolated có rollback.
Không sử dụng hiện vật K16 để tuyên bố BBCheck đã được sửa.

**Mọi trạng thái hiện tại:** chưa có real macOS K16 workflow artifact;
K11–K14 giữ bằng chứng riêng, K15 runtime weak stub chưa được
sửa; K16 iPhone, arm64e/PAC, Crane production và bảo vệ security
đều **NOT_TESTED/NOT_IMPLEMENTED**.
