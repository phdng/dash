// RECONSTRUCTION/CNABConn.m — APPROXIMATION synthesis (session-054)
// Source: EVIDENCE/cnab_observers.md §§0,4-6 (F-026/Q-11; 229FC/22A8C/227E4/99D4 FULL +
//   fabric 887C/8D78 + inventory). §§1-3,7 ngoài scope (FULL records hiện có).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: disconnect reason-strings, active-gated teardown,
//   carWin registry + pid-change throttle-map clear, nudger knobs,
//   fabric add-vs-post phân biệt, không kill trực tiếp.

#import "DuoDashShared.h"
// Đăng ký: CarPlay side 163EC.c:131-136 (CarPlayObserver.new + 887C host.state→onHostState:,
//   carwindow→onCarWindow:); SB side 27E20.c:283-311 (SBObserver.new + 887C host.request→
//   onHostRequest:, .split→onHostRequestSplit:, cpui.status→onCarPlayUIStatus: +
//   NSNotification CarPlayIsConnectedDidChange→onCarPlayConnChanged:,
//   UIScreenDidDisconnect→onScreenDisconnect: + carPlayPollTick).
// Fabric: 887C = NSDistributedNotificationCenter addObserver (887C.c+8900.c);
//   8D78 = postNotification deliverImmediately:=1. 5 notify appbridge.* = NSDistributed +
//   userInfo NSDictionary (HYPOTHESIS cross-process SB↔CarPlay, entitlement chưa đọc).
// Records hiện có (cross-ref, không duplicate): 1FB5C/202D0/20010/9D64 (FULL),
//   208F4/217EC/218D8 (HostSplit.m + functions/218D8.md), 22AD0 poll (PollFlush.m).

// ---- onCarPlayConnChanged: (229FC.c:9, 27 dòng) ----
static void DDOnCarPlayConnChanged(void /* NSNotification */) {
    // userInfo["CarPlayIsConnectedDidChange_IsConnected"]→bool (:15-18);
    //   true → 7BCBC("...") (gated logger 164710/164709) else
    //   cnabDoCarPlayDisconnect:"..." (:20-26, reason string exact UNKNOWN).
    // void, không transform/globals.
}

// ---- onScreenDisconnect: (22A8C.c:9, 16 dòng) ----
static void DDOnScreenDisconnect(void) {
    // Bỏ qua a3; !DDz1.carPlayConnected → cnabDoCarPlayDisconnect:@"UIScreenDidDisconnect".
    // void, không transform/globals.
}

// ---- cnabDoCarPlayDisconnect: (227E4.c:9, 64 dòng) ----
static void DDDoCarPlayDisconnect(NSString *reason) {
    // reason → 76224 (teardown) + 7B924 log (:21-33); async queue 165118 block 146308
    //   nếu có (:34-35, UNKNOWN body).
    // 163C40>0 → 371F4 else async (:36-44, bodies UNKNOWN).
    // CHỈ khi DDz2.active: dismiss + DDz1 invalidateForDisconnect +
    //   notify_set_state(162DD8,0) + zero xmmword_163A98/AA8/AC0+qword_163AD0 +
    //   notify_post(cpdisconnect) + 4D0F4("CarPlay disconnect") (:45-61).
    // Inactive → chỉ log. Không kill trực tiếp.
}

// ---- onCarWindow: (99D4.c:9, 119 dòng FULL) ----
static void DDOnCarWindow(void /* NSNotification userInfo */) {
    // Input dict else nil (:42-47). Keys: bundleIdentifier (:48), carWinW (:49),
    //   carWinH (:50), carWinPid optional (:51). Gates lồng: bid NSString→W/H
    //   NSNumber→doubles (:52-69); guard length>0 && W,H>=1.0 else return (:71).
    // Lazy NSMutableDictionary 1635B8 (size) + 1635C0 (pid) (:73-88).
    // pid đổi → remove 1635C8[bid] (:89-92; 1635C8 init chưa thấy — HYPOTHESIS
    //   throttle map, nil-safe).
    // Ghi 1635B8[bid]=CGSize (:93-95); pid>=1 → 1635C0[bid]=@(pid) (:96-101).
    // Lookup 13AB8 (lock 163648, đọc 163510/163518) → bool (:102-104);
    //   counter 163640 cap 59. found → 127F0(bid) (:105-106): debounced nudger —
    //   skip nếu /var/tmp/duodash_cpui_nonudge, CACurrentMediaTime>=1635D0[bid]+?,
    //   12C48 rect, 1635D0[bid]=now+4.0, after 1s → 12D84 (127F0.c).
    // Không frame*/cpui*/CFPrefs/post/kill/UI trực tiếp.
}
