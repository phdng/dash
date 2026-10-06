// RECONSTRUCTION/FastRelayout.m — APPROXIMATION synthesis (session-047)
// Source: EVIDENCE/ddz_inventory.md §4 (D684 FULL 626 dòng) + §32 D4C4 trigger (F-034).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: KHÔNG gọi DDz (đính chính premise — 67 callees toàn sub_/objc/CG),
//   fast-vs-slow phân biệt tombstone-set, rect-compare luôn-update-meta,
//   2 họ entity build, fail-telemetry 14 reasons, foreground-request cuối,
//   trigger 3 đường (now/async/telemetry-direct), không chạm DDz state.

#import "DuoDashShared.h"
// Callers: D4C4 (SpawnLaunch.m) + E7DC (CB08-done path — cross-ref SpawnLaunch.m §CB08).
// Lấp UNKNOWN đã ghi: SpawnLaunch.m §D4C4 (D684 body) + SpawnMisc.m §D684-note +
//   functions/9D64.md U05 (rect passing — phần nào: rect là arg a3-a6 của D684).
// KHÔNG ở đây: DDz1/DDz2/DDz3 class synthesis (inventory 251 methods — scope sau).

// ---- D684(a1=bid, a2=gen, a3-a6=rect) fast re-layout (D684.c:9) ----
static void DDFastRelayout(NSString *bid, unsigned long long gen /* +rect */) {
    // FAST PATH (v11=163588[bid] state && v12=163578[bid] VC, :124-128):
    //   so rect cũ (CGRectValue) vs mới (:130-136); LUÔN update rect/gen/posted=NO/since +
    //   xóa nopic/rebinds/bgsince/refg (:138-151); BD18 + E7F4 embed/resize (:152-153);
    //   ECB8 resolve (:154); giống → EE4C re-arm timer (:155-157);
    //   khác → ED5C geometry push + stamp pushed + EE4C + after 50ms block 12D068 (:159-168).
    // SLOW PATH (thiếu một, :171+): VC tồn tại nhưng bid ∈163590 + EEF0(vc)==1 →
    //   remove khỏi set → attach (LABEL_91 :535); else F150(vc,0) + xóa VC khỏi dict (:178-180).
    //   Resolve root VC F3E0 + environment (:184-186), build VC mới 2 họ:
    //   (a) DBApplicationSceneViewController/_CAR... → initWithApplicationInfo:
    //       [proxyApplicationInfo:]environment: + copy statusBarInsets nếu encoding
    //       {UIEdgeInsets=dddd} (:187-341);
    //   (b) DBApplicationViewController + DBDashboard[Proxied]ApplicationSceneEntity
    //       verify method type-encodings (@24/@32) (:385-401) → template-host/
    //       music-service/proxied entity (:439-513).
    //   Fail → FB9C(bid,gen,reason) telemetry (14): no_environment/no_app_info/
    //     no_scene_vc_class/no_initializer/init_returned_nothing/no_application/no_policy/
    //     no_template_host/no_music_ui_service/no_entity/entity_shape/no_root_vc/
    //     no_container/no_foreground/build_failed (:515-530,608,613,619).
    //   Ok → lưu 163578, attach child (addChild nếu parent khác), E7F4 embed, ECB8,
    //     didMoveToParent, state dict 5 keys (rect/gen/posted/since/pushed) →163588,
    //     BD18, add 163598, FC10, foregroundSceneWithSettings:completion: (block FF98) +
    //     ED5C+EE4C, thiếu selector → no_foreground (:532-610).
    // D4C4 trigger: cả 163588+163578 → D684 ngay (:31-39); thiếu → C2A4 lấy appInfo:
    //   có → copy + CB08(...,E7C4,E7DC) async (E7DC caller thứ hai của D684);
    //   không → D684 thẳng để báo no_application/no_environment (:67-70).
    // Side-effects: ghi 163588/163578, add/remove 163590/163598; addChild/didMove;
    //   geometry push + timer + after; foreground request; failure telemetry FB9C.
    //   KHÔNG chạm DDz state (không callee DDz, không đọc 163Cxx/163Dxx DDz).
    // Kiến trúc (HYPOTHESIS, từng cạnh CONFIRMED): D684 là tầng scene-VC thấp hơn;
    //   DDz2 là cầu nối CNAB scene-layer ↔ DDz1 shell (DDz dùng kết quả D684).
}
