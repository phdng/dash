// RECONSTRUCTION/DDzCommit.m — APPROXIMATION synthesis (session-046)
// Source: EVIDENCE/ddz3_commit.md (F-039; subagent đọc FULL 5F044/5F224/5F538/5F74C/5F8A4
//   + helpers + call-sites, mỗi claim có file:line).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: picker→prefs bridge (KHÔNG gọi host trực tiếp),
//   resolve fallbacks + dedup theo layout, commit-vs-giữ-prefs-cũ phân biệt swap,
//   6A13C 3-valued gate, bake-trước-flush, reconcile-CPUI có-điều-kiện + luôn 74C8,
//   why chẩn đoán-không-persist, host nhận gián tiếp qua resolved.

#import "DuoDashShared.h"
// Host handoff: 74C8 → write plist + post resolved (PrefsResolver.m);
//   host thực thi hostSlots từ onHostRequestSplit:/hostSplitL
//   (PresentCommitAck.m + HostSplit.m) — cross-ref, KHÔNG duplicate.
// Helpers: 7044/70FC/7E730/84D8/86A0/8270 (prefsesterday) — semantics ở PrefsResolver.m.
// KHÔNG ở đây: DDz inventory 251 methods (ddz_inventory.md — scope sau); 1FB40/792C4
//   re-host trigger; 17344 debounce chi tiết; buildKitLevel (không liên quan chain).

// ---- Commit chain (tổng quan §0) ----
// onTilePressed: [5EDC4:76-77] → close + commitPick:(cnabBid) → resolveSlotBids [5F538:25] →
//   dedup + validate 6A13C [5F538:40-65] → commitSlotBids:why:("picked %@ for slot %ld") [5F538:67-80] →
//   bakeLiveSwapForCommit:(why) [5F8A4:72] → SetValue left/right/third + Sync [5F8A4:73-94] →
//   CarPlay-UI reconcile 7044/70FC/86A0/84D8 [5F8A4:99-147] → 74C8() → write plist + post resolved.
// SỬA HYPOTHESIS SAI thường gặp: commitSlotBids KHÔNG gọi onHostRequestSplit
//   (onHostRequestSplit là CNABSpringBoardObserver đăng ký CPDistributedMessagingCenter
//   host.request(.split) [27E20:287-291]; hostSplitL→hostSlots [217EC:40]).
// commitSlotBids:why: là biên cuối picker; why chỉ string chẩn đoán → bake, không persist.

// ---- 5F044 resolvePairL:R: (legacy 2-slot, không ai gọi) ----
static void DDResolvePair(NSString **outL, NSString **outR) {
    // Inputs self->_pairL/_pairR. 3 tầng fallback + dedup 2-slot: (1) rỗng → +DDz2 shared
    //   hostedBundleId (L) / hostedBundleId2 (R) (lần duy nhất chạm DDz2; không
    //   DDz1/CNAB/host/notify); (2) vẫn rỗng → 7044("appbridge_split_left"/"right");
    //   (3) dedup: 162E90!=1 && cả hai non-empty && equal → R=@"" (layout-id !=1 cấm trùng — HYPOTHESIS).
    // Ghi out-params (nil→@""), luôn ghi nếu con trỏ non-null. Không prefs/notify/global/error.
    // VAI TRÒ: tàn dư trước slot thứ 3 (pairC) — callers none + grep HYPOTHESIS tương thích.
}

// ---- 5F224 resolveSlotBids (-> NSMutableArray [L,R,C]) ----
static NSArray *DDResolveSlotBids(void) {
    // Inputs duy nhất self->_pairL/_pairR/_pairC. Vòng i=0..2: slot rỗng →
    //   hostedBundleId/2/3 nếu DDz2.shared!=nil; vẫn rỗng → 7044("..._left/right/third");
    //   nil→@"" addObject. Dedup 3-slot: v13=(162E90-1)>7 ? 2 : BA7C8[162E90-1]
    //   (slot-count theo layout); v13<2 → bỏ dedup; loop j=1..v13-1: bids[j] non-empty &&
    //   equal bids[0..j-1] → bids[j]=@"" (chỉ trong phạm vi layout).
    // Gọi DDz2 (+shared, hostedBundleId/2/3). Không DDz1/CNAB/hostSlots/CFPrefs/notify_post.
    // Read-only resolve, không bake/validate. (Header callers thiếu — grep thực 8 sites.)
    return nil; // APPROXIMATION returns
}

// ---- 5F538 commitPick: (caller duy nhất onTilePressed:) ----
static void DDCommitPick(NSString *bid) {
    // Gate picker: cnabBid từ CNABTileControl, length!=0, bid ∈ self->_apps[][bid];
    //   đã lọc long-press/swipe/arrange-exit (time-_arrExitAt>=0.5); close + commit
    //   (picker đóng dù commit thành công hay không).
    // 5 bước: resolveSlotBids → mutableCopy; guard openSlot (âm/vượt count → silent return);
    //   setObject tại openSlot; dedup slot-count layout (trùng bid pane khác →
    //   HỦY COMMIT GIỮ PREFS CŨ — khác commitSwapOfPositions swap tường minh);
    //   validate `!length || 6A13C(v4)` mới commit.
    // 6A13C: ""→0; không SBApplicationController→-1; có class không responds→-1;
    //   app tồn tại→1; nil + Preferences tồn tại→0 else -1. Commit iff clear HOẶC
    //   đã cài (1) HOẶC môi trường lỗi (-1); drop chỉ khi chưa cài mà SB còn sống (0).
    // why 2 bước: "slot %ld" → "picked %@ for %@" → commitSlotBids (đường duy nhất user-pick→host).
    // Error silent, không alert/log. Không DDz1/DDz2/CNAB/host/prefs trực tiếp.
}

// ---- 5F74C bakeLiveSwapForCommit: (why forward/debug, không parse) ----
static void DDBakeLiveSwap(NSString *why) {
    // Guard: chỉ bake khi KHÔNG ở live-swap special-mode (word_162ED8/byte_163AF1...
    //   pattern; ý nghĩa bit UNKNOWN).
    // Nhánh layout==2 (162E90==2): 163AF1==1 && llround(162EB8*100)-1<=0x62 →
    //   SetValue split_ratio NSNumber (integer elided — UNKNOWN giá trị).
    // Nhánh else (163AF3==1): v7/v8=69E20(0/1), 8270(layout,v7,v8) = ghi frac_a/b/layout
    //   (clamp 1..99 else 0) + Sync, layout 2..8 (range HYPOTHESIS).
    // Sau đó nếu không special-mode: 75F38 (tự 752E4 lấy live index → 75E14 reorder;
    //   chỉ reorder khi result 1..3 + not-special — HYPOTHESIS "bake swap drag vào prefs").
    // Không DDz1/DDz2/CNAB/host. Ghi prefs ratio hoặc fracs. Không Sync riêng nhánh ratio.
}

// ---- 5F8A4 commitSlotBids:why: (biên cuối picker) ----
static void DDCommitSlotBids(NSArray *bids, NSString *why) {
    // Guard count<3 → silent drop. Unpack [0]/[1]/[2] nil→@"".
    // Bake trước: bakeLiveSwapForCommit:(why) — geometry/frac bake trước bids flush.
    // Persist: SetValue split_left/right/third + Synchronize.
    // CarPlay-UI reconcile: v34=7044(carplay_ui)?:@""; v18=70FC() merge; v19=86A0
    //   predicate isEqual trên v15 (array 3 bids, chỉ dùng CarPlay test);
    //   v21 = v34.length && v19(v34) ? v34 : @"" (chỉ giữ main nếu đang pick);
    //   v22 = filter v18 qua v19; đổi → 84D8(v21,v22). LUÔN 74C8() dù CarPlay đổi hay không.
    // 74C8: notify_post resolved — tín hiệu duy nhất tới host. Không CPDistributedMessagingCenter
    //   send, không hostSlots call. Callers: 5F538:80 (user-pick) + 571B8:69 (swap).
}

// ---- why strings (chỉ 2 call-sites commitSlotBids; grep corpus) ----
// "picked %@ for slot %ld" (2 bước) — duy nhất user-pick. "gutter re-host swap" — swap path.
// "gutter drag" → bake trực tiếp (không qua commitSlotBids). "layout apply" → bake trực tiếp.
// why không persist (arg → bake → 75F38 bỏ qua; HYPOTHESIS log/debug).

// ---- Đường song song (commitSlotBids KHÔNG phải bottleneck duy nhất) ----
// commitGutterFrac: bake("gutter drag")+resolve+prefs left/right/third+ratio/fracs+74C8.
// commitSwapOfPositions:with:: resolve→mutableCopy swap→notePanesSwapped/geometry→
//   commitSlotBids("gutter re-host swap").
// onLayoutTilePressed:: bake("layout apply")+prefs+Sync trực tiếp, KHÔNG qua commitSlotBids
//   (cuối gọi 746C layout setter — cross-ref PrefsResolver.m).
