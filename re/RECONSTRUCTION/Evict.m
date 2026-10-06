// RECONSTRUCTION/Evict.m — APPROXIMATION synthesis (session-045)
// Sources: EVIDENCE/evict_helpers.md (F-036: 85B8 + 7764C FULL + 5 call-sites) +
//   EVIDENCE/evict_from_phone.md (F-037: 3AE48/3AE50 FULL + callers + verdict).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: 3 hệ thống evict RIÊNG BIỆT (prefs-logical / probe-readonly /
//   Home-transition — không kill), kill thật chỉ ở 7792C/763E0 (cross-ref),
//   guards thứ tự (noevict → skipfrontmost → workspace), watchdog exactly-once,
//   truthy-cả--1 tàn dư, pure-call bỏ-kết-quả tàn dư.

#import "DuoDashShared.h"
// Callers: 20010 (cpui-status), 25C4C (evict continuation ← 2410C), 25FE0 (gen-retry),
//   26FE4 (in-place ← 208F4), 3CC44:312 (skipEvict-gated evictFromPhone),
//   3B2D8:189/211 (evict-rồi-host / fire-and-forget).
// Kill paths: Tweak.x §kill (763E0 verify+kill(9), 7792C reaper) — cross-ref,
//   KHÔNG bodies ở đây. Trình bày verdicts cuối file.

// ---- 85B8(bid) prefs-only logical evict (85B8.c:9-47 FULL) ----
static void DDEvictPrefs(NSString *bid) {
    // Guards: empty → no-op (:22); bid==main && ∉list → no-op (:31-33 inverted-check).
    // Đọc: 7044("appbridge_split_carplay_ui") → main (:24); 70FC() → merged [main+more]
    //   (7E730 merge dedup trừ main, :30-32).
    // Nhánh: v6(bid!=main) → v8=@"" (clear main) else giữ main (:35-38);
    //   mutableCopy − removeObject:bid (duy nhất :40) → 84D8(v8,v9) (:39-41).
    // 84D8: length?copy:empty + 7E730 re-normalize + SetAppValue(ui)+SetAppValue(more)+
    //   AppSynchronize + 74C8() → writeToFile plist + post resolved (lan truyền SB — consumer HYPOTHESIS).
    // KHÔNG kill/unhost/process: callees toàn objc/CF (grep kill chỉ match removeObject:).
    // "Unhost" nghĩa hẹp: xóa bid khỏi ui[_more] + sync + notify; teardown view do caller.
}

// ---- 7764C(snapshot,filter) liveness probe read-only (7764C.c:9-116 FULL) ----
static long long DDProbeLive(NSArray *snapshot, NSString *bidFilter) {
    // Input: NSArray<NSDictionary{pid:NSNumber, path:NSString, bid:NSString}>;
    //   filter rỗng/nil = match mọi bid, else bid==filter (:76-78).
    // Gating SpringBoard-only: once 1646A8/12E728 + byte_1646A1==1 else return -1
    //   (771D4: bundleIdentifier==com.apple.springboard); ngoài SB → -1.
    // pid+path liveness: intValue>=2 && proc_pidpath>=1 → strcmp(buffer,path) →
    //   khớp → counter++ (:80-87). pid<2 skip. Read-only (sau probe chỉ strcmp+counter).
    // Return: counter khi SB-gated else -1 (0xFFFFFFFF). 0 = không live khớp;
    //   >0 = số live khớp; -1 = UNKNOWN/non-SB.
    // TÀN DƯ: callers ép unsigned + check !=0 truthy → -1 cũng truthy ngoài SB
    //   (fail-closed? bug? — UNKNOWN intent). Không check main-thread/gen/state/
    //   frontmost/sleeping/pane_unload/noreap. Không side-effect (retain/release + stack buf).
    return 0; // APPROXIMATION returns
}

// ---- 3AE48 evictFromPhone wrapper (3AE48.c:9-11) ----
static void DDEvictFromPhone(void) {
    // 1 dòng: evictFromPhoneThen:nil (fire-and-forget, a3=0 → luôn v20=0, không gắn SB block).
    // Không kill/unhost/notify/prefs/globals/files.
}

// ---- 3AE50 evictFromPhoneThen: Home-transition (3AE50.c:9-186 FULL) ----
static void DDEvictFromPhoneThen(void /* completion nullable, exactly-once via 3F088 */) {
    // Bước 1: fileExists duodash_ab_noevict → LABEL_2 (gọi completion ngay, không evict).
    // Bước 2: file evict_skipfrontmost tồn tại → 3EDFC(163D30[0]) bid slot0 có phải
    //   frontmost phone (SB _accessibilityFrontMostApplication, rỗng→nil) → frontmost → LABEL_2.
    // Bước 3: getClass SBMainWorkspace + SBHomeScreenEntity (nil → LABEL_2);
    //   sharedInstance; phải responds createRequestWithOptions: VÀ executeTransitionRequest:.
    // Bước 4: createRequestWithOptions:0 + entity + modifyApplicationContext: block 3F100
    //   (chỉ setActivatingEntity:entity). Không entity → nullptr, vẫn tiếp tục.
    // Bước 5 (chỉ khi completion!=nil): chọn selector theo CF<1946.102 ?
    //   setCompletionBlock:/addCompletionHandler: (đảo); thử cả 2 via respondsToSelector;
    //   gắn được → 3F164 wrap + watchdog 2s after-main 3F170 (guard 1-lần, chống double-call).
    // Bước 6: executeTransitionRequest: — HÀNH ĐỘNG DUY NHẤT: yêu cầu SB về Home
    //   (app phone-side background gián tiếp, không SIGKILL). v20==0 → completion ngay.
    // KHÔNG: kill/pid/signal/proc_pidpath; DDz/spike/cnab/dismiss/removeFromSuperview;
    //   notify_post; CFPrefs; ghi prefs/globals/files (chỉ đọc 2 flags).
    // Callers: 3CC44:312 (!skipEvict && split_evict → rồi scheduleGeometryPushes),
    //   3B2D8:189 (evict-rồi-host + placeholder đen + completion 3EF20 gen-check →
    //   cnabBuildSceneHostForBid + handshake), 3B2D8:211 (fire-and-forget sau buildSceneHost ok).
}

// ---- Caller matrix (5 điểm gọi thực 85B8/7764C) ----
// 20010:84 85B8(cpuiBid) — cpuiOk==false && gen+1==current, dedup per-gen. Không 7764C/kill.
// 25C4C:66 7764C(snapshot,bid) truthy → nhánh evict; :84 85B8 sau clear flags;
//   :113 7764C bỏ kết quả (pure-call — tàn dư debug? UNKNOWN).
// 25FE0:51 7764C(snapshot,0) any-live → retry 25EDC else SBApplicationController/processState path.
// 26FE4:114+152 cặp 7764C→85B8 (guard active/split/visible/connected) → di chuyển slot index →
//   rebuild slots/panes + geometry + 9424 + 4D0F4("split.cpui-in-place").

// ---- Verdicts (3 hệ thống riêng biệt — KHÔNG lẫn) ----
// 85B8: KHÔNG kill — prefs logical evict (xóa bid khỏi ui[_more] + sync + regenerate/notify).
// 7764C: KHÔNG kill/không unhost — probe read-only (count/-1).
// evictFromPhone: KHÔNG kill — SB Home-transition (guards noevict/skipfrontmost + watchdog 2s).
// Kill thật: 763E0 (verify proc_pidpath + kill(9) đồng bộ) + 7792C reaper
//   (pane_unload/noreap/sleeping gates → list → map → proc_pidpath+strcmp+kill(9)) — cross-ref Tweak.x.
// Nhánh evict 25C4C/26FE4 = unhost mềm có điều kiện liveness; kill đồng bộ (nếu có)
//   do 2410C→763E0 hoặc chain 7792C.
