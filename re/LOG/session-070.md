# LOG/session-070.md
_Date: 2026-10-06. Objective: reopen steady-state at user request, make RECONSTRUCTION buildable, add GitHub Actions build._

## Làm gì
1. Tạo branch `chore/reconstruction-build-ci` từ master.
2. Đối chiếu STATE/TODO/COVERAGE + session-069; xác nhận 30 synthesis modules tồn tại nhưng repo chưa có Makefile/control/CI.
3. Đọc filter gốc: Bundles = springboard/Preferences/CarPlayApp/UIKit, Mode=Any; Executables=mediaserverd/kbd.
4. Tạo buildable runtime phase-1:
   - `ReconstructionRuntime.{h,m}`
   - role detection theo AC5FC suffixes;
   - clearpanes one-shot;
   - AppBridge snapshot/cache/notify;
   - settings.changed Darwin observer;
   - SpringBoard-only activation để tránh chạy behavior chưa đủ evidence ở role khác.
5. `Tweak.x` ctor gọi `DDReconstructionStart()`.
6. Thêm Theos `Makefile`, `control`, `DuoDashReconstruction.plist`.
7. Thêm `.github/workflows/build.yml`: macOS + Theos + `make clean all` + upload dylib/plist.
8. Thêm `scripts/verify_reconstruction.py` + BUILD.md; local verifier PASS.

## Quyết định
- KHÔNG compile 30 synthesis modules bằng fake extern/stub hàng loạt. UNKNOWN/HYPOTHESIS phải còn nhìn thấy.
- Build target chỉ chứa code có thể biểu diễn từ evidence mà không cần private symbols chưa resolve.
- 74C8 runtime approximation giữ type-gated raw values ở chỗ helper normalize/filter chưa resolve; không claim 1:1.
- CI macOS là compiler gate đầu tiên vì workspace hiện tại Windows, không có Xcode/iOS SDK.

## Verification
- `python scripts/verify_reconstruction.py` → PASS: 30 synthesis modules + build scaffold + filter.
- Theos compiler build chưa chạy local; sẽ được chạy bởi GitHub Actions macOS.

## Next
- Làm CI xanh trước.
- Sau đó promote từng subsystem từ synthesis → compile-safe runtime, ưu tiên prefs setters / notify fabric trước private UIKit/SpringBoard hooks.
