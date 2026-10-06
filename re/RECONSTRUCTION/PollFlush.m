// RECONSTRUCTION/PollFlush.m — APPROXIMATION synthesis (session-043)
// Source: EVIDENCE/spawn_teardown_kb.md §C (F-032; subagent đọc FULL 22AD0 +
//   365D4/371AC/370F8, mỗi claim có file:line).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: poll connect/disconnect transitions, retry-count labels,
//   probe persist-chỉ-khi-đổi, flush guards (visible/running/nonudgetick),
//   re-arm 3s, main-vs-async flush dispatch.

#import "DuoDashShared.h"
// Cross-refs (không duplicate): 365D4("panel.host",0) call-site ở 218D8:552
//   (functions/218D8.md B11 + PresentCommitAck.m); ble.status.changed consumer
//   (HudBle.m — BLE pair/unpair F-024); cpconnect (notify_matrix).
// KHÔNG ở đây (R-031): BEE4/B768/B144 + CCEC/D684.

// ---- 22AD0 poll tick (22AD0.c:26-109) ----
static void DDPollTick(int connected) {
    // connected → 1652B0 + uptime 1652B8 (:26-30).
    // 162E74!=1 && v3==0 → disconnect "poll" (:32-40);
    //   v3==1 && 162E74!=1 → 163A68=5 + post cpconnect (:44-47).
    // Labels poll.retry/connect/bringup "%@#%d" 6-163A68 (:50-64);
    //   163A68 = 365D4(label,1) ? 0 : -1 (:65-70).
    // 163C40>0 → 371AC (main) else async (:78-92);
    //   v3==1 → 370F8 (main) else async (:95-100).
    // Chốt 162E74=v3 + after 3s 22D5C re-arm (:102-109).
    // (Label strings exact + 163C40 nghĩa UNKNOWN.)
}

// ---- 365D4(label,force) probe resolution + persist + notify (365D4.c:9) ----
static int DDProbeDisplay(NSString *label, int force) {
    // Display 34250() nil → 0 (:40-42,96-97). FBSDisplayConfiguration
    //   initWithCADisplay (pixelSize/scale, fallback bounds/frame, :43-93);
    //   w<1||h<1 → 0 (:94). Clamp xmmword_163AA8>=40 (:101-118);
    //   lưu 163AC0=w/h, 163AD0=scale (:119-121);
    //   format "%.0f × %.0f", bucket 480p/720p/1080p (:122-138).
    // force || !equal(163AD8/AE0) → storeStrong +
    //   SetAppValue(headunit_resolution/video_quality) + Sync +
    //   Post ble.status.changed (:140-159); return h>0 (:129,170).
    // Side-effect duy nhất prefs+notify. Class FBSDisplayConfiguration
    //   CONFIRMED theo string. (Caller thứ hai: 218D8:552 label "panel.host".)
    return 0; // APPROXIMATION returns
}

// ---- 371AC(_) flush dropOverdueNotice (371AC.c:9) ----
static void DDFlushOverdue(void) {
    // [DDz1 shared] → dropOverdueNotice (:13-14).
    // Không plist/post/điều kiện/knob. Gọi tại 22AD0:86-92.
}

// ---- 370F8(_) flush nudgePresent:"tick" có knob (370F8.c:9) ----
static void DDFlushNudgeTick(void) {
    // [DDz1 shared]; visible==0 → return; livePresentRunning==1 → return (:16-18).
    // fileExists nonudgetick → return, vắng → nudgePresent:"tick" (:20-24).
    // Post trong nudgePresent nếu có = UNKNOWN từ file này.
}
