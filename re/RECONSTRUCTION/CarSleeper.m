// RECONSTRUCTION/CarSleeper.m — APPROXIMATION synthesis (session-028)
// Sources: F-021 + EVIDENCE/4C34_import_defaults.md §8 (daemon init) +
//   EVIDENCE/notify_matrix.md §carsleeper (6 handlers + settings/testunblank).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: guards thứ tự (once/latch/master), priors save/restore,
//   delays, boot_id persist, IOPS source, enable/disable paths.

#import "DuoDashShared.h"
// Records: F-021 (session-003). Daemon name: carsleeper / carsleep (latch).
// Dirs: /var/mobile/Library/CarSleeper/{state.plist, carsleeper.log, suspended_pids.plist}.

// ---- Daemon init (4C34.c:1121-1273; EVIDENCE §8) ----
static void DDCarSleeperInit(void) {
    // Guard once byte_164878 (:1121-1123).
    // 6 Darwin observers (observer=null, Coalesce):
    //   carsleeper/bt-off → 85D8C; /bt-on → 85E20; /cell-off → 85ED4;
    //   /cell-on → 85F08; /airplane-on → 85F28; /airplane-off → 85FA0 (:1124-1166).
    // Nhẹ (chỉ 85FB0/86028/86218 rồi goto LABEL_246) nếu master !=1 hoặc
    //   latch "carsleep" on (:1167-1173).
    // Full daemon khi master==1 && latch off:
    //   RadiosPreferences alloc_init (:1175-1177);
    //   os_log_create("com.sensetechlab.carsleeper", "daemon") (:1178);
    //   mkdir -p /var/mobile/Library/CarSleeper + chmod 0x1FD (509) / 0x180 (384) (:1180-1192);
    //   observers settings.changed → 862DC + carsleep.testunblank → 86334 (:1193-1206);
    //   86338 → byte_16487C/D (:1207-1209);
    //   nhánh 863E8 vs 888B4("autolock_prior",4294966296)+864C4 (:1210-1219);
    //   85FB0/86028/86218 (:1220-1222);
    //   sysctl kern.bootsessionuuid → state.plist {boot_id} via 886CC+885A4 (:1231-1243);
    //   IOPSNotificationCreateRunLoopSource(87D84) + CFRunLoopAddSource (:1247-1255);
    //   nếu 16487C==1 && !87CA0 && !88648 → dispatch_after(8s, main, 130088) (:1256-1268).
}

// ---- Radio handlers: save/restore priors (notify_matrix §carsleeper) ----
static void DDCarSleeperBT(double on) {
    // bt-off (85D8C): BT mgr 87974 — save powered→16487F, setPowered:0/setEnabled:0,
    //   dispatch_after 2.5s block 130288.
    // bt-on (85E20): restore setPowered/Enabled từ 16487F, clear 16487E,
    //   88960(bt_captured/bt_prior/air_prior), dispatch_after 2.5s block 1302A8.
    // (Bodies 85D8C/85E20/87974/88960 chưa tách record — cross-ref notify_matrix.)
}
static void DDCarSleeperCell(double on) {
    // cell-off (85ED4): 879E8(0) → byte_164881 (nhớ prior).
    // cell-on (85F08): nếu 164881 → 879E8(1) (restore khi trước đó on).
}
static void DDCarSleeperAirplane(double on) {
    // airplane-on (85F28): save BT powered→16487F, 87868(1)→byte_164880, 879A0
    //   (airplane on giữ BT snapshot).
    // airplane-off (85FA0): 87868(byte_164880) restore prior.
}

// ---- Enable/disable + test-unblank (notify_matrix) ----
static void DDCarSleepSettingsChanged(void) {
    // 862DC: 86338 → byte_16487C; nếu on && !16487D → 863E8;
    //   nếu off && 16487D → 864C4 + 88648 (fail → 86E80); update byte_16487D.
    // (Bodies 86338/863E8/864C4/88648/86E80 chưa tách record.)
}
static void DDCarSleepTestUnblank(void) {
    // 86334 → thunk 8843C: dispatch_once 1649C8 + off_1649C0(0) + off_1649B0(...,1.0,0)
    //   (force unblank/display wake test).
}
// Liên quan: respring.request pipeline tôn trọng carsleep (8097C check carsleep — F-023);
//   85FB0/86028/86218 init nhẹ (chạy cả khi latch on).
// Kill-switch: latch "carsleep" via 9C530 (file/disabled hoặc notify-latch state) — F-002/F-021.
