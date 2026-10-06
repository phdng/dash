// RECONSTRUCTION/DDzCore.m — APPROXIMATION synthesis (session-048)
// Source: EVIDENCE/ddz_inventory.md §§0-3,5 (F-034; totals + DDz1/DDz2 method lists +
//   8 central methods FULL + division hypothesis). DDz3 UI clusters (§6) + D684 (§4) ngoài scope.
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: DDz1=shell/view vs DDz2=hosting/state (tinh chỉnh, không tuyệt đối),
//   cross-link bất đối xứng (DDz1→DDz2 5 sites, DDz2→DDz1 1 site),
//   central-method contracts, caller-names giải-từ-address, DDz4 ngoài-phạm-vi.

#import "DuoDashShared.h"
// Bodies đã cover ở files khác (cross-ref, không duplicate): spike chain
//   (SpikeHosting.m: 3CC44/3BBF0/3C1F0/3D4FC), slot-flags/convert (HostSplit.m:
//   setSlot/convertSlot), evict (Evict.m: evictFromPhone/Then), dismiss-dọn-re-host
//   (dưới §dismiss), fast re-layout (FastRelayout.m: D684 — KHÔNG gọi DDz).
// KHÔNG ở đây: DDz3 153 methods UI (EVIDENCE §6 — scope sau); buildKitLevel (asm-only).

// ---- Totals (§0: grep function_index) ----
// ^Function:.*DDz[123] → 251: DDz1=63 (61 instance incl. destruct + 2 class),
//   DDz2=35 (34 + 1 class), DDz3=153 (152 + 0 class).
// strings.txt `DDz` → ZERO hit. classRef DDz1/DDz2/DDz4 trong pointers —
//   DDz4 TỒN TẠI, ngoài phạm vi, UNKNOWN.
// "Called by: none" = không static caller trong export (có thể gọi qua objc_msgSend
//   không resolve) — HYPOTHESIS hạn chế tool, data CONFIRMED.

// ---- DDz1 = shell/view (63 methods: window lifecycle, splash+notice 8, layout, swap/mirror 5, maximize 11) ----
static void DDz1Map(void) {
    // State: rootWindow/backdrop/paneContainer/content/splash/notice/matStrips/exitChip +
    //   _visible/_maxActive/_maxPos/_maxInFlight/_mirroring (getters 29B30/2DDEC/2E800/2E86C + setter 2C2CC:30).
    // Cụm: visible 29B30; carPlayUsableBounds 29BC4; prepareShell 2A0E8; teardownWindow 2A1C4;
    //   showSplashOverSplit 2A300/removeSplash 2A394; nudgePresent: 2A3E0(+AfterShow 2A4D0);
    //   livePresent 2A5C0/2A610/2B194; notices retire/show/discard/remove/drop (2B3B0/2B484/2B5BC/2B6D8/2B738/2B748/2B7B4);
    //   invalidateForDisconnect 2B81C; buildShellIfNeeded 2B8B0; exitChip 2BA34; splitHostView 2BDE0;
    //   setAppContentFrame: 2BE54; installContent: 2BF84; present 2C2CC; dump* ×5 stub rỗng;
    //   showSpike 2C41C; showWithHostView: 2C4F8; layoutGutterStripMatInHost: 2C614;
    //   showSplit/showLayoutPanes/replacePane/rebuildMat 2D074/2D270/2D4F4/2D8A0;
    //   swap/mirror (canSwap/swapInFlight/canMirror/swapPanes/mirrorPanes);
    //   maximize (maximizedPosition/Rect/InFlight/Allowed/Position:animated:/reapply/rollback...).
    // Caller-names giải từ address: 1FB5C/202D0/208F4/218D8/227E4/229FC?/22AD0/22E40/25C4C/26FE4/27C88/297A0 subs.
}

// ---- Central DDz1 methods (FULL reads) ----
static void DDz1Central(void) {
    // +shared (36474): dispatch_once 163C28/12D448, return 163C20 autoreleased.
    //   9 callers tầng điều phối CarPlay. Chỉ trả instance, không init window.
    // +carPlayConnected (3640C): getClass AVExternalDevice nil→NO, else
    //   currentCarPlayExternalDevice non-nil→YES. Stateless. 7 callers poll/guard (cổng HW chung).
    // -showWithHostView: (2C4F8): nil→NO; non-nil: block 33F5C sync main
    //   (buildShellIfNeeded → installContent:hostView → present). Entry show gọn nhất.
    // -present (2C2CC): _rootWindow nil→NO; unhidden + interaction ON + animate 0.25s
    //   (block 34240); _visible=1; weak view front + announce; nudgePresentAfterShow +
    //   startLivePresent. Đối xứng hide (async main, 30624).
}

// ---- DDz2 = hosting/state (35 methods: getters 10, host/spike, aux scene 6, evict 2, dismiss+reset) ----
static void DDz2Map(void) {
    // State: 163D30 bids, 163D48 count, 163D50 flags, 162F08 orient,
    //   163D88/163DC0 active/split, _auxVC/_appVC3.
    // Getters: active 3AADC (=163D88); isSplitHosting 3AE3C (=163DC0); hostedBundleId{,2,3}
    //   3AC04/10/1C; hostedSlotCount 3AC28 (=163D48); hostedSlotBids 3AC34 (snapshot ≤3,
    //   nil→@"", bound 163D48, read-only); hostedSlotIsCarPlayUI 3ACD0; hostedOrientation
    //   3AD80 (=162F08); renderSize 3AAE8; probeSceneForSlot: 3AD8C; aux* (Live/Bid/Size/Orient/Object).
    // Host/spike: spikeHostLeft:...: 3CAA4 (wrapper →spikeHostSlots); spikeHostSlots: 3CC44;
    //   spikeCreateSlot: 3BBF0; degradeSlot: 3C1F0; scheduleGeometryPushes: 3D4FC;
    //   setSlot:carPlayUI: 3D6EC (ghi word_163D50+slot); convertSlotToCarPlayUI: 3D704;
    //   dismiss 3D8A8 (+block 3D990: clear VC ivars, remove+invalidate views, re-89D8 per slot, resetHostingState).
    // Scene/host: hostBundleId:renderSize: 3B2D8 (→evictFromPhoneThen:/cnabPostAppSideHandshake:/
    //   cnabBuildSceneHostForBid:); createAuxSceneForBid:native:orient: 3C368;
    //   teardownAuxScene 3C808 (←resetHostingState, ←3C368); auxSceneLive 3C908.
    // Evict: evictFromPhone 3AE48 (wrapper →Then:nil); evictFromPhoneThen: 3AE50.
    // +shared (3F1B8): once 163D80/12D8F8, return 163D78. 18 callers (7 CNAB/sub +
    //   291F4/29400/30FB8/37A7C/38240/3A588 + 5 DDz1).
    // Chain nội bộ: 3CAA4→3CC44→(3BBF0→3C1F0, 3D4FC, dismiss); 3B2D8→(evict/handshake/build);
    //   3AAF8→3C808; 3D990→3AAF8. dismiss caller duy nhất spikeHostSlots: → dọn trong re-host.
}

// ---- Phân công + cross-links (hypothesis ĐÚNG có tinh chỉnh, §5) ----
// DDz1→DDz2 shared (0x3F1B8) tại 5 sites: retireServerNotice 2B3B0:6, discardHiddenShell
//   2B5BC:6, installContent: 2BF84:6, maximizeAllowed: 2E874:6, maximizeCarPlayUIPosition: 2F754:6
//   (hỏi/guard state trước khi động view — crisp).
// DDz2→DDz1 (0x36474) CHỈ 1 site: spikeCreateSlot 3BBF0:6 (carPlayDisplaySize fallback).
// Kiến trúc (HYPOTHESIS, từng cạnh CONFIRMED): DDz2 là cầu nối CNAB scene-layer ↔
//   DDz1 shell; DDz3 (hàng trăm call-sites tới cả hai) là tầng UI trên cùng điều phối.
