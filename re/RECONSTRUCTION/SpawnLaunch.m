// RECONSTRUCTION/SpawnLaunch.m — APPROXIMATION synthesis (session-040)
// Source: EVIDENCE/spawn_teardown_kb.md §A items 5,7,8,10,12,14
//   (F-032; subagent đọc FULL BE34/BFF4/C2A4/CB08/D01C/D4C4, mỗi claim có file:line).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: router fast-vs-waiter, gate base, dispatcher confine/retry/
//   timeout, predicate hướng-chứa, killed-list knob-gated, waiter 50ms offers,
//   acks via 986C (không post trực tiếp từ helpers).

#import "DuoDashShared.h"
// Caller: 9D64 onHostState: base-rect chain + GC/spawn (call-sites ở functions/9D64.md
//   B06-B13 — không duplicate ở đây). Teardown/evict cluster: SpawnTeardown.m.
// KHÔNG ở đây (R-028): event-launch C37C (heavy, 324 dòng) + BEE4/B768/B144 +
//   CCEC lazy-init (cross-ref) + D684 fast re-layout + confine/env helpers
//   (13220/14C80/14CA0/14E74/14060/14080/15238/E7C4/E7DC — bodies UNKNOWN).

// ---- D4C4(bid,gen,rect) router spawn: fast D684 hay CB08 (D4C4.c) ----
static void DDSpawnRoute(NSString *bid, unsigned long long gen /* +rect via v75 lookup? */) {
    // CCEC() (:29); 163588[bid] && 163578[bid] → D684 fast re-layout (:30-38).
    // Else v15=C2A4(bid) (:42): non-nil → CACurrentMediaTime + CB08(copy,killed,20,
    //   E7C4-check,E7DC-done) (:45-63); nil → D684 (:69). Không notify.
    // (Rect passing: call 2 args nhưng rect lookup v75[bid] trước — exact mechanism
    //  UNKNOWN, cross-ref functions/9D64.md U05. D684 body UNKNOWN.)
}

// ---- D01C(bid,gen,retry,rect) gate base rồi D4C4 hoặc retry (D01C.c) ----
static void DDSpawnGateBase(NSString *bid, unsigned long long gen, int retry /* +rect */) {
    // Gate 1637A0==a2 else no-op (:25). BE34==1: retry<=0 → 986C "is_base_app"
    //   (:29-31); còn retry → after 100ms 14060 (:35-48). Không base → D4C4 ngay (:53).
    // Caller 9D64:621 non-base, 9D64:614 base-fail.
}

// ---- BFF4(bid,gen,retry,rect) dispatcher confine/retry/timeout (BFF4.c:9) ----
static void DDLaunchDispatch(NSString *bid, unsigned long long gen, int retry /* +rect */) {
    // Gate: 163528.length>0 && 1636E8==a2 else return (:41-45, khớp 9D64:394-400).
    // !BE34: retry<=0 → B9A8(0)+986C(gen,bid,0,"launch_timeout") (:49-53);
    //   còn retry → after 100ms 15238 (:55-67).
    // BE34: a3<1 → bỏ qua (:71-74); else FAF0+13220, 13220 nil + 163720<=9 →
    //   ++ + after 100ms 14C80 (:77-101); có env → 14CA0(rect) test confine (:104):
    //   true → 163538=FAF0 + 14E74(bid,gen,30,rect) (:105-111);
    //   false → B9A8(1)+986C "confine_failed" (:115-116).
    // Ghi 163538, post 986C (ack), schedule retry.
}

// ---- BE34(str) predicate "is base app?" (BE34.c:9) ----
static int DDIsBaseApp(NSString *bid) {
    // Rỗng → nil (:35-37). base = 155D8() (bỏ FAF0, :19-20); base rỗng → nil (:22-31);
    //   isEqual → 1 else containsString ([base contains:query], :24-27). Pure, no side-effect.
    // ("base" HYPOTHESIS tên, hướng chứa CONFIRMED.)
}

// ---- C2A4(bid) lookup killed-list + knob deathwait (C2A4.c) ----
static NSArray *DDKilledList(NSString *bid) {
    // Rỗng → nil (:17-20); else 163570[bid] (:18). Trả array iff NSArray + count>0 +
    //   byte_163748==1 + file nodeathwait VẮNG + 14080(bid,array)==0 (:22-26);
    //   else nil (:30-32). Pure predicate. D4C4 + 9D64:451-452 dùng chọn CB08 vs C37C.
    return nil; // APPROXIMATION returns
}

// ---- CB08(bid,array,retries,check,done,startT) waiter retry 50ms (CB08.c:9) ----
static void DDWaitKilled(NSString *bid, NSArray *killed, int retries /* +check/done/blocks */) {
    // check()[2]() ==0 → return (:31). 14080(bid,array)!=0 → done ngay (:33-35).
    // Hết retry → lock 1423C, đọc 163560[bid] (bỏ), done (:39-47);
    //   còn retry → after 50ms 1427C retained (:51-66). Không post trực tiếp.
    // D4C4 gọi 20 retries (D4C4:63); 9D64:473 retry-count UNKNOWN (decompiler cắt args).
    // (14080/1423C/163560/1427C/E7C4/E7DC bodies UNKNOWN.)
}
