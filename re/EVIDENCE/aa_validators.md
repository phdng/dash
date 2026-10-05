# EVIDENCE/aa_validators.md — AA9FC/AAAD0 validators + A7E04 unrefuse (session-010)
_Nguồn: subagent general đọc FULL AA9FC (30 dòng) + AAAD0 (30) + A7E04 (22) + A761C/A78B8/A7D54/A7338. Mỗi claim có file:line + nhãn._

## 1. AA9FC — validator số thực (AA9FC.c:9, __int64 (a1=obj, a2=out double-bits))
- a1 retain ngay (:16); a2 nhận bit-pattern double khi success (:21). Return 1/0 (:22,26,29). Không NSError/throw/log.
- Check duy nhất: isKindOfClass NSNumber (:18; subclass qua, NSString số/NSNull/Array/Dict rớt). Sau đó doubleValue + finite bit-mask: `(bits & 0x7FFF...) <= 0x7FEFFFFFFFFFFFFF` (max finite) (:19; v5 bit-pattern :13). Chấp nhận ±0/subnormal/normal/DBL_MAX; **loại ±Inf/NaN**. Không range hẹp, không isnan(), không integer-check.
- Ghi *a2 chỉ khi pass (:21). nil/wrong-type/NaN/Inf → 0, không chạm out (:25-27). retain/release cân bằng (:16,28). Pure, không global (header callee b05a0 không dùng trong body — listing dư, UNKNOWN).
- Error: mọi fail silent return 0 (caller không dùng out).

## 2. AAAD0 — validator số nguyên/enum (AAAD0.c:9, __int64 (a1, a2=out int64))
- Giống hệt AA9FC (isKindOfClass :18 + finite mask :19) + khác duy nhất: pass → `*a2 = llround(v5)` (:21; b05a0 HYPOTHESIS chính là llround).
- **Không strict-int**: 1.6 → pass, out=2; 1.5→2; -1.5→-2 (HYPOTHESIS từ llround + không có floor==value check). **Không whitelist enum**: không ==/switch/range trong body (caller A9840 giữ range-check nếu có — HYPOTHESIS).
- Không check overflow llround (1e308 finite → pass nhưng llround UB, thường LLONG_MIN, vẫn return 1 — HYPOTHESIS libc).
- Error paths giống AA9FC (:25-28).

## 3. A7E04 — KHÔNG phải persist worker (A7E04.c:9, void (a1=block, +32=captured string HYPOTHESIS))
- Caller duy nhất A7D54 (A7E04:5); A7D54 guard queue 1650E0 + length rồi copy + async (A7D54:21-31) → A7E04 luôn async string non-empty đã copy.
- Logic: v2=A761C() (:14); v2 && isEqual(v2, *(a1+32)) (:16) → A78B8() (:18) + A7338() (:19, delete-trước-trigger); else no-op giữ file (:16-21).
- Body **không writeToFile/create/fopen/fwrite/chmod/plist-serialize** → hypothesis cũ "persist" **SAI (CONFIRMED SAI)**.
- Đích file duy nhất nhánh: `/var/mobile/Library/DuoDash/license.refused.plist` (A761C:20-26 + A78B8:14-21 build path giống hệt; không phải geometry/prefs/license khác).
- Format read-side A761C: dictionaryWithContentsOfFile (:27) + isKindOf NSDictionary (:30, else nil :42) + dict[@"nonce"] isKindOf NSString (:32-37, else nil) + length!=0 (:44-47) → autoreleased string (:48-51).
- Ghi/xóa: **A78B8 = removeItemAtPath error:0** (:14-22, fail silent :22). Không chmod/write trong A761C/A7E04/A7D54/A7338. Error: missing/hỏng/non-dict/thiếu nonce/non-string/empty → A761C nil → A7E04 no-op, không crash.
- A7338 (:16-38): v0=A774C(); !A7838(1650D0) || ![1650D8==v0] → check deviceID (A3558/A4450) + alert "Cannot identify this device" (A54A4/A5514). Không file-op trực tiếp; transitive sâu hơn UNKNOWN.

## 4. Verdict hypothesis cũ
- "AA9FC=parse double, AAAD0=parse int/enum" → **ĐÚNG bản chất, sửa 2 chi tiết**: cả hai chỉ nhận NSNumber + finite (reject NSString số); AAAD0 chấp nhận mọi finite-double rồi llround (không strict, không whitelist, không overflow-check).
- "A7D54→A7E04 persist, đích UNKNOWN" → **SAI persist, ĐÚNG chain; đích đã rõ**: A7E04 = conditional-unrefuse (stored-nonce == async-string → delete refused.plist + re-arm A7338, else no-op).
