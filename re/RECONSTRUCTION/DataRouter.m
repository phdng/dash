// RECONSTRUCTION/DataRouter.m — APPROXIMATION synthesis (session-030)
// Source: F-022 + EVIDENCE/notify_matrix.md navprovider/voice section (715C0 ×1, 7F14C ×13).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: duo/true variants, timestamp race, ingest queue, relayed posts,
//   guards, cross-component posts (voicecmd/respring/crash/BLE/mapBg thuộc subsystems khác — cross-ref).

#import "DuoDashShared.h"
// Records: F-022 (session-003). Registrar: 7F14C (17 Darwin notifies) + 715C0 (relayed ingest).

// ---- Registrar (7F14C + 715C0) ----
// 7F14C đăng ký (Immediate trừ update/Coalesce):
//   duodash.navUpdate → 7F5A4; duodash.speedLimit → 7F974; duodash.cameraAlert → 7FBA4;
//   truedash.navUpdate/speedLimit/cameraAlert → cùng 3 handlers (variants TrueDash);
//   navprovider.update → 7FBBC (Coalesce); navprovider.rescan → 7FC04;
//   navprovider.selftest → 7FC4C; voicecmd.rescan → 7FD94;
//   settings.changed → 7FDDC (full reload); + ble.action/latch.reset/respring.request/
//   crashreport.send/mapBgUpdate/mapBgClear (subsystems khác — cross-ref F-023/F-024/B-08).
// 715C0: navprovider.relayed → 71664 (Coalesce, guard !started).

BOOL DDDataRouterIsTrueDashNotification(CFStringRef name) {
    return DDNavProviderIsLegacyTrueDashNotification(name);
}

NSInteger DDDataRouterSourceCode(NSString *source) {
    return DDCameraRelaySourceCode(source);
}

BOOL DDDataRouterProviderPayloadMatches(id payload, NSString *provider) {
    return DDNavProviderPayloadMatchesProvider(payload, provider);
}

// ---- Nav update race: GMaps vs Waze (duo + true variants) ----
static void DDNavUpdate(BOOL isTrueDash) {
    // 7F5A4 (duodash.navUpdate + truedash.navUpdate chung):
    //   83FDC phân biệt duo/true → đọc duodash_nav_data.plist (GMaps) +
    //   duodash_waze_nav.plist (Waze) [true-variant: truedash_waze_nav.plist + cache 164790] →
    //   so timestamp → DataRouter.shared submitNav → 82830(navUpdate.relayed).
    // (Bodies 83FDC/submit/82830 chưa tách record — cross-ref F-022.)
}
static void DDSpeedLimit(BOOL isTrueDash) {
    // 7F974 (duodash.speedLimit + truedash variant):
    //   đọc duodash_waze_data.plist [true: truedash_waze_data.plist + cache 164788] →
    //   submitSpeed{limit,confidence,source,timestamp} +
    //   write /var/tmp/com.sensetechlab.speed.plist + 82830(speedLimit.relayed) + 84040.
}
static void DDCameraAlert(BOOL isTrueDash) {
    // 7FBA4 (duodash.cameraAlert + truedash variant): 83FDC → 84040 passthrough.
    // (84040 body chưa tách record.)
}

// ---- Provider ingest queue (1647C0) ----
static void DDNavProviderIngest(void) {
    // navprovider.update → 7FBBC: dispatch_once 1647F8 + async queue 1647C0 block 12FB10.
    // navprovider.rescan → 7FC04: async queue 1647C0 block 12FB30 (rescan BLE/sources).
    // navprovider.selftest → 7FC4C: async queue 1647C0 block 12FB50.
    // (Block bodies 12FB10/30/50 opaque — cross-ref Q-12.)
    // navprovider.relayed → 71664 (715C0, guard !started): CNABNavData.shared
    //   ingestProvider + publish (ingest relayed nav vào DataRouter).
}

// ---- Voicecmd rescan link (cross-ref SiriProbe.m, không duplicate) ----
static void DDVoiceCmdRescan(void) {
    // voicecmd.rescan → 7FD94: async queue 1647C0 block 12FBD0.
    // (Cặp notifyd voicecmd.changed; rescan pipeline worker 81CE4 + posters —
    //  xem RECONSTRUCTION/SiriProbe.m §rescan. Ở đây chỉ wiring-fed notify.)
}

// ---- Settings full reload (cross-ref, không duplicate bodies) ----
static void DDDataRouterSettingsChanged(void) {
    // settings.changed → 7FDDC: 80E50 + DataRouter.shared reloadSettings +
    //   7FE78/7FF7C/8009C + async 1647C0 block 12FC10 + 7FC94 (full DataRouter+BLE reload).
    // (Bodies 80E50/7FE78/7FF7C/8009C/7FC94 chưa tách record.)
}

// ---- Non-nav notifies cùng registrar (cross-ref subsystems khác, KHÔNG implement ở đây) ----
// ble.action → 80468: Sync prefs + hud_paired ? BLEManager pair : unpair (F-024).
// latch.reset → 80574 → Post(respring.request) (F-023).
// respring.request → 8097C: guards + Post(respring.ack) + delayed thực hiện (F-023).
// crashreport.send → 80C04: spinlock + async gửi report (B-08).
// mapBgUpdate → 80C74: JPEG SOI/EOI check → 97564 + write map_bg.jpg (guard 1647C8).
// mapBgClear → 80E04: ImageUploader sendClear (guard 1647C8).
// navprovider.listchanged → 91DCC (navbubble source-list reload — prefs UI).
