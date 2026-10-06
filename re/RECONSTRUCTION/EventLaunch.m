// RECONSTRUCTION/EventLaunch.m — APPROXIMATION synthesis (session-042)
// Source: EVIDENCE/spawn_teardown_kb.md §A item 9 (F-032; subagent đọc FULL C37C
//   324 dòng, 3 tầng, mỗi claim có file:line).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: base fast-path, cached-validator shortcut, noeventlaunch gate,
//   DB-vs-CAR introspect, 9 fail reasons + no_launch_route ack, success → BFF4 retry 30.

#import "DuoDashShared.h"
// Caller: 9D64 base-rect chain (C2A4 nil → C37C fallback, 9D64:480 — cross-ref
//   functions/9D64.md B06-B10). Routing/predicates: SpawnLaunch.m (D4C4/D01C/BFF4/
//   BE34/C2A4/CB08). Teardown: SpawnTeardown.m. Acks via 986C (caller-side).
// KHÔNG ở đây (R-030): BEE4/B768/B144 + CCEC/D684 + poll §C (365D4/371AC/370F8).

// ---- C37C(bid,gen,rect) event-launch DB/CAR rồi BFF4 (C37C.c) ----
static void DDLaunchEvent(NSString *bid, unsigned long long gen /* +rect */) {
    // Tier 0 — base fast-path: BE34(bid) → BFF4(bid,gen,0,rect) (:61,321).
    // Tier 1 — cached validator: F654 + 1439C, 145F8(env,bid) true →
    //   163530=copy + BFF4(bid,gen,30,rect) (:63-72).
    // Tier 2 — heavy event, gate file `noeventlaunch` VẮNG mới chạy (:79):
    //   introspect DBApplicationLaunchInfo/DBEvent vs CARApplicationLaunchInfo/CAREvent,
    //   ivar _application/_activationSettings, mode 0..3, validate signatures,
    //   build F4B0/F9B8 + 14744/14820 → launchInfo → event(4) → handleEvent: (:81-271).
    //   (Class OS cụ thể HYPOTHESIS — DB vs CAR theo OS; flow CONFIRMED.)
    // v25==1 → 163530=copy + BFF4(bid,gen,30,rect) (:305-311);
    //   fail → B9A8(0) + 986C(gen,bid,0,"no_launch_route") + reason chi tiết
    //   (:144-299,313-317). Reason taxonomy (9):
    //   unknown_launch_info / shape / no_environment / handleEvent_shape /
    //   no_launch_info / no_event / no_app_info / not_this_os / knob.
    // (F654/1439C/145F8/F4B0/F9B8/14744/14820/v25/knob-which giữ UNKNOWN.)
}
