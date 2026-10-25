# Kagura K21 — báo cáo đối chiếu artifact macOS thực

Ghi nhận 25/10/2026. Trạng thái: **REAL_MACOS_OFFLINE_AARCH64_WORD_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY**.

ZIP người dùng cung cấp: `DuoDash-Kagura-K21-STATIC-OPCODE-INVENTORY-OFFLINE-EXPERIMENTAL.zip`.
SHA-256 **`1991f38f5af55f310352e0f23d6e2a566eec8dba5d0a35ee6c8c2d91fffe40aa`**, **91.451 bytes** và **57 entries tên duy nhất** (CRC sạch, không duplicate/traversal/symlink/encryption). Đối chiếu trực tiếp file bytes trong lần review: **785/785 checks PASS** (không phải 785 unit tests hay kiểm tra bảo mật).

| Target mã thực | Word AArch64 little-endian | Tổng bytes |
| --- | ---: | ---: |
| macOS K13 baseline `_dd_k8_evaluate` | 115 | 460 |
| macOS K13 protected `_dd_k8_evaluate` | 136 | 544 |
| iOS K14 protected `_dd_k8_evaluate` | 136 | 544 |
| iOS K14 `_dd_k14_ios_parity` | 121 | 484 |

Bằng chứng độc lập gồm ba thin arm64 `MH_EXECUTE`, `LC_UUID`, section `__TEXT,__text` SHA-256, K19 `LC_SYMTAB` và địa chỉ/cận của 4 interval, K20 ULEB128 `LC_FUNCTION_STARTS` (macOS 3/3, iOS 30 starts), K21 histogram đủ 10 mẫu opcode được tính lại từ raw little-endian machine words và digest. Object/IR/pinned CSEBreak trace K13 hợp lệ. Native baseline và protected đều `DD_K8_COMPLETE=PASS` cho 4.096 vectors, checksum `25a3318e3d7d6525`. IPA K14 unsigned bên trong ZIP có executable trùng raw Mach-O.

**Giới hạn:** Đây là đối chiếu *artifact offline* macOS thực, không có GitHub Actions run ID/console log đầy đủ trong ZIP và chưa quan sát K21 độc lập trên iPhone. Không xác nhận CFG/function extent/basic block identity, signed trust anchor, runtime self-integrity, anti-tamper, PAC hoặc Crane production. K18 tiếp tục user-skipped/NOT_TESTED, K15 BBCheck weak always-return-1 bị chặn. Bằng chứng không tự biến thống kê word thành security protection.

K22 sẽ đo độ tái lập bốn vùng code trong **hai lần build macOS riêng**. K22 PASS chỉ đóng mốc nghiên cứu offline, không tự chứng minh hai build được attested hoặc production-ready.
