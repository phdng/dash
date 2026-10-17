# Protection Lab — benchmark overhead trên iPhone (không dùng làm security score)

**Trạng thái:** Mã nguồn và workflow đã triển khai; chỉ báo hiệu năng
iPhone sau khi ứng dụng **được ký hợp lệ, cài trên máy dự phòng và thực
sự được người dùng bấm chạy**. Build xanh trong GitHub Actions hoặc chạy
macOS host không xác nhận điều đó.

## Các phép đo

Sau khi bốn nhóm VM, CE/ICALL, IGV/IBR và Objective-C CE kiểm tra đúng
8.192 vector mỗi nhóm và UI hiện `DD_RUNTIME_COMPLETE=PASS`, nút
**Measure overhead (optional)** mới hoạt động. Nút này không chạy tự
động, không đo hay can thiệp Crane sản phẩm.

Ứng dụng đo năm cặp lời gọi, cùng dữ liệu đầu vào synthetic:

| Cặp | Bản đối chứng | Bản được biến đổi |
|---|---|---|
| VM | `dd_canary_native` | `dd_canary_vm` |
| CE | `dd_pilot_plain_hash` | `dd_pilot_protected_hash` |
| ICALL | `dd_pilot_plain_dispatch` | `dd_pilot_protected_dispatch` |
| IGV | `dd_igv_plain` | `dd_igv_protected` |
| IBR | `dd_ibr_plain` | `dd_ibr_protected` |

Mỗi hàm chạy 20.000 lần trong mỗi mẫu, lấy trung vị 5 mẫu dùng
`clock_gettime(CLOCK_MONOTONIC)`. Chỉ đo elapsed nanoseconds **cho cả
20.000 lời gọi**, không phải nanoseconds mỗi lời gọi. Bật tối ưu hóa
`-O1`, dùng các wrapper cùng giao diện; checksum `volatile` giữ
các phép tính cần thiết. Tỷ số chỉ là
**thời gian protected / thời gian plain quan sát được**. Số liệu chịu
ảnh hưởng lớn từ thermal, CPU frequency, scheduler và cache; không áp
ngưỡng bảo mật hay ngưỡng hiệu năng bắt buộc.

## Hai bản báo cáo tách biệt

Sau khi benchmark hoàn thành, nút **Share result text** hiện lựa chọn:

- **Share functional PASS/failure:** xuất chính xác 7 dòng
  `DD_RUNTIME_*` để chạy `device_audit.py verify-log`.
- **Share observational benchmark:** xuất riêng 17 dòng `DD_PERF_*`
  và không tự nhận là log PASS chức năng.

Ví dụ (chỉ minh họa số liệu, **không phải đo đạc thực trên iPhone**):

```text
DD_PERF_SCHEMA=1
DD_PERF_CONTEXT=IOS_DEVICE
DD_PERF_ABI=arm64e:0x80000002
DD_PERF_ITERATIONS=20000
DD_PERF_REPEATS=5
DD_PERF_ESTIMATOR=MEDIAN_ELAPSED_NS
DD_PERF_VM_NATIVE_NS=100000
DD_PERF_VM_PROTECTED_NS=310000
DD_PERF_CE_NATIVE_NS=80000
DD_PERF_CE_PROTECTED_NS=90000
DD_PERF_ICALL_NATIVE_NS=130000
DD_PERF_ICALL_PROTECTED_NS=135000
DD_PERF_IGV_NATIVE_NS=115000
DD_PERF_IGV_PROTECTED_NS=119000
DD_PERF_IBR_NATIVE_NS=405000
DD_PERF_IBR_PROTECTED_NS=605000
DD_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_PROOF
```

## Phân tích trên máy tính

Lưu lại 17 dòng nguyên dạng UTF-8 và chạy:

```sh
python scripts/protection_lab/perf_audit.py verify \
  --log iphone-arm64e-performance.txt \
  --context IOS_DEVICE --arch arm64e \
  --out iphone-arm64e-performance.json
```

Với iPhone 6s arm64 thì đổi `--arch arm64`. Parser từ chối log
`MACOS_HOST` nếu người dùng tuyên bố đó là iOS, log mất dòng, số 0,
NaN, số âm, thứ tự sai hoặc dữ liệu thêm. JSON chứa 5 tỷ số, SHA-256
log và trường `ios_device_runtime_verified=false`: **parser chỉ
kiểm tra nội dung, không thể chứng thực nguồn gốc hoặc kết quả chạy.**

Workflow `.github/workflows/protection-ios-app.yml` còn tạo
`host-performance.log` và `host-performance-report.json` từ một
binary host macOS riêng. Đây là kiểm thử chạy được native và giao thức
báo cáo, **không phải phép đo hiệu năng iOS**.

Muốn so sánh có ý nghĩa, cần giữ kèm log chức năng PASS, thiết bị/iOS,
kiến trúc Mach-O thực sự được nạp, bản ký, điều kiện thermal và vài lần
lặp tay. Chưa có kết quả runtime A12+ và không tích hợp mã này vào
CRCredits, CranePrefs, hook, daemon hoặc securityd.
