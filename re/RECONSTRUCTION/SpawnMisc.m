// RECONSTRUCTION/SpawnMisc.m — APPROXIMATION synthesis (session-044)
// Source: EVIDENCE/spawn_teardown_kb.md §A items 1,6,11,17 (F-032; subagent đọc FULL
//   B768/BEE4/CCEC/B144, mỗi claim có file:line). Đóng coverage 17 callees của 9D64.
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: nil-safe lặng lẽ, view-move ngưỡng 0.5, dock-ticker đảo gates,
//   lazy-init idempotent, D684 body UNKNOWN (không bịa).

#import "DuoDashShared.h"
// Caller: 9D64 onHostState: (B768 async :734?/BEE4 already-check/CCEC/D684 fast-path/
//   B144 ticker "host.state" :734 + "host refused" :769 — cross-ref functions/9D64.md).
// Routing/teardown/event/poll: SpawnLaunch.m + SpawnTeardown.m + EventLaunch.m + PollFlush.m.

// ---- B768(a1) notify SB active bid + refresh dock (B768.c) ----
static void DDNotifyActiveBid(void /* a1 block, bid tại a1+32 */) {
    // Lấy sub_15F40() (:21; object ngoài HYPOTHESIS SB/HomeScreen, class UNKNOWN);
    //   responds appHistory → _bundleIdentifierDidBecomeVisible:
    //   previous:@"com.sensetechlab.duodash",0 (:25-36).
    // Chọn bid: a1+32 nếu length>0 else 1634B8/1634C0 (:44-55);
    //   có length + responds → setActiveBundleIdentifier:animated:bid,1 (:57-58);
    //   responds _refreshAppDock → gọi (:59-61).
    // Không post/global trong file. 15F40 nil → chỉ release (:23,65);
    //   thiếu selector → lặng lẽ skip (nil-safe).
}

// ---- BEE4(outFlag*,x,y) kiểm tra/move view (BEE4.c:9) ----
static int DDCheckMoveView(int *outMoved /* +x,y */) {
    // *out=0 nếu non-nil (:24-25). View = 12988() (bỏ FAF0, :26-27);
    //   nil → return nil (:57-60). superview nil → return (:31-35).
    // Có superview: convertPoint:fromView:0 (:36-38); lệch<=0.5 cả 2 →
    //   đúng vị trí, return 1, *out=0 (:41-47);
    //   else setFrame:v11,v13 → return 1, *out=1 (:50-53).
    // (setFrame size có giữ UNKNOWN. Không global/post.)
    return 0; // APPROXIMATION returns
}

// ---- CCEC() lazy-init 7 containers (CCEC.c:9) ----
static void DDEnsureContainers(void) {
    // 163578 Dict, 163580 Array, 163588 Dict, 163590 Set, 163598 Set,
    //   1635A0 Set, 1635A8 Dict — nil thì tạo (:26-74). Idempotent.
    // Gọi từ D4C4/CE5C/9D64.
}

// ---- D684 fast re-layout (body UNKNOWN) ----
static void DDFastRelayout(void) {
    // Gọi từ D4C4 khi 163588[bid] && 163578[bid] (:30-38) và khi C2A4 nil (:69).
    // Body chưa đọc (không có trong evidence) — UNKNOWN toàn bộ, không bịa.
    // (Cross-ref SpawnLaunch.m §D4C4.)
}

// ---- B144(label) dock-hide ticker + timer 1s (B144.c) ----
static void DDDockTicker(NSString *label) {
    // Non-main → async 16398 return (:74-82). LoadWeak 1635D8 window, nil →
    //   161F8() tạo + storeWeak (:84-92). 1635F0!=1 || !window → cancel timer
    //   1635E0 + restore hidden theo 1637D0/1637D1 (:93-95,214-235).
    // Hide CHỈ khi file nodockhide VẮNG + 1635EC>=1 + kill(pid,0)==0||EPERM;
    //   else LABEL_33 không hide (:96-97, điều kiện đảo).
    // Chọn bid: 163528 nếu rect ∩ window.bounds (via 163A0), else quét
    //   163588[*]["rect"] rồi 1635A8[*] (:105-196); nil nếu không khớp.
    // Timer 1635E0 1s (1s, 0x3B9ACA00, 0xEE6B280) + handler 12D0A8 nếu chưa có
    //   (:205-244); bookkeeping 1637D0/1637D1/1637D8 + setHidden:1 nếu visible
    //   (:246-261, hide-semantics HYPOTHESIS).
}
