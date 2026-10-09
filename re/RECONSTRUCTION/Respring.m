// RECONSTRUCTION/Respring.m — APPROXIMATION synthesis (session-036)
// Sources: F-023 (80574/8097C/96D60), B-14 (latch/respring chain),
//   EVIDENCE/notify_matrix.md §B (latch.reset + respring.request/ack rows),
//   EVIDENCE/toggle_matrix.md §B (norespring/respring_soft/ab_norespring/no_msrv_restart).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: guard thứ tự (reenable → wipe → post; norespring → throttle
//   → carsleep → 9C790 → ack → delayed-execute), throttle 8/60s, delay 21.6s,
//   ack flag, kill-switch files.

#import "DuoDashShared.h"
// Registrar: 7F14C (latch.reset → 80574; respring.request → 8097C, Immediate) +
//   96D2C (respring.ack → 96D60). Wiring-fed notifies đã liệt kê ở DataRouter.m
//   (không duplicate registrar ở đây).
// Cross-refs (không duplicate bodies): CrashReporting.m (collecting-file lifecycle
//   + latch.reset unlink), CarSleeper.m (carsleep gate trong 8097C).

// ---- latch.reset → 80574 (7F14C.c:121-127) ----
static void DDOnLatchReset(void) {
    // Guard: chỉ chạy khi `duodash_reenable_tweaks` tồn tại/khác-false
    //   (notify_matrix row; đọc flag exact UNKNOWN — cross-ref F-023).
    //   Guard fail → no-op (không wipe, không post).
    // Body khi guard pass:
    //   unlink /var/mobile/Library/DuoDash/*.plist (glob loạt — danh sách exact UNKNOWN);
    //   + flag=false (which flag UNKNOWN — cross-ref F-023);
    //   + unlink crashreport_collecting
    //     (/var/mobile/Library/DuoDash/crashreport_collecting — cross-ref CrashReporting.m);
    //   + 9DEEC("Idle") status;
    //   + Post Darwin "com.sensetechlab.respring.request" (notify_post — kích 8097C).
}

double DDRespringCooldownSecondsForJailbreakPrefixCString(const char *prefix) {
    return prefix && prefix[0] ? 60.0 : 8.0;
}

BOOL DDRespringCooldownAllowsElapsed(double elapsedSeconds, const char *prefix) {
    double threshold = DDRespringCooldownSecondsForJailbreakPrefixCString(prefix);
    return elapsedSeconds < 0.0 || elapsedSeconds >= threshold;
}

// ---- respring.request → 8097C (7F14C.c:129-135) ----
static void DDOnRespringRequest(void) {
    // Guard 1 — kill-switch file: `duodash_norespring` tồn tại (stat!=0) → return,
    //   không respring (toggle_matrix 8097C:28; còn `duodash_ab_norespring` prefix-variant
    //   cùng call-site 8097C:28 — cả hai đều gate).
    // Guard 2 — throttle (exact pure core promoted in session-290): rootful/null-or-empty
    //   jailbreak prefix uses 8s; nonempty/rootless prefix uses 60s. Missing timestamp is
    //   represented by elapsed<0 and passes; otherwise require elapsed>=threshold.
    //   Pass → touch `respring_last` (đường dẫn dir exact UNKNOWN — API_MAP chỉ liệt
    //   kê `respring_*` dưới Library/DuoDash).
    // Guard 3 — carsleep: latch "carsleep" on (9C530-path — cross-ref CarSleeper.m) → return.
    // Guard 4 — 9C790(...) !=0 → return (điều kiện exact UNKNOWN — cross-ref F-023).
    // Body khi mọi guard pass:
    //   Post Darwin "com.sensetechlab.respring.ack" (→ 96D60 set byte_164B4E=1);
    //   + dispatch_after 21.6s block 12FC70 (queue exact UNKNOWN);
    //   + thực hiện respring: 811B0/81624 HOẶC async 812F4/81304/81344
    //     (phân nhánh exact UNKNOWN — notify_matrix row giữ cả hai).
    //   `respring_soft` (9DB88:24) + `duodash_no_msrv_restart` (81344:56) là stat-gated
    //     sub-paths của nhánh thực hiện (exact mapping UNKNOWN).
}

// ---- respring.ack → 96D60 (96D2C.c:14-20) ----
static void DDOnRespringAck(void) {
    // byte_164B4E = 1 (ack flag, observer unk_164B58).
    // Không post tiếp, không prefs-write (theo notify_matrix row).
}

// ---- Toggles liên quan (toggle_matrix §B, không bake thêm behavior) ----
// duodash_reenable_tweaks: guard latch.reset (có mới wipe+post).
// duodash_norespring / duodash_ab_norespring (8097C:28): có file → KHÔNG respring.
// respring_soft (9DB88:24): stat-gated respring path (exact UNKNOWN).
// duodash_no_msrv_restart (81344:56): không restart mediaserverd trong nhánh async.
