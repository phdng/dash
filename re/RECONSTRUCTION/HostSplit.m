// RECONSTRUCTION/HostSplit.m — APPROXIMATION synthesis (session-038)
// Source: EVIDENCE/hosting_engine.md §§2-3,5-6 (F-031; subagent đọc FULL 217EC 42 dòng
//   + 208F4 624 dòng 2 passes + helpers, mỗi claim có file:line).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: wrapper 2-pane nil-coalesce, guards từ chối sớm,
//   convert-fail rollback-nhưng-return-1, completion async qua 25EDC/25FE0,
//   26FE4 continuation gates, layout-chỉ-so-không-đọc.

#import "DuoDashShared.h"
// Cross-refs (không duplicate bodies): 218D8 full-host/reshow (functions/218D8.md),
//   279F4/27AC8 onHosted + delayed verify (PresentCommitAck.m + functions/202D0.md),
//   spike internals (SpikeHosting.m), evict/kill helpers (F-036/F-037).
// Caller envOnly: 202D0 B05 thử switch-in-place trước, fail (0) mới rơi vào host block
//   (functions/202D0.md:71). onHosted nil từ wrapper (217EC:40) → 2565C skip callback.

// ---- 217EC hostSplitL:right:skipEvict: (217EC.c:10-42) ----
static void DDHostSplit(NSString *L, NSString *R) {
    // Wrapper split 2-pane (HYPOTHESIS): nil-coalesce L/R → @"" (:26-32);
    //   build [L,R] arrayWithObjects:count:2 (:33-37);
    //   gọi hostSlots(...,0) với onHosted=nil (:40).
    // Không slots/evict/DDz/IPC/globals/files/error riêng, không chạm `layout`
    //   (callees chỉ 218D8 + runtime; grep 0 hit).
}

// ---- 208F4 switchCarPlayUIInPlace:gen: (208F4.c:9-14) ----
static BOOL DDSwitchCarPlayUIInPlace(NSArray<NSString *> *bids, unsigned long long gen) {
    // Return 1=đã xử lý/accept (KỂ CẢ rollback một phần), 0=từ chối early/mismatch
    //   (:203-206,240-242,605,623 — return-semantics HYPOTHESIS).
    // Guards từ chối → return 0 (:170-206): !active || !isSplitHosting || !visible ||
    //   swapInFlight || maximizedPosition<0 || maximizeInFlight || 163978!=0 ||
    //   1639B8!=1639BC || 162E90!=73E8() || hostedSlotCount(1..3)!=1639C0 ||
    //   !=BA7C8-map || 1639C8<slotCount || word_162ED8!=0x0100 || byte_162EDA!=2 ||
    //   word_163C18&0x101. Tiếp: bids mới khớp hostedSlotBids + size>=1 (:207-237);
    //   22D64 shell-bounds false → LABEL_109 return 0 (:238).
    //   (`layout` string: chỉ SO 162E90==73E8() — không đọc file trực tiếp.)
    // Phân loại slots (:244-348): v105=22E40 eligible flags (carplay_ui + entitlements
    //   7DBDC + carPlayConnected + !nocpui), v104=hiện CPUI. Loop: obj (!eligible &&
    //   !CPUI → convert); v102 (eligible && !CPUI → HYPOTHESIS replace pane);
    //   v99 (eligible && CPUI && word_163A00[i]==1). v112=bids obj non-empty;
    //   v107=eligible-nonempty (292-348). Index order giữ nguyên (HYPOTHESIS).
    // Convert: mỗi obj → convertSlotToCarPlayUI: fail → rollback
    //   setSlot:carPlayUI:0 đã làm + return 1 (:368-380); ok → 26F60 tạo view +
    //   replacePaneAtSlot:withView:native: (w,h từ unk_1639D0), fail → rollback
    //   (:369-408); ok → addObject + word_163A00[slot]=1 (:409-410). Mỗi v102
    //   tương tự (:431-450). Có thay đổi → rebuildMatForEnvironment (:457-460).
    // Hoàn tất async (:461-605): v100=mutableCopy(v112)+merge v102 (:461-491);
    //   v95=77244(v100) else empty (HYPOTHESIS resolve display items, :492-495);
    //   v72=v95 + 163970 pending cũ dedup + merge v107 (:502-540);
    //   763E0(v100,"cpui switch in place (R3)",0) nếu có (:542-543);
    //   v93=2595C(v72,v83) (killed set? HYPOTHESIS);
    //   block 26FE4 captures (DDz2,DDz1,v81,v82,v80,v83,v112,v72,v97,v93) (:544-573);
    //   v87(v72).count → 163970=copy + 25EDC(v87,gen,20,0,0,0,block) delay 100ms →
    //   25FE0 (25EDC:15,28-41), else gọi block trực tiếp (:574-584).
    // DDz calls: hostedSlotCount/active/isSplitHosting/visible/swapInFlight/
    //   maximizedPosition/maximizeInFlight/hostedSlotBids/hostedSlotIsCarPlayUI/
    //   convertSlotToCarPlayUI:/setSlot:carPlayUI:/replacePaneAtSlot:withView:native:/
    //   rebuildMatForEnvironment/spikeCreateSlot:/scheduleGeometryPushesForSlot:.
    // IPC gián tiếp 26FE4→9424→8D78 + 4D0F4. notify_post/CFPrefs vắng.
    // Không đọc /var/tmp/* (grep duodash_ab_ 0 hit).
    return YES; // APPROXIMATION returns
}

// ---- 26FE4 continuation (208F4.c:544-573, body 26FE4:81-260) ----
static void DDInPlaceContinuation(void) {
    // Clear 163970; yêu cầu active&&split&&visible&&carPlayConnected;
    //   7764C liveness-check; 85B8 evict (prefs logical evict — F-036);
    //   setSlot:carPlayUI:1/0 + spikeCreateSlot: + replacePaneAtSlot: +
    //   scheduleGeometryPushesForSlot: + rebuildMatForEnvironment +
    //   9424(1,...,cpuiGen=162E60++) + 4D0F4("split.cpui-in-place").
    // (Evict ở đây = setSlot + replacePane + 85B8 — HYPOTHESIS.)
}
