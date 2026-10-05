// RECONSTRUCTION/PresentCommitAck.m — APPROXIMATION synthesis (session-022)
// Source: FUNCTION records 202D0 + 218D8 + 2410C + 2565C (+9424 exact dict).
// KHÔNG compile ở đây (không toolchain iOS). Mọi nhánh có nguồn record; UNKNOWN giữ nguyên.
// Semantics phải giữ: gen-guards, queue hops, sync/async boundaries, orig call-through,
// retain/release balance (MRC, như original), silent-drop paths.

#import "DuoDashShared.h"
// Records: functions/{202D0,218D8,2410C,2565C}.md

// ---- 202D0: onHostRequestSplit: (record 202D0.md B01-B08) ----
static void DDOnHostRequestSplit(id self, SEL _cmd, NSNotification *note) {
    if (dword_162E70 >= 1) dword_162E70--;                    // B01 (consumer UNKNOWN)
    NSDictionary *ui1 = note.userInfo ?: @{};                // B02 (double-read!)
    // Frame decode 27670(ui1) -> cache 163998/9A0/9A8/9B0 (mapping U02)
    NSDictionary *ui2 = note.userInfo ?: @{};
    NSString *L = ui2[@"bundleIdL"] ?: @"";
    NSString *R = ui2[@"bundleIdR"] ?: @"";
    NSString *C = ui2[@"bundleIdC"] ?: @"";
    BOOL activate = [ui2[@"activate"] boolValue];             // nil->NO
    BOOL skipEvict = [ui2[@"skipEvict"] boolValue];           // v69
    BOOL envOnly = [ui2[@"envOnly"] boolValue];              // v70
    // NOTE: `layout` key vắng mặt có chủ ý (CONFIRMED absent).
    DDz2 *host = [DDz2 shared]; DDz1 *shell = [DDz1 shared];
    NSArray *hosted = [host hostedSlotBids];
    if (hosted.count == 0)                                   // B03 fallback
        hosted = @[[host hostedBundleId] ?: @"",
                   [host hostedBundleId2] ?: @""];
    if (!activate) {                                         // B08 deactivate
        qword_163980++;
        if ([[NSFileManager defaultManager] fileExistsAtPath:@"/var/tmp/duodash_ab_split_deactivate_dismiss"])
            [host dismiss];                                  // conditional
        [shell hide];                                        // unconditional
        sub_4D0F4("split.deactivate");
        sub_76224(/* v61 = 4D0F4 return, semantics UNKNOWN U04 */);
        return;
    }
    // ACTIVATE (v52 = ++gen)
    long long gen = ++qword_163980;                          // B04
    if (envOnly) {                                           // B05 short-circuit
        NSArray *try3 = @[L, R, C];
        BOOL done = [self switchCarPlayUIInPlace:try3 gen:gen]; // (record riêng — Q-11)
        if (done) return;                                    // SKIP host block
    }
    // Reapdelay read/trim/clamp (0,60] else 0.0 — B06
    double delay = DDReadReapDelay();                        // /var/tmp/duodash_ab_reapdelay
    NSArray *slots3 = @[L, R, C];
    // onHosted block: captures (delay, copy old bids) — body 279F4:
    //   dispatch_after(delay) { if (gen-still-current) 7792C(old,new) } (cross-ref hosting_engine §4)
    [self hostSlots:slots3 skipEvict:skipEvict onHosted:^(NSArray *doneBids) {
        // 279F4/27AE4 gen-guard → 7792C(old,new) reap/kill (pane_unload gates)
    }];
    // Delayed verify: captures gen — body 27AC8: gen-guard → 792C4 (nav-hide)
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(delay * NSEC_PER_SEC)),
                   dispatch_get_main_queue(), ^{
        // sub_27AC8 exact body: cross-ref hosting_engine §4 (record riêng)
    });
}

// ---- 218D8: hostSlots:skipEvict:onHosted: (record 218D8.md B01-B14) ----
static void DDHostSlots(id self, NSArray *bids, BOOL skipEvict, id onHosted /*766F6467*/) {
    // B01 slot-count/layout match (73E8 gọi 2 lần: 1 dùng + 1 bỏ)
    // B02 dirty loop per-slot (3DD4C normalize + isEqual + size>=1)
    // B03 display/pane flags + CPUI loop (22D64/22E40; flag bits UNKNOWN U02)
    // B04 7-way OR → full-host vs reshow
    // FULL-HOST: carPlayUsableBounds → B05 no-display (97A0 + return) →
    //   23D94 → B06 degenerate (97A0 + conditional discard, FALLTHROUGH) →
    //   reset globals → B07 nopanepad → B08 files (panepad clamp (0,40]/13.0/layout 1..8/panefracs a,b/paneratio 1..99 + noratio) →
    //   365D4("panel.host",0) → B11 geometry-log gate (163AC0 + ABAEC dedup → ABB7C async) →
    //   gen pair (++163980/163978) → build 2410C block (captures DDz2/DDz1/onHosted/geometry/skipEvict/splash/"host") →
    //   A8424 dispatch (queue 165118 hoặc sync fallback)
    // RESHOW: hostedOrientation + per-slot 89D8 (skip CPUI-flagged) + 70248 +
    //   234A0/23AB0 + 162E60++ + 9424(1,...) + touch + 4D0F4("host.request.split.reshow")
    // (Chi tiết operands trong functions/218D8.md — body này chỉ wiring.)
}

// ---- 2410C: async host-execution (record 2410C.md B01-B14) ----
static void DDHostExecute(void *blk /*captures*/, void *answer, long long verdict, long long gen /*a4*/) {
    if (qword_163978 == gen) qword_163978 = 0;
    if (qword_163980 != gen) return;                         // B01 stale silent-drop (no else)
    if (!answer || verdict) {                                // B02 refused
        // B03 license map (A4450 → expired/not_activated/invalid; a3==2 → no_internet trừ bit) +
        // B04 refused-notice flow + B05 notice.state (mkdir 0x1ED + write atomic UTF-8 + chmod 0x1A4)
        // + 97A0→8D78 refused ack. a3 codes U01.
        return;
    }
    // HOST (:379+):
    NSArray *oldBids = [DDz2.shared hostedSlotBids] ?: @[]; // active? else []
    NSArray *oldCPUI = [DDz2.shared hostedSlotIsCarPlayUI] ?: @[];
    if (DDz2.shared.active) [DDz2.shared dismiss];           // sync, no delay/guard
    byte_163A02 = 0; word_163A00 = 0;
    if (![DDz1.shared prepareShell]) {                       // B06
        sub_97A0("no-display-postanswer"); return;           // (dismiss ĐÃ xảy ra!)
    }
    // 369E8 + setAppContentFrame: + parse answer → globals (clamps) +
    // build bids/natives (pad, overflow gom-bỏ U03) + 22E40 filter +
    // symmetric-diff (loop indices U02) + build 2565C block + union evict
    BOOL needEvict = (v81.count || qword_163970.count);       // B09 (tên locals theo record)
    if (needEvict) {                                         // B10-B12 evict-delay
        id resolved = sub_77244(v81);                        // null nếu không main/fail → urgency, không abort
        if (v81.count) sub_763E0(v81, "cpui switch (R3)", 0); // a3=0: kill(9) có đk (duy nhất ở đây)
        // tombstone 163970=copy; map 2595C → byref cpuiKilled
        // 25EDC dispatch_after 100ms main (retries a3=20) →
        // 25FE0 (gen + 7764C + pid poll, retry/defer) →
        // 25C4C (clear tombstone; per-bid: đk → clear + 85B8 prefs-evict; +7764C probe) →
        // carPlayConnected? → DDPresentCommit(...) : drop
    } else {
        DDPresentCommit(/* captures, đồng bộ */);            // B09 direct (:850)
    }
    // skipEvict: KHÔNG ức chế gì trong 2410C (forward vào spikeHostSlots: — F-035).
    // onHosted: chỉ success (trong 2565C), delay nếu evict.
}

// ---- 2565C: present-commit (record 2565C.md B01-B10) ----
static void DDPresentCommit(void *ctx /*captures a1*/, NSArray *carPlayUI /*a2*/) {
    DDz2 *host = *(id *)(ctx + 32);
    NSArray *bids = *(id *)(ctx + 40);
    NSArray *natives = *(id *)(ctx + 48);
    DDz1 *shell = *(id *)(ctx + 56);
    long long expected = *(long long *)(ctx + 80);
    BOOL skipEvict = *(unsigned char *)(ctx + 88);
    BOOL splash = *(unsigned char *)(ctx + 89);
    NSArray *v3 = [host spikeHostSlots:bids natives:natives carPlayUI:carPlayUI skipEvict:skipEvict]; // :37-44
    if (v3.count == expected && [shell showLayoutPanes:v3 natives:natives bids:bids]) { // B01
        for (int i = 0; i < 3; i++)                      // B02 (luôn 3 lần, pad/cắt)
            unk_1639D0[i] = (i < expected) ? [natives[i] CGSizeValue] : CGSizeZero;
        qword_1639C0 = expected; dword_1639BC = dword_1639B8;
        sub_7B6D8(bids);
        NSArray *hosted = [[host hostedSlotBids] copy];
        if (splash) [shell showSplashOverSplit];         // B03
    } else {                                             // B05/B06 fail
        if (byte_164508) { /* teardown splash root (setGen+1, removeFromSuperview, nil) */ }
        sub_52338(/* v13, nil-safe? — INFERRED */);
        sub_746C(/* v12=qword_164518 */);
    }
    id bid = sub_23AB0(host);                            // v17
    id cpuiBid = nil, cpuiMore = nil;
    if (/* v11 success */) { /* 234A0(host,&origin,&more) → v20/v21 */ } // B07
    // v22 = byref pid-map; v23 = 162E60++ (monotonic, cả success lẫn fail)
    sub_9424(/* v11, v17, v20, v21, v22, v23, origin/size */); // B08 dict cond (record 2565C B08)
    // NOTE: 9424 tự post host.state trong body (9424.c:102) — cross-ref COMPARISON 2565C
    if (![v20 length]) [v21 count];                      // B09 touch (intent HYPOTHESIS)
    sub_4D0F4("host.request.split");
    id onHosted = *(id *)(ctx + 64);
    if (/* v11 */ && onHosted && /* v10 */) onHosted(/* v10 copy hosted */); // B10 3-layer gate
    // releases (MRC balance — INFERRED từ decompile retains)
    // U01: v13 uninit nếu B05 false (cần verify assembly). U02: v3-nil + expected==0 edge.
}

// ---- 9424 dict (record 2565C.md TRACE 11a-11f; đọc FULL 9424.c) ----
// base {activated=bool, bundleIdentifier=(bid?:empty), sbPid=int(getpid())} count:3 → mutableCopy;
// + cpuiBid/RectX/Y/W/H nếu bid.length; + cpuiMore copy nếu count;
// + cpuiGen ULL nếu (bid||more); + cpuiKilled copy nếu v22.count && (bid||more);
// → 8D78(host.state, dict). (Xem functions/2565C.md B08 — không duplicate ở đây.)
