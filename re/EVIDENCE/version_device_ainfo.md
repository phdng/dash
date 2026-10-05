# EVIDENCE/version_device_ainfo.md — P3-5 + Q-10 (session-006)
_Nguồn: subagent general đọc decompile. Mỗi claim có file:line + nhãn._

## A. P3-5 version/device-specific + locale flow

### A.1 Ba file chỉ định
- **4008.c** (70 dòng): `sub_4008(a1..a4)` = 4 version ints (9). Đường nhanh: qword_163428==-1 && 163430!=0 → pack v13 → `_availability_version_check(1,v13)` (21-28). Chưa init → lưu args, AD018(), restore, thử nhanh (31-43). Fallback (163430==0): so thủ công với dword_163410/414/418 (parse từ plist, 4198.c) — 410>a2→1, <a2→tiếp; bằng→414 vs a3; bằng→418>=a4 (45-69). Ngữ nghĩa: true nếu OS >= yêu cầu (HYPOTHESIS chiều 1=true). AD6B8 thunk weak-import (10-12). Init 4198:47-50 weak-link check. **Generic "OS>=X.Y.Z?", không branch iOS cụ thể; caller duy nhất 46340 (UNKNOWN threshold).**
- **A3558.c ĐÍNH CHÍNH** (9-14): chỉ dispatch_once + return qword_1650C0. Writer duy nhất A3598:73-74 (=A385C hash), clear khi fail (54-55). A3598:26-60: override→"test-override" (26); MobileGestalt UniqueDeviceID (37, literal) → "MobileGestalt" (59); trim → 1650B8, encode+hash → 1650C0 (62-74). **A3558 = device_hash (UDID hash), KHÔNG phải hw.machine.** Dùng làm device_hash/hq (A574C:87,115-118; A8A88:86,112-113; 4C34:404). Tiền đề task sai một nửa — CONFIRMED.
- **ACF1C.c** (31 dòng): chỉ announce "role=%s pid=%d stage=installed armed_wall=%.0f boot=%s" ra qword_164C88 khi 168D18&&168D19&&164C88 (9-30). bootUUID via 9CC7C (22-26; sysctl kern.bootsessionuuid như 9CF9C:18, 86028:46, 4C34:1231). Callers 4A08:16, 4A80(via 948C0), 4C34:1460. Không branch version/device/locale.

### A.2 Grep version/device (decompile/*.c)
| # | Pattern | Site | Kết luận |
|---|---|---|---|
|1-3|availability_version_check|4008:28, 4198:47-50, AD6B8:10-12|Đường nhanh/resolve/thunk. Không branch cụ thể|
|4|ProductVersion + SystemVersion.plist|4198:95,129,141|fopen plist → CFPropertyList → ProductVersion → sscanf %d.%d.%d → 163410/414/418. Truth cho fallback 4008. Chỉ parse, không loại iOS|
|5|kCFCoreFoundationVersionNumber|**3AE50:120,124 — branch version DUY NHẤT**: `<1946.102` → setCompletionBlock: else addCompletionHandler: (và đảo cho v18). Dùng chọn selector SBMainWorkspace evict (3AE50:81-92, evictFromPhoneThen, timeout 2s + fallback, 149-168). Không disable tính năng. Map 1946.102≈iOS 17.x HYPOTHESIS|
|6|operatingSystemVersion|A574C:174, 9EE88:1358, thunk B2720|Điền ios_version/os_version telemetry (A574C:182-196, 9EE88:1437-1446). Không if|
|7|UIDevice|455D0:219-220 (hook orientation), 47F74:22, 98238:179-180 (currentDevice→name→BLE packet khi _isFirstPairAfterLockOn, 200-207)|Không branch|
|8|sysctlbyname hw.machine|A574C:135 via A2720:21,27|Đọc → sanitize [A-Za-z0-9,_-] len<=0x20 (135-161) → dict model. Fail → bỏ key, tiếp tục|
|9|sysctl hw.machine/model/osversion/ncpu/memsize/bootsessionuuid|9EE88:1432-1469 via A2720|dict device{model,machine,os_version,os_build,ncpu,memsize,boot_session}. A2720:20-39 wrapper (fail → "?"). Không branch|
|10|kern.bootsessionuuid|4C34:1231, 86028:46, 9CF9C:18|boot_id → CarSleeper state.plist. Không branch|
|13|MinimumOS|0 hit decompile|Floor duy nhất = Info.plist 14.0 (external)|
|14|systemVersion/AppleLanguages/currentLocale/preferredLanguage|0 hit|Không đọc UIDevice.systemVersion/AppleLanguages|

### A.3 Locale/language
| # | Site | Nội dung |
|---|---|---|
|L1|6A4E4:21-24|Write duy nhất: guard 9B284 whitelist (19) → SetAppValue duodash_language → Sync → 9B314 → post language.changed|
|L2|9AFB0:34-103|Read: (1) /var/tmp/duodash_lang_force trim (34-59), (2) prefs duodash_language (62), (3) legacy carnav_language migrate→ghi lại (67-86), (4) default en (90). Validate 9B284 mỗi bước. Cache 164C38 + lock 164C58 (26-33,105-115)|
|L3|9B284:9-40|Validator strcmp off_130E88, step 2 đến 32 → 17 entries (9AF00:24 v4=17, 9AE54:18). Nội dung 17 strings UNKNOWN (chỉ lộ "en" pointers 130E88)|
|L4|9B314:9-22|Cache-clear 164C38/40 dưới unfair_lock. Mọi observer gọi|
|L5|9B848:14-20 + 9B87C|Observer toàn cục → 9B87C()=9B314(). Chỉ clear|
|L6|948C0:156-162|Settings ctor đăng ký 96220 cho language.changed (+ble.status, settings). Handler 96220: 9B314 + async main 96D70|
|L7|8C41C:30-36|License controller observe license.changed + language.changed → 8E0F0 (body UNKNOWN, mẫu clear+reload HYPOTHESIS)|
|L8|8EFE4:23-36|NavBubble controller observe language + listchanged → 91DCC: 9B314 + async main 91E58|
|L9|920C0:23-36|VoiceCmd controller observe language + listchanged → 933FC (cùng mẫu, HYPOTHESIS)|
|L10|93A3C:20-26 + 93B3C:20-27|TweakMgmt observe → 93B3C: 9B314 + async main 93BC8|
|L11|9B314:5 fan-out|Callers 6A4E4,8EE04,91DCC,91EE0,933FC,9394C,93B3C,948C0,96220,9B87C — clear + main-reload|
|L12|9EE88:1376-1381|NSLocale en_US_POSIX chỉ cho NSDateFormatter created_at. Không branch locale user|
|L13|truedash_language|strings 1418 + pointers CFString, **0 hit decompile** — dead/legacy|
|L14|carnav_language|Chỉ migrate tại 9AFB0:67-86. Legacy|

### A.4 Tóm tắt P3-5
- iOS floor khai báo 14.0 (external). Runtime: weak-link + plist fallback (chạy cả OS cũ). Branch version duy nhất 3AE50 CF<1946.102 (evict callback selector, có fallback+timeout; map iOS HYPOTHESIS). operatingSystemVersion chỉ telemetry.
- **Không loại device nào**: hw.machine sanitize-then-optional; device_hash rỗng → fail-soft no_device_id/no_blob; bootsessionuuid fail → bỏ boot_id; UIDevice.name rỗng → bỏ qua.
- Language: write 6A4E4 → post → 6 observers (clear + main-reload). Read 9AFB0 4-tầng + whitelist 17 + cache. Không AppleLanguages.

## B. Q-10 license info-response schema (A9840.c 654 dòng, parse off-main queue geo 165118)
- Chuỗi: A8A88 build POST /api/v1/info timeout 6s (205-225; body 16 keys hq/v3/tb/mz/ej/w9/c4/ux/u2/gk/d7/dn/dr/y5/yq/ab + nf/n8 + nonce, 90-166,90-97) → snapshot + dataTask (249-277; ++165400, 165420=now, push 165138) → A9678 dispatch_async queue 165118 (v10 từ 7F14C:151-154, com.sensetechlab.geo) block A9840 với 15+ fields (49-83).
- Parser: v4=statusCode (pointer-obfuscated, 150-155), v5=JSON dict nếu length>0 (156-171).
- 4 nhánh: A (v4==158.reloff+3 → log A82C4(1,**403**,e2) :181 — HYPOTHESIS mạnh 403); B (v4==1A8.sectname[5] → A82C4(3,**429**,e9) :619 — HYPOTHESIS mạnh 429); C success (!err && v4==B8.segname && v5 dict && keys pass → A82C4(0,**200**) :568 — HYPOTHESIS 200); D error body/network (A82C4(2,v4,domain/code-or-body) + A6344(1) + A850C code 2, :217-239).
- Điều kiện success gộp: NSError null && 200 && dict && z0==true && w9/q6 AAAD0 && bw/bx NSArray count khớp && entries validate && c4 && c8 count==2 && ux/u2 && kp count≤2 && entries validate.
- Keys (objectForKeyedSubscript): e2 (NSString else "-", log 403); e7 (optional → retry-after ms, default 1050.0; 165420=v89/1000+now-1.05); e9 (NSString, chỉ khi retry-flag → error 3 no-retry); z0 (NSNumber true, cổng success); w9/q6 (AAAD0, UNKNOWN ngữ nghĩa); bw/bx (NSArray count==block[8] && == nhau; entries NSDictionary); bw[i].{i1,i2 (AA9FC), tb (0..8192), mz (>=0,<=8192)}; bx[i].{tb,mz} (>=0); c4 (AAAD0); c8 (NSArray==2 → block[168/176]); ce/u7/jv (bool flags → block); ux/u2 (AAAD0); kp (NSArray<=2 → block[216], loop entries l3/l4/l9 AAAD0 + lm/lr AA9FC + l7 bool); tk/nq (optional, không fail nếu vắng). "b2" tại :184 là giá trị so sánh, không phải key.
- HYPOTHESIS: AA9FC=parse double, AAAD0=parse int/enum (chưa đọc bodies).
- Side-effects: 403 → A82C4 verdict geometry.state (1,403,e2) + A6344(0); nếu e2=="b2" && body non-empty → async queue 1650E0 A7C64 + 1461D8 (verify/cache blob ngay cả khi 403). Success → ++165408, 165418=now; body non-empty → A7D54 → async 1650E0 A7E04 persist (đích file UNKNOWN); A6344(0); fresh (216==165128) → storeStrong 165108 + memcpy 165150 + 165120=1 + uptimes; A82C4(0,200); A850C success kèm blob. 429 → retry-flag? error 3 : dispatch_after(v89ms, geo, AAA74) → A8A88 retry một lần (AAA74:32). Error D → A850C code 2.
- Return void; mọi kết quả qua A850C → main AABC0 → caller block. Không CFPreferencesSet* trực tiếp trong A9840 (prefs gián tiếp via A7D54→A7E04 + geometry.state file).
- UNKNOWN: numeric mapping tuyệt đối v4 (cần xref disasm); bodies AA9FC/AAAD0/A4450-nonce/A7E04/AABC0-caller; 16 strings off_130E88 còn lại; threshold 46340→4008.
