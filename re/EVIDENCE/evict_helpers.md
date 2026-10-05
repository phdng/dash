# EVIDENCE/evict_helpers.md — kill-vs-unhost: 85B8 + 7764C (session-009)
_Nguồn: subagent general đọc FULL 85B8 + 7764C + callers 25C4C/25FE0/26FE4/20010 + helpers + grep. Mỗi claim có file:line + nhãn._

## 0. Phạm vi
Đọc FULL 85B8.c:1-48, 7764C.c:1-116. Callers 25C4C:1-126, 25FE0:1-201, 26FE4:1-265, 20010:1-91. Helpers 84D8/7044/70FC/7E730/74C8 + gating 771D4. Grep `sub_85B8\(|sub_7764C\(` = 9 matches (2 định nghĩa + 5 điểm gọi thực trong 4 files, +2 header). Grep kill/proc đối chiếu.

## 1. sub_85B8 — FULL body (85B8.c:9, void, a1=bid NSString HYPOTHESIS mạnh)
- a1 string: length guard (:22), isEqualToString (:31), containsObject (:32); callers truyền cpuiBid/bid (20010:40-41, 25C4C:59, 26FE4:107). Không arg gen/pid/state/path. Return void.
- Prefs đọc: 7044("appbridge_split_carplay_ui") (:24; 7044:18-37 dict plist, NSString non-empty else nullptr; missing → fallback @"" :27-28) + 70FC() (:30; đọc ui + more → 7E730 merge dedup trừ main :31-75, 70FC:18-28). v4=main, v5=merged [main+more].
- Điều kiện (:31-33): v6=![v4==v1] (inverted), v7=[v5 contains:v1]; `if (v6 || v7)` mới làm; bid==main && ∉list → no-op. bid empty → no-op (:22).
- Nhánh (:35-38): v6 → v8=@"" (clear main) else v8=v4 (giữ main). (:39-41): v9=[v5 mutableCopy]; [v9 removeObject:v1] (removeObject duy nhất :40); 84D8(v8,v9).
- 84D8 (84D8:9-35): a1.length?copy:empty (:19-22); 7E730 tái-normalize (:27); **SetAppValue(ui, ...duodash.settings) + SetAppValue(more, ...) + AppSynchronize** (:28-30, 2 prefs duy nhất); 74C8() (:31) → writeToFile plist (:416) + post resolved (:419, lan truyền cho AppBridge/SB — consumer cụ thể HYPOTHESIS). 74C8 clearpanes nhánh (:139-196) không liên quan trừ khi file tồn tại.
- **KHÔNG kill/unhost/process**: FULL body :21-47 chỉ length/isEqualToString/containsObject/mutableCopy/removeObject + helpers; callees toàn objc/CF (không kill/proc); grep kill chỉ match removeObject: NSArray (:40). = **prefs-only logical evict**. "Unhost" nghĩa hẹp: xóa bid khỏi ui[_more] + sync + notify; teardown view do caller, không UI API nào trong 85B8.

## 2. sub_7764C — FULL body (7764C.c:9, __int64 (a1=snapshot array, a2=bidFilter/nil))
- a1 NSArray<NSDictionary{pid:NSNumber, path:NSString, bid:NSString}> (:51,64-69); a2 NSString filter hoặc nil/0 (25FE0:51 truyền 0): rỗng/nil = match mọi bid, else bid==filter (:76-78). Không input gen/state/frontmost/sleeping/pane.
- **Không check main-thread** (không isMainThread trong file; ngược 25FE0:78 có). **Gating SpringBoard-only**: once 1646A8/12E728 (:41-42); byte_1646A1==1 else return -1 (:43,107,111); 771D4:20 byte = [bundleIdentifier==com.apple.springboard]. Ngoài SB → -1.
- **Không check gen** (không cpuiGen/162E60). **pid+path liveness**: v17=intValue, >=2 && proc_pidpath>=1 (:80); strcmp(buffer, UTF8 path) (:83); khớp → v23++ (:85-87). pid<2 skip. **proc_pidpath read-only probe** (sau đó chỉ strcmp+counter, không kill; grep kill chỉ match proc_pidpath :81). **Không check state/processState/frontmost/sleeping/pane_unload/noreap** (không có các selectors như 25FE0:88-143 hay 7792C).
- Return v20 (:115): counter khi 1646A1==1 else -1 (0xFFFFFFFF) (:107/111). 0 = không live khớp (rỗng/pid<2/fail/mismatch/sai type); >0 = số live khớp; -1 = UNKNOWN/non-SB (không đếm). Callers ép (unsigned int) dùng boolean: !=0 truthy (25C4C:66, 25FE0:51, 26FE4:114) → **-1 cũng truthy ngoài SB** (fail-closed? hay bug — UNKNOWN intent).
- Side-effects: **không** (retain/release + stack buffer; không prefs/globals/kill/UI/notify).

## 3. Callers (5 điểm gọi thực)
- **20010:84** 85B8(v8): onCarPlayUIStatus, cpuiOk==false && cpuiGen+1==currentGen, dedup per-gen (:69-83); v8 = userInfo["cpuiBid"] (:40). Không 7764C/kill.
- **25C4C:66** 7764C(*(a1+56),v9): evict continuation (caller duy nhất 2410C), duyệt bids (*(a1+40)), v9 từng bid (:46-59); snapshot nguồn UNKNOWN (cần producer 2410C). Truthy → nhánh evict.
- **25C4C:84** 85B8(v9): sau clear flags (:68-82). Chuỗi 85B8+7764C → 2565C present+onHosted (present/onHosted ngoài đoạn đọc — HYPOTHESIS phần sau; :123-125 chỉ completion/connected).
- **25C4C:113** 7764C(*(a1+56),...) bỏ kết quả (a2!=0, duyệt *(a1+72), :94-113): vì pure → no-op quan sát được (tàn dư debug? giữ ấm cache? compiler giữ? — UNKNOWN).
- **25FE0:51** 7764C(*(a1+32),0): gen==163980 (:49) → any-live check; truthy → retry 25EDC (:60-67); else nhánh SBApplicationController/processState/pid (:75-199). Không 85B8.
- **26FE4:114 + :152** cặp 7764C→85B8 (chain khác, caller 208F4): guard active/split/visible/connected (:84-87); đk (:108-114) giống mẫu 25C4C; evict di chuyển slot index (:121-150) rồi 85B8 (:152); sau đó rebuild slots/panes + geometry + 234A0/23AB0/9424 + 4D0F4("split.cpui-in-place") (:161-259, unhost+rehost in-place, trigger 202D0 HYPOTHESIS vì không đọc 202D0).
- Headers khớp grep: 85B8 callers 20010/25C4C/26FE4; 7764C callers 25C4C/25FE0/26FE4. Không caller ẩn trong decompile/.

## 4. Verdict kill-vs-unhost
- **85B8: KHÔNG kill. Chỉ unhost/prefs (logical evict).** FULL body + callees + grep. Tác động: xóa bid khỏi ui[_more] + sync + 74C8 regenerate/notify.
- **7764C: KHÔNG kill. Chỉ probe liveness, không unhost/prefs.** proc_pidpath → strcmp → counter. Return count/-1.
- Kill thật ở nơi khác (763E0:247, 7792C:321 — grep) nhưng **không gọi từ 2 helpers** (callees không chứa). Nhánh evict 25C4C/26FE4 = **unhost mềm có điều kiện liveness**; kill đồng bộ (nếu có) do 2410C→763E0 hoặc chain 7792C.
- Tàn dư: 7764C truthy cả khi -1 (non-SB); 25C4C:113 pure-call bỏ kết quả; 85B8 no-op khi bid==main&&∉list / bid empty; snapshot *(a1+56/32/88) cùng nguồn? UNKNOWN (cần producers).
