# K24 — Own Running Code Measurement + external Ed25519 reference (experimental)

Ngày 26/10/2026. **Chỉ thử nghiệm độc lập**, không gọi là anti-tamper
hoặc hardened integrity của ứng dụng. Mốc K23 v2 đã có IPA offline
verified + ba lượt PASS người dùng báo cáo, nhưng K23 chỉ kiểm **K14
resource**. K24 khắc phục giới hạn đo đó: ứng dụng Swift mới tự đọc
vùng **`__TEXT,__text` của chính main executable đã được dyld nạp
trong RAM** (ASLR/slide), tính SHA-256 và UUID. Không đọc K14 tham chiếu.

## Trạng thái sau artifact thực (26/10/2026)

**Mode A đã có bằng chứng offline + log người dùng phù hợp**: ZIP K24
9 entries CRC PASS, IPA SHA khớp report, main executable UUID
`825856f9-f710-38bd-a434-aaa983adbc5b`, vùng `__TEXT,__text`
**45880 bytes**, SHA-256
`5471f918a4fad5c7360c7f423d2ed8639c1a329b4a61a40eaaff63c017298b5b`.
Cả ba trường khớp log K24 iPhone `MEASUREMENT_ONLY` mà người dùng báo.
Xem [KAGURA_K24_MODE_A_REAL_ARTIFACT_DEVICE_LOG_REVIEW.md](KAGURA_K24_MODE_A_REAL_ARTIFACT_DEVICE_LOG_REVIEW.md).
**Không phải device attestation hay anti-tamper**. Tới lúc này Mode B
vẫn chưa build IPA với external public key hoặc thử chữ ký trên iPhone.

## Hai chế độ và mức độ tin cậy

**Mode A — đo runtime, không cần khóa:** workflow manual
`.github/workflows/kagura-k24-self-text-external-signature.yml` luôn
có thể build IPA unsigned riêng
`KaguraK24SelfTextLab-TrollStore-arm64.ipa`. Trên iPhone nhấn
**Measure actual running app code**; kỳ vọng log có UUID, độ dài, SHA256
và `DD_K24_COMPLETE=MEASUREMENT_ONLY`. Đây là phép đo chức năng,
**không** phải kiểm tra tính toàn vẹn so với một tham chiếu được tin cậy.

**Mode B — kiểm đối chiếu signed reference:** người dùng tự sở hữu
khóa **Ed25519 private** ngoài repo/CI. GitHub Actions chỉ biết **public
key raw 32 byte**, được đặt vào repository variable tên
`K24_TRUSTED_ED25519_PUBLIC_KEY_B64` *trước khi build K24 IPA*.
Sau khi link xong, Python đo `__TEXT,__text` thật từ K24 executable,
tạo **unsigned signing request** chứa UUID, size và digest. Khóa private
ký nội dung này ngoài repo/CI bằng tool `external_sign.py`. K24 iOS
import `K24-EXTERNAL-SIGNED-STATEMENT.json` từ Files, xác minh chữ ký
CryptoKit Curve25519.Signing với public key biên dịch vào chính IPA,
so UUID/size/text SHA **từ mã đang chạy** với statement đã ký. Không
chấp nhận "PASS" nếu thiếu key, thiếu statement, sai chữ ký hoặc sai
từng byte của phép đo. Kiểm thử negative tạo bản sao RAM đã đổi byte
và cắt 1 byte, đồng thời sửa bản statement với chữ ký giữ nguyên;
**không sửa các trang mã thật** hay thử chiếm quyền hệ điều hành.

**Giới hạn bảo mật:** kẻ có khả năng vá và cài một executable mới
có thể sửa cả code verifier và public key được pin trong cùng IPA. Các
vòng kiểm này không tạo root of trust bất biến. Việc dùng khóa riêng
tách khỏi CI giúp tách quyền signer, nhưng **không bảo đảm root trên
thiết bị bị xâm nhập**. K24 chưa có độc lập device attestation,
CodeDirectory/runtime page trust, rollback protection, PAC/arm64e,
jailbreak hook detection, hardened protection hay Crane integration.
Không thay K15 weak BBCheck thành mẫu này. Không kích hoạt pass Kagura
mới vào production.

## Hướng dẫn trên máy (Windows PowerShell + GitHub macOS CI)

1. Từ thư mục ngoài repository (ví dụ thư mục riêng tư trên máy),
   tạo khóa Ed25519 dùng OpenSSL nếu chưa có (không chia sẻ private):

   ```powershell
   openssl genpkey -algorithm Ed25519 -out K24-private.pem
   openssl pkey -in K24-private.pem -pubout -out K24-public.pem
   ```

2. Lấy giá trị raw public key Base64 và SHA-256 SPKI bằng Python có
   thư viện `cryptography`, chạy ở thư mục chứa public key:

   ```powershell
   python -c "import base64,hashlib; from cryptography.hazmat.primitives import serialization; from pathlib import Path; k=serialization.load_pem_public_key(Path('K24-public.pem').read_bytes()); print('PUBLIC_B64='+base64.b64encode(k.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()); print('SPKI_SHA256='+hashlib.sha256(k.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).hexdigest())"
   ```

   **Giữ SHA SPKI tại nơi quản lý tin cậy riêng**, không tin fingerprint
   do artifact tự báo. Không đặt private PEM trong repository, GitHub
   variables, secrets của workflow này hoặc ZIP artifact.

3. Trên GitHub repo → Settings → Secrets and variables → Actions →
   **Variables** → đặt `K24_TRUSTED_ED25519_PUBLIC_KEY_B64` thành
   `PUBLIC_B64` **trước khi build**. Đây là public key, không phải
   private key. Nếu không có key, workflow **Mode B fail closed ngay CI**,
   không im lặng xây Mode A. Mode A có thể chạy khi chưa cấu hình key:
   nó luôn biên dịch `keyConfigured=false`, kể cả khi repo đang có biến
   public key, để không làm sai kỳ vọng của user.

4. GitHub **Actions → Kagura K24 - Own Running Text and External
   Ed25519 Lab (Experimental) → Run workflow**, chọn branch
   `chore/reconstruction-build-ci`. **Để chạy Mode B**, tại form dispatch
   chọn `require_signed_mode=true` và điền đúng
   `approved_public_spki_sha256` (64 ký tự hex thường từ bước 2,
   được phê duyệt ngoài artifact); workflow gọi
   `scripts/custom_ollvm/kagura_k24/key_preflight.py` để từ chối
   key sai/thiếu/fingerprint sai trước khi gọi Swift compiler.
   Nếu không chọn Mode B, Mode A vẫn đo, không giữ public key bên trong
   binary. Khi CI macOS chạy thành công,
   lấy ZIP artifact
   `DuoDash-Kagura-K24-OWN-TEXT-EXTERNAL-SIGNATURE-LAB-EXPERIMENTAL`.
   Giải nén, tìm thư mục chứa:

   - `KaguraK24SelfTextLab-TrollStore-arm64.ipa`
   - `Kagura-K24-SELF-TEXT-SIGNING-REQUEST.json`
   - `Kagura-K24-SELF-TEXT-IPA-REPORT.json`
   - `K24Pinned.swift`, `K24KeyConfig.json`
   - `KaguraK24SelfTextLab.app/KaguraK24SelfTextLab`

   Đó là thư mục dùng trong `--artifact-dir`.

5. Đặt private và public PEM ở **ngoài** repository, ngoài thư mục ZIP
   đã giải nén. Chạy từ thư mục gốc DuoDash (thay đường dẫn thực và
   SHA SPKI đã ghi từ bước 2; file `--envelope` cũng phải nằm ngoài
   repo/artifact và **chưa tồn tại**):

   ```powershell
   python scripts/custom_ollvm/kagura_k24/external_sign.py sign --artifact-dir "C:\K24-artifact" --trusted-public-key "C:\K24-private\K24-public.pem" --expected-spki-sha256 "<64-hex-approved-fingerprint>" --private-key "C:\K24-private\K24-private.pem" --envelope "C:\K24-private\K24-EXTERNAL-SIGNED-STATEMENT.json"
   ```

   Sau đó có thể đối chiếu offline, **không cần private key**:

   ```powershell
   python scripts/custom_ollvm/kagura_k24/external_sign.py verify --artifact-dir "C:\K24-artifact" --trusted-public-key "C:\K24-private\K24-public.pem" --expected-spki-sha256 "<same-64-hex>" --envelope "C:\K24-private\K24-EXTERNAL-SIGNED-STATEMENT.json"
   ```

   Nếu script lỗi SHA/UUID/key fingerprint, không sửa JSON để ép PASS.
   Sign tool replay raw executable, public pinned và artifact report.

6. Trên iPhone **tương thích với unsigned IPA và cách cài bạn đã dùng
   cho K23**, cài riêng `KaguraK24SelfTextLab-TrollStore-arm64.ipa`
   (không thay thế K23 hay Crane). Mở app, bấm
   **Measure actual running app code**. Với build Mode B, chuyển file
   statement JSON **đã ký bên ngoài** vào app Files, rồi bấm
   **Import EXTERNAL signed statement (.json)** chọn file. Kỳ vọng
   `DD_K24_EXTERNAL_ED25519=PASS`,
   `DD_K24_SIGNED_EXPECTED_MATCH=PASS`, ba negative controls
   `REJECTED`, `DD_K24_COMPLETE=PASS_LAB_ONLY`.
   Bấm **Share full diagnostic text** để chia sẻ log gốc.

Nếu nhận `DD_K24_COMPLETE=MEASUREMENT_ONLY`, điều đó chỉ xác nhận đã
đọc phần code runtime trong RAM, **chưa có signature verification**.
Nếu bất kỳ bước nào FAIL, gửi log và artifact; không coi là PASSED.
Mode A **đã có** artifact macOS thật và log iPhone user-shared
khớp SHA/UUID/size; xem báo cáo Mode A. Còn **Mode B** (bản build
public-key-pinned, ký detached và thử iPhone) **PENDING**.

## 7. Đối chiếu log user chia sẻ với artifact (không phải attestation)

Bộ parser strict mới `scripts/custom_ollvm/kagura_k24/device_log_audit.py`
đọc **chính JSON report K24** thay vì chỉ tin chữ `PASS`.

Ví dụ chạy **mode đo** (log `DD_K24_COMPLETE=MEASUREMENT_ONLY`):

```powershell
python scripts/custom_ollvm/kagura_k24/device_log_audit.py --mode measurement --log "C:\K24-logs\01-measure.txt" --report "C:\K24-artifact\Kagura-K24-SELF-TEXT-IPA-REPORT.json" --out "C:\K24-logs\K24-MEASURE-REVIEW.json"
```

**Mode signed** bắt buộc có cả envelope và PEM/fingerprint bên ngoài
để replay chữ ký Ed25519 offline, rồi mới chấp nhận các dòng log
`PASS_LAB_ONLY` đúng schema. Không truyền private key:

```powershell
python scripts/custom_ollvm/kagura_k24/device_log_audit.py --mode signed --log "C:\K24-logs\02-signed.txt" --report "C:\K24-artifact\Kagura-K24-SELF-TEXT-IPA-REPORT.json" --artifact-dir "C:\K24-artifact" --envelope "C:\K24-private\K24-EXTERNAL-SIGNED-STATEMENT.json" --trusted-public-key "C:\K24-private\K24-public.pem" --expected-spki-sha256 "<64-hex-approved-fingerprint>" --out "C:\K24-logs\K24-SIGNED-REVIEW.json"
```

Các receipt ghi rõ `actual_iPhone_runtime_independently_verified=false`,
`runtime_security_or_anti_tamper_proven=false`, không tạo chứng thực
thiết bị hoặc bảo đảm chống bản app bị thay thế.

## Nghiệm thu tiếp theo

- Mode A có ZIP thật và log user-shared tương quan với
  `__TEXT,__text`; không cần thử lặp vô hạn.
- Mode B bắt buộc chạy **workflow mới** với `require_signed_mode=true`
  và fingerprint được operator xác nhận, rồi review IPA/raw Mach-O
  bản key-pinned trước khi ký request.
- Mode B: app xác nhận Ed25519 imported, signed expected và memory
  code trùng; thử sai key, sai chữ ký, changed payload, stale release
  và import thiếu. Phải FAIL CLOSED. `PASS_LAB_ONLY` không phải
  security tamper attestation.
- Không can thiệp Crane production, Theos, K18 hoặc K15.
