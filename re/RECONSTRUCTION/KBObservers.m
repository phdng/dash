// RECONSTRUCTION/KBObservers.m — APPROXIMATION synthesis (session-052)
// Source: EVIDENCE/spawn_teardown_kb.md §B (F-032; onKbShow/onKbHide/onDismiss/
//   onEndEditing + 449C8/453B8 + onApply-bonus 44B1C).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: stubs no-op CONFIRMED (sửa UNKNOWN cũ), onDismiss gated-count,
//   449C8 full-teardown, onEndEditing inverted-knob + double-decrement có-điều-kiện.

#import "DuoDashShared.h"
// Đăng ký: 4CBDC (guard DUODASH_AB_UIAPP_IPC_HOOKED): Darwin apply→4CF3C/dismiss→4CFBC/
//   card→4D03C/fallback→4D050 + NSNotification WillShow/Hide→onKbShow:/onKbHide:,
//   TextField/TextViewDidEndEditing→onEndEditing: (wiring ở KeyinputRelay.m — cross-ref).
// Relay/apply/password/keypane bodies: KeyinputRelay.m (44B1C/454F4/45568/4C000/4B90C).
// SỬA STALE: KeyinputRelay.m "body onKbShow/onKbHide UNKNOWN" → CONFIRMED no-op stubs (dưới).

// ---- onKbShow:/onKbHide: (44AE8.c / 44AEC.c:9-11) — stubs rỗng CONFIRMED ----
static void DDOnKbShowHide(void) {
    // Body `;`, callers/callees none. No-op DÙ ĐÃ ĐĂNG KÝ (không phải UNKNOWN thiếu đọc).
}

// ---- onDismiss: (44AF0.c:11-15) ----
static void DDOnDismissObserver(void) {
    // `if (163ED9==1) { 162F58>=1 → --; 449C8(); }`.
    // (Header callees-none stale — thực tế gọi 449C8.) Không đọc plist/post.
}

// ---- 449C8 full teardown (449C8.c:9-40) ----
static void DDTeardownInput(void) {
    // 163F5A=0,163F59=0,++163F60, clear 163F48 + weak 163F30 + 163F38, 164148=0;
    //   weak responder tồn tại → 164150=1, setInputView:nil+reload (nếu responds),
    //   resignFirstResponder (nếu responds), 164150=0.
    // Đk: 163ED9 + responder tồn tại.
}

// ---- onEndEditing: (45180.c FULL) — teardown có-điều-kiện + post end ----
static void DDOnEndEditing(void /* notification */) {
    // Gate 163ED9 (:22). 162F88==0 → 163F58=0,164130=0, return (:24-28).
    // v4=453B8("nokeypane", TTL 1s cache 453B8:26) (:30); 163F58=164130=v4^1 (:31-32);
    // v4==1 (knob tồn tại) → return, KHÔNG teardown (:33-85, LOGIC ĐẢO).
    // Knob vắng: notification.object vs weak 163F30 — nil/khác → v8=0;
    //   bằng + 163F59!=1 → v8=1; bằng + 163F59==1 → 163F59=0, --162F58, v8=0 (:35-84).
    // Chung: 162F58>=1 → -- (:46-47); v8==1 → clear setInputView+reload (nếu responds),
    //   clear weak, 163F5A=0, ++163F60, và CHỈ khi 163F58==1 → post keyinput.end +
    //   --162F58 lần nữa (:50-73).
    // Posts cousin (cross-ref KeyinputRelay.m): end (45180/49778/4C650).
}
