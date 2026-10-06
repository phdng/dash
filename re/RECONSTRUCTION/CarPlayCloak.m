// RECONSTRUCTION/CarPlayCloak.m — APPROXIMATION synthesis (session-026)
// Source: EVIDENCE/elig_cloak.md (installer + helpers + 8 hook bodies + dock/focus/statusbar/icon).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên (U-refs).
// Semantics phải giữ: orig-first/call-through mặc định, guards thứ tự, swallow/nuốt có điều kiện,
//   runtime class-patch once, debounce/throttle, knob files runtime vs env guards installer.

#import "DuoDashShared.h"
// Records: EVIDENCE/elig_cloak.md (session-005, subagent FULL reads).

// ---- Installer + helpers (EVIDENCE §0) ----
// Elig group cài tại 163EC:181-295, guard getenv(DUODASH_AB_ELIG_HOOKED).
// Orig-slots: 163858=effectivePolicyForAppDeclaration:; 163860=declarationForAppProxy:;
//   163868=_newApplicationLibrary; 163870=carPlayDeclaration;
//   163878/163880=icon:imageWithInfo: (object/struct variants); 163888/163890=displayName(+ForLocation:).
// dword_162E08 = capability probe DBApplicationController (sharedInstance/appLibrary/
//   applicationWithBundleIdentifier:/_didAdd:/_didRemove: + DBApplicationInfo tồn tại, 163EC:285-295);
//   ==1 mới cho nhánh patch policy.
// Dock/focus/statusbar cài tại 18A7C:17-66, guard DUODASH_AB_DOCK_HOOKED, fallback DB→CAR:
//   1638D0=_dockButtonPressed:; 1638D8=takeWithPriority: (8-arg); 1638E0=homeButtonUp:.
//   Env chỉ set khi cả 3 origs non-nil (18A7C:59-62).
// Icon-tap cài tại 189D0:9-42 trên SBHIconManager: 163790=iconTapped:,
//   1638C8=iconTapped:modifierFlags:; class nil → không hook.
// Helpers: 1CAF8(bid) = length>0 && =="com.sensetechlab.duodash" (first-party hardcoded,
//   không list/plist/CFPrefs/substring); 114B4(bid) = bridged check (enabled[163770] AND
//   contains[163450] − navprovider_selected (nếu 116D4()) − split_carplay_ui (163470/163478));
//   1CA4C = split-member (1CAF8 || ==1634B8/C0/C8; dùng dock/split/focus, không elig/icon);
//   1E770 roster gate (cache 1s: !exists noroster); 1C3C8 master kill-switch
//   (!exists hosting_off → mọi intercept skip → call-through); F83C int-probe
//   (responds ? msgSend : -1).

// ---- A. Eligibility cloak (EVIDENCE §A) ----
// A1. effectivePolicyForAppDeclaration: (17EC4 — KHÔNG fake số):
//   v7 = orig(...) LUÔN TRƯỚC (:34). Cache bridged khi 163770 && bid∈163450
//   (163488[bid]=policy, 163490[bid]=@(launchUsingTemplateUI), chỉ khi F83C>=0).
//   Nhánh patch (v7 && 162E08==1 && (114B4||1CAF8) && 1E770()): 3 probes via F83C
//   (bỏ kết quả — HYPOTHESIS probe/log); v18=1 (không literal policy number).
//   Ép launchUsingTemplateUI=0 (độc lập v18/roster, chỉ cần responds).
//   Ép CarPlay-capable khi v18==1: add 163898 (once) + runtime-add
//   setCarPlaySupported:/setCanDisplayOnCarScreen: ("B") nếu chưa patch + set =1.
//   v7 nil → skip + trả nil. Luôn trả v7 (mutate tại chỗ), không object synth.
// A2. +declarationForAppProxy: (18318): orig trước; non-nil → giữ (không override).
//   Orig nil mới synth: bid (applicationIdentifier nếu responds) + (114B4||1CAF8) →
//   1DB14(bid) else nil. 1DB14: getClass CRCarPlayAppDeclaration (nil→nil);
//   alloc_init + setBundleIdentifier:bid + setSupportsMaps:1 (guarded responds).
//   Fake = {bundle=bid, SupportsMaps=1}. bid nil/empty → nil.
// A3. +_newApplicationLibrary (1842C, không điều kiện bid): v0=orig() → store 163480 →
//   1DBE8(v0) → return v0 (luôn call-through; orig nil → lưu nil + return nil).
//   1DBE8 injector: bridgedApps + "com.sensetechlab.duodash" (luôn add);
//   mỗi bid chưa có applicationInfo → LSApplicationProxy + addApplicationProxy: +
//   ivar _carPlayDeclaration=1DB14(bid); nhánh icon-add via file + notify (thứ tự HYPOTHESIS).
// A4. -carPlayDeclaration (18490): orig trước; non-nil → thắng (kể cả DuoDash).
//   Orig nil + !114B4 && !1CAF8 → nil. Orig nil + bridged/duodash → once add set 1638B8
//   → trả 1DB14(bid-trích via 1D9BC duyệt selector-list).
// A5/A6. icon:imageWithInfo: (185C8 object-variant / 1875C struct-variant CAR):
//   Chỉ xét fake khi 1CAF8 (KHÔNG hỏi 114B4 → bridged giữ icon orig).
//   Synth 1D4F8: size=max(orig,60) else 120 / scale=orig else 2.0 (A5, orig trước);
//   variant 2 fake-first (A6, orig sau khi nil). Nguồn DualAppsIcon.png +
//   UIGraphicsImageRenderer; load-fail → fallback 1D6D4 (glyph UNKNOWN).
// A7/A8. displayName/displayNameForLocation: (18888/18918): 1CAF8 → @"DuoDash"
//   (không gọi orig, bỏ qua location arg); else orig.

// ---- B. Dock/focus/statusbar/icon-tap (chung: !1C3C8 → skip → forward orig) ----
// B1. _dockButtonPressed: (1BB20 — nuốt tap, chuyển/host app):
//   Trích bid (duyệt off_154130 + fallback 14A9C). Khối 162E40-- + reads bỏ (no-op, UNKNOWN).
//   DuoDash (non-split): debounce 1.5s (trong window nuốt không reassert);
//     163610==1 → clear + 19330(0,0); NUỐT (không gọi orig).
//   Split-member (1635F0 && 1CA4C): NUỐT.
//   Bridged: đang split → 1CB48() clear; !1CBA0 + quá 1.5s → 1CC04(bid) host
//     (8DF8(bid,1), 163610=1, 1634B0=copy, stamp; mapcoexist HYPOTHESIS); NUỐT.
//   App khác: 1CCF4 teardown (>0.5s, không noswitchteardown) + 1CE54 warm +
//     forward orig nếu non-nil (nil → nuốt lặng). Call-through CHỈ nhánh này.
// B2. takeWithPriority: (1BF1C — đè focus, KHÔNG nuốt; luôn forward cuối nếu non-nil):
//   Parse (notification-reason? target bid, đang-host/split?, TemplateUIHost?, aggressive-file).
//   Gate 1C3C8. Single-active: skip teardown khi (elapsed<0.5?1:notification-reason) | đúng-app.
//   Single-không-active: skip khi (đúng-app|notification|!split|elapsed<0.5).
//   Teardown khi (aggressive | !TemplateUIHost): split?1C414():1C670().
//   ("giữ focus" là HYPOTHESIS diễn giải; literal là skip-conditions.)
// B3. homeButtonUp: (1C29C — luôn forward orig nếu non-nil, home KHÔNG bị nuốt):
//   Gate 1C3C8 && (single || split). Knob nohomedismiss tồn tại → giữ home (không teardown).
//   Debounce 163850 (writer UNKNOWN): chỉ teardown khi uptime>=. Teardown split?1C414():1C670().
// B4. iconTapped[:modifierFlags:] (1D0E4/1D158, shared 1D1D4; 1=xử lý/nuốt):
//   DuoDash: non-split → clear single + 19330; return 1 (KHÔNG debounce — khác dock).
//   Bridged: split → 1CB48(); !1CBA0 → 1CC04; return 1 (không debounce).
//   App khác: 1CCF4 + 1CE54 + return 0 → caller forward.
//   Lưu ý 1D1D4:53-54 use-after-release mặt chữ (HYPOTHESIS artifact, cần verify asm).
//   Call-through chỉ khi không DuoDash/bridged (+hosting_off) và orig non-nil.
