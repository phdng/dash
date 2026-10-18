# K17 — Ed25519 detached signature cho tham chiếu Mach-O offline

Ngày triển khai: **18/10/2026**. Trạng thái:
**STAGED_EXTERNAL_ED25519_KEYS_REQUIRED_NOT_SIGNED_CI_VERIFIED**.

K16 đã có ZIP thực từ GitHub Actions, 54 thành phần với 276/276
đối chiếu raw file-backed PASS; 3 executable arm64 post-link
`__TEXT,__text` được đo SHA-256/UUID đúng phạm vi **offline**.
[K16 review](KAGURA_K16_ARTIFACT_REVIEW.md).

K16 manifest ban đầu **không có chữ ký**; đối thủ kiểm soát được
binary và manifest có thể tính lại hash. K17 chỉ triển khai
**chữ ký Ed25519 detached cho raw K16 manifest**, đòi hỏi
**public key được phê duyệt ngoài artifact**, không tự sinh một
khóa CI rồi tự tin rằng đó là trust anchor.

## Quy tắc trust bắt buộc

- Khóa ký Ed25519 **private** được giữ bên ngoài repository,
  cung cấp qua GitHub Actions secret
  `K17_ED25519_PRIVATE_KEY_PEM`.
- Khóa công khai Ed25519 được chủ sở hữu phân phối độc lập qua
  GitHub Actions repository variable `K17_ED25519_PUBLIC_KEY_PEM`.
  Người kiểm toán độc lập nhận bản public PEM **ngoài ZIP**,
  tuyệt đối không dùng một PEM kèm trong ZIP làm trust anchor.
- Fingerprint **SHA-256 của DER SubjectPublicKeyInfo (SPKI)** cần
  được chủ sở hữu phê duyệt trước qua kênh độc lập. CI dùng
  repo variable `K17_ED25519_PUBLIC_KEY_SPKI_SHA256` và CLI
  verifier yêu cầu `--expected-spki-sha256` được truyền riêng.
  **Các biến của cùng GitHub project không tự cung cấp tính độc lập**
  nếu admin hoặc đối thủ có thể sửa tất cả; khi kiểm toán, so với
  fingerprint đã ghi lưu qua kênh tin cậy độc lập với CI.
- Mặc định thiếu/bị đổi key, fingerprint hoặc private/pub không
  khớp → **workflow FAIL trước khi build**; không phát hành
  `SIGNED_PASS` tự tạo.
- Private PEM nằm trong thư mục runner temp
  `$RUNNER_TEMP/k17-external-signing-material`, **ngoài artifact**,
  chỉ dùng trong bước ký; không ghi khóa vào report/ZIP/source.
  GitHub runner ephemeral được dọn khi kết thúc job.
- **Không gắn khóa vào IPA, không ký executable, không dùng**
  code signing hoặc on-device verifier.

## Tạo và phê duyệt khóa riêng bên ngoài dự án

Trên máy được bạn tin cậy, ví dụ OpenSSL 3:

```sh
umask 077
openssl genpkey -algorithm ED25519 -out k17-private.pem
openssl pkey -in k17-private.pem -pubout -out k17-public.pem
```

Dùng script với Python có `cryptography==50.0.2` tính đúng
**SHA-256 DER SPKI** của public key (không phải hash PEM):

```python
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives import serialization
key = serialization.load_pem_public_key(Path("k17-public.pem").read_bytes())
raw = key.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
print(hashlib.sha256(raw).hexdigest())
```

Lưu riêng fingerprint/public PEM và kiểm soát người có quyền sửa
GitHub Actions secrets/variables. **Không commit hoặc gửi private PEM
cho ChatGPT.** Cấp secret và hai variables trên vào repo GitHub trước
khi chạy workflow thủ công.

## Workflow thủ công

`.github/workflows/kagura-k17-external-ed25519.yml`:
**Kagura K17 - Externally Trusted Ed25519 Offline Manifest (Experimental)**.

1. Thiết lập Python venv độc lập, dùng thư viện chuẩn cryptography
   `50.0.2`. Kiểm thử K17 fail-closed với **khóa test sinh tạm**,
   cộng regression K16/K15/K14/K13 và audit pass.
2. Bắt buộc có private secret/public variable/fingerprint
   đã được phê duyệt; không tự tạo private key trong CI.
3. Build lại Kagura LLVM19 commit pin
   `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`,
   registry SHA
   `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`,
   chỉ tái tạo **CSEBreakPass K13 + IPA lab K14**, không chạy
   `kagura-bbcheck`.
4. Rerun K13 native 4096-vector parity, iOS arm64
   source/objects/UUID/IPA K14, K16 post-link raw section
   `__TEXT,__text` và replay manifest trước khi ký.
5. Ký chính xác byte stream `DOMAIN || K16_MANIFEST_RAW_BYTES`,
   trong đó DOMAIN là
   `DuoDash/K17/K16/MachOTextOfflineEd25519/v1\0`
   để tránh nhầm giao thức. Signature Ed25519 raw **64 bytes**,
   không cho ký nội dung đã bị sửa/fake security claim.
6. Ký xong sẽ replay **lần hai bằng public key cung cấp riêng**,
   SPKI fingerprint khớp, chữ ký hợp lệ; receipt JSON được tính lại
   từ signed bytes và field bắt buộc (không thể tự đặt
   runtime/device/security PASS).

Các file riêng của K17:
- `Kagura-K17-K16-MANIFEST.ed25519`: detached signature 64 bytes.
- `Kagura-K17-SIGNATURE-RECEIPT.json`: algorithm/domain, SHA-256,
  external SPKI fingerprint, các cờ scope an toàn.
- Raw `Kagura-K16-OFFLINE-TEXT-MANIFEST.json`, ba executable
  gốc K13/K14 cùng báo cáo/IPA để independently replay.

Artifact:
`DuoDash-Kagura-K17-EXTERNALLY-TRUSTED-ED25519-OFFLINE-EXPERIMENTAL`.

## Kiểm lại trên máy độc lập

Cài `cryptography==50.0.2`, giữ public key tin cậy ở đường dẫn
**ngoài thư mục artifact** rồi chạy:

```sh
python scripts/custom_ollvm/kagura_k17/signature.py verify \
  --out /path/to/Kagura-K17-Signed-Offline \
  --trusted-public-key /trusted/location/k17-public.pem \
  --expected-spki-sha256 <fingerprint-64-hex-da-luu-doc-lap>
```

Lệnh verification **không cần private key**. Nó bắt buộc
parse lại các executable thật, K16 manifest/UUID/source hashes,
kiểm public-key fingerprint và chữ ký Ed25519 detached.
Nếu archive bị thay byte, manifest giả, thiếu source, key không
khớp hoặc claim được nâng trạng thái thì FAIL.

## Giới hạn dù K17 CI ký thành công

- Ed25519 xác thực **offline reference được ký bởi khóa được
  chấp thuận**, không chứng minh khóa không bị đánh cắp,
  freshness, anti-replay hoặc môi trường GitHub CI không bị xâm nhập.
- K16 reference gốc trong payload vẫn có
  `metadata_authenticated=false` vì bản đo K16 chưa ký.
  Receipt K17 chứng minh chữ ký của *tham chiếu file*, không làm
  K16 trở thành một runtime verifier.
- Không có đối chiếu in-memory khi iPhone chạy, không có
  code signing/Apple attestation, không chứng minh per-basic-block
  integrity, ASLR/PAC/dyld fixups, Objective-C hooks hoặc
  biện pháp phòng chống đối thủ kiểm soát máy khách.
- **K15 vẫn BLOCKED** vì weak `kagura_bb_check()` luôn trả về 1;
  K17 không thay callback, không tạo stub khác, không triển khai BBCheck.
- K11–K14 và Crane production **không sửa**, iPhone K17 NOT_TESTED.
- **Portable test PASS không đồng nghĩa có khóa ngoài hoặc bản
  signature từ CI thực**. Khi chưa có CI artifact K17, trạng thái
  vẫn là `STAGED_EXTERNAL_ED25519_KEYS_REQUIRED_NOT_SIGNED_CI_VERIFIED`.
