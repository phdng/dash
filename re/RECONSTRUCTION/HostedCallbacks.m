// RECONSTRUCTION/HostedCallbacks.m — APPROXIMATION synthesis (session-067)
// Source: EVIDENCE/hosting_engine.md §4 (279F4/27AE4/27AC8 + 7792C/792C4 refs).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: capture semantics (delay/old-bids/gen), gen-guards 2 lớp,
//   reap-delay clamp, nav-hide verify conditions, async boundaries.

#import "DuoDashShared.h"
// Callers: 202D0 onHostRequestSplit: (block layouts exact :230-248 — cross-ref
//   functions/202D0.md B07 + PresentCommitAck.m). Reap killer: 7792C (pane_unload/
//   noreap/sleeping gates + proc_pidpath+kill(9) — cross-ref Tweak.x §kill).
// Verify worker: 792C4 (dispatch_once + !nonavhide + !sleeping + 791A4 → async 793F4 →
//   79434 nav-hide verify, else 1646B4++). Gen-guard pattern: 2410C:202-203, 25FE0:49.
// AUDIT VERDICT (session-067): PresentCommitAck.m KHÔNG cần SE/COMPARISON rows riêng —
//   mọi body của nó đã có record rows (SE-202D0-*/218D8-*/2410C-*/2565C-* +
//   COMPARISON 202D0/218D8/2410C/2565C). File này lấp 2 bodies còn thiếu (cross-ref-only trước đây).

// ---- 279F4 onHosted block (202D0:230-237 → 27AE4) ----
static void DDOnHosted(void /* a1=ctx, a2=host-result */) {
    // Captures: *(a1+32)=old-bids snapshot (copy), *(a1+40)=delay double
    //   (reapdelay file trim, 0<delay<=60 else 0.0 — 202D0:198-225).
    // Logic (279F4:22-31): v4=163980 hiện tại → dispatch_after(delay, main,
    //   27AE4{v10=v4, v8=old-bids, v9=a2}). Chỉ schedule, không slots/DDz/IPC đồng bộ.
    // 27AE4 (11-13): result[6]==163980 → 7792C(result[4]=old, result[5]=new)
    //   else no-op (gen-guard). 7792C reap/kill bids thay thế.
}

// ---- 27AC8 delayed-verify block (202D0:239-246 → 792C4) ----
static void DDDelayedVerify(void) {
    // Captures: v65=qword_163980, dispatch_time(v60s), block {27AC8, block[4]=v65}
    //   → dispatch_after(v66, main, block) (:239-246).
    // Body (11-12): *(result+32)==163980 → 792C4() else no-op (gen-guard HYPOTHESIS
    //   khớp 27AE4/2410C:202-203). v60=0 → dispatch_time(0,0) ≈ ngay.
}
