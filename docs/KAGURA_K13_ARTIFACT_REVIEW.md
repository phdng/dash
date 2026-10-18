# DuoDash K13 — đối chiếu artifact thực CSEBreak Native + iOS arm64

Ngày kiểm tra: **18/10/2026**.

**Trạng thái: MACOS_NATIVE_AND_IOS_OBJECT_ARTIFACT_VERIFIED_NO_DEVICE.**
Nguồn là ZIP K13 thực do người dùng tải lên. Đã đọc trực tiếp bytes
Mach-O `LC_SYMTAB`, LLVM IR, bitcode, log native và SHA file; không
suy diễn từ chữ PASS trong tên file ZIP hoặc chỉ từ report JSON.

## ZIP và nguồn compiler

- ZIP: `DuoDash-Kagura-K13-CSEBREAK-NATIVE-IOS-ARM64-OBJECT-EXPERIMENTAL.zip`
- SHA-256: `2f18e54d3cc6f421ab997d96a162fd6b5869a4f5c78e62f739943e2238ce64f3`.
- **41 entry**, không trùng, CRC32 sạch, không traversal/mã hóa.
- **422/422 phép đối chiếu file-backed PASS** bằng trình đọc ZIP/IR
  và parser Mach-O `LC_SYMTAB` độc lập, bao gồm hash của object
  và chứng cứ log runner thực được CI lưu.
- Commit Kagura theo CI: `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`.
  File `pinned-registry.def` thật trong ZIP có SHA-256
  `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`
  trùng artifact K12, định nghĩa đúng **FN `CSEBreak`**.
  `pinned-LICENSE` SHA
  `daf2c2bd9b6b162d9d9e3eb5b265594c2af6b8f009a627772fb0c7636144aa53`.
- Fixture C `scripts/custom_ollvm/kagura_k8/fixture.c` SHA
  `39e0b833ab8574bf2e8abb2a66dc440d06424a82d6a0f371297e313bc91992fc`
  và native runner C `runner.c` SHA
  `4c1929802af256c6a7130e8f010e26f517f887a5b8dcbaad53434c6eb5bc2d6e`
  đã được tái băm **từ workspace DuoDash thực**, đều khớp báo cáo.

## Pass LLVM19 và IR/object thực

Hai trace macOS/iOS chứa:

```text
Running pass: kagura::CSEBreakPass on dd_k8_evaluate (73 instructions)
Running pass: kagura::CSEBreakPass on dd_k8_internal (6 instructions)
Running pass: VerifierPass on [module]
Running pass: BitcodeWriterPass on [module]
```

- Pipeline `function(kagura-cse-break),verify` cho đúng một pass
  (`kagura::CSEBreakPass`). Cả hai `.ll` đầu ra thêm các lệnh
  `%cse.mask`, `%cse.break` và `%cse.unmask` thực so với IR gốc,
  không chỉ khác `ModuleID`. SHA normalized IR trước/sau khác nhau.
- Clang19 tạo Mach-O `MH_OBJECT` **ARM64 subtype0** ở cả macOS
  và iOS; SHA object thay đổi sau pass.
- Kiểm tra **trực tiếp nlist trong Mach-O** xác nhận definition
  external `_dd_k8_evaluate` và symbol internal `_dd_k8_internal`.
  Bên iOS, undefined symbol thực từ nlist là **`_strlen`**
  (framework/system runtime), **không có `_kagura_*`**;
  log `xcrun nm -gU` và `nm -u -j` khớp symbol table thật.

| Target | Object baseline SHA-256 | Object protected SHA-256 |
| --- | --- | --- |
| macOS arm64 | `d8e1a34f8696d039c6133657eb10969f481c89bf0070dcb9870925a2e4fa09a5` | `02caa3bc92b5a927463229d0de9854f3422b6ce24d90741175a4ad040464e839` |
| iOS arm64 | `43b263d0d1eb5b8194dd944e86e1c49ce57061f6ec283dd39f654f67a0c2ec71` | `a1dea3f6cdb66d4f62d40dcfa7d32608049082700b2c78f7f69854c6b864cc62` |

## Native macOS 4096-vector parity

Trong ZIP có **hai executable Mach-O arm64 `MH_EXECUTE` thật**,
có external `_main` và `_dd_k8_evaluate` trong nlist.
CI native stdout lưu hai log độc lập:

```text
DD_K8_SCHEMA=1
DD_K8_VECTORS=4096
DD_K8_CHECKSUM=25a3318e3d7d6525
DD_K8_COMPLETE=PASS
```

Cả baseline và protected có **cùng checksum**
`25a3318e3d7d6525` sau 4.096 vector mỗi biến thể, đáp ứng
điều kiện parity native của K13. Khớp hash file/report/runner
chứ không chỉ so hai chuỗi log. **Đã xác minh tính nhất quán của
bằng chứng CI native**, nhưng máy kiểm tra hiện tại không chạy lại
executable macOS từ ZIP; đây không phải chứng thực thiết bị độc lập.

## Ranh giới

- iOS chỉ là **arm64 subtype0 MH_OBJECT build-only**: chưa link app,
  chưa có IPA K13, chưa chạy trên iPhone.
- Không có kiểm chứng **arm64e/PAC**, Objective-C hooks, Crane
  production, benchmark hiệu năng, hoặc sức mạnh anti-reverse.
- CI tự khai pinned git commit; ZIP lưu registry và LICENSE thật với
  SHA đối chiếu, nhưng không có chứng thực mật mã riêng cho provenance
  toàn bộ checkout GitHub.
- Đây là bằng chứng cho **một pass `CSEBreakPass` riêng lẻ**;
  không chứng minh kết hợp an toàn với K11 năm pass khác.
- K11 IPA đã xác minh 331/331 trước đó không thay đổi.
- Bước kế tiếp K14 **đã có IPA thực và log iPhone do người dùng
  chia sẻ**: [review K14](KAGURA_K14_ARTIFACT_AND_DEVICE_REVIEW.md).
  IPA sử dụng đúng `ios-cse-break.o` nguồn K13, 53 thành phần ZIP,
  103/103 điều kiện PASS, user-shared log UUID/checksum khớp,
  nhưng **không có device attestation hay PAC/Crane proof**.

Bản raw review JSON: `Kagura-K13-CSEBREAK-Artifact-Review.json`,
được tạo từ ZIP thật để đối chiếu SHA/Mach-O và danh sách gate.
