// RECONSTRUCTION/SpawnTeardown.m — APPROXIMATION synthesis (session-039)
// Source: EVIDENCE/spawn_teardown_kb.md §A items 2-4,13,15-16 (F-032; subagent đọc FULL
//   BBF8/BCDC/BD18/D154/CE5C/B9A8, mỗi claim có file:line).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: conditional-evict theo generation, tombstone a2-gated,
//   abort 2 nhánh, timer-cancel idempotent, size-register guards,
//   teardown-all duyệt snapshot-copy, không post trực tiếp (ack via 986C ở caller).

#import "DuoDashShared.h"
// Caller: 9D64 onHostState: (call-graph + ack semantics ở functions/9D64.md —
//   không duplicate ở đây). Containers 163578/163588/163590 lazy-init CCEC (cross-ref).
// KHÔNG ở đây (R-027): launch-route C37C/BFF4/D01C/D4C4 + predicates BE34/C2A4 +
//   waiter CB08 + BEE4/B768/B144; KB observers §B (cross-ref KeyinputRelay.m);
//   poll/UI-flush §C (365D4/371AC/370F8).

// ---- D154(bid,a2) teardown một bid (D154.c:9) ----
static void DDTeardownBid(NSString *bid, int keepTombstone) {
    // VC=163578[bid], xóa 163588[bid], probe 13AB8 (:39-42).
    // VC + EEF0 + responds backgroundSceneWithCompletion: → copy bid, gọi block
    //   13F90(a2^1, v5&(a2^1)), schedule after 15s 14040 nếu (v5 & ~a2) +
    //   after 15s 1404C nếu ~a2, v14=1 (:45-91); else v14=0 (:94-96).
    // Detach vô điều kiện nếu VC: 10188, willMoveToParent:nil, viewIfLoaded.hidden=0,
    //   removeFromSuperview, removeFromParent (:97-105).
    // a2==1 → 163590 add (GIỮ tombstone, :107-109); else xóa 163590, F150(vc,v14),
    //   xóa 163578[bid], v14==0 && !(v5^1) && !a2 → BBF8(bid,v28) (:111-118).
    // Cuối: 163588.count==0 → 127B4() (:121-122). Không post trực tiếp.
    // (v5/v28 nghĩa exact UNKNOWN; 13AB8/EEF0/13F90/14040/1404C/F150/10188/127B4 bodies UNKNOWN.)
}

// ---- CE5C() teardown toàn cục (CE5C.c:9) ----
static void DDTeardownAll(void) {
    // CCEC() rồi copy allKeys 163588 → D154(key,0) từng key (:33-60);
    //   copy 163590 → D154 từng object (:66-86); removeAllObjects 163590 + 1635A8,
    //   return xóa 1635A8 (:88-89). (Argless; call-site 9D64:727 truyền arg — arg
    //   ignored? UNKNOWN — cross-ref functions/9D64.md U04.)
    // Gọi từ 9D64:727 khi !activated. Duyệt trên snapshot-copy (an toàn mutate).
}

// ---- B9A8(keep) abort/reset bid hiện tại (B9A8.c:9) ----
static void DDAbortCurrent(int keep) {
    // Nhánh 1 (163528 non-empty): giữ bid, ++1636E0, clear 163540/15278/163528/
    //   rect/1636E8/163538/1636F0, v7=BE34 (:30-49). a1 && 163530==bid && v7 →
    //   13AB8+15CBC, copy, after 3s 15DA4 (:50-68, grace delayed-evict HYPOTHESIS);
    //   else BBF8(bid,0) + v7→15A94 (:72-74); clear 163530 + 1636D8=0 (:76-80).
    // Nhánh 2 (163550 non-empty): clear + BCDC + BBF8 + BE34→15A94 (:82-96);
    //   cả hai rỗng → no-op. Không post trực tiếp.
}

// ---- BBF8(key,gen) evict có điều kiện generation (BBF8.c) ----
static void DDEvictKey(NSString *key, unsigned long long gen) {
    // key rỗng → no-op (:18). Lock unk_163648, lookup 163510[key] (:20-24).
    // a2==0 → xóa luôn; !=0 → chỉ xóa khi 163518[key]==a2 (:25-40);
    //   xóa cả 163510/163518 (:38-42). Chỉ ghi dicts, không post/986C.
    // Callers 9D64/B9A8/D154.
}

// ---- BCDC() cancel timer/source 163558 (BCDC.c:9) ----
static void DDCancelTimer(void) {
    // !=0 → dispatch_source_cancel + =0 + release (:13-18); nil → idempotent no-op.
    // Chỉ clear global. Gọi từ B9A8 nhánh 163550 + 9D64:391.
}

// ---- BD18(key,w,h) register size + bump generation (BD18.c:9) ----
static void DDRegisterSize(NSString *key, double w, double h) {
    // Guards length==0 / w<1||h<1 → return (:18,20). Dưới lock: 159FC() ensure (:23);
    //   163510[key]=CGSize value (:28-29); ++163718 (:31);
    //   163518[key]=NSNumber ULL (:32-33, đối số decompiler nuốt — UNKNOWN giá trị gen).
    // Không post.
}

// ---- Ack chung (caller-side, nhắc để giữ wiring) ----
// 986C(gen,bid,ok,why) → 8D78 cpui.status (986C:23-54); why strings:
//   launch_timeout/confine_failed (BFF4), already (9D64:422),
//   no_launch_route (C37C), is_base_app (D01C) — bodies ở R-027.
