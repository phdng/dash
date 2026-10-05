// RECONSTRUCTION/KeyinputRelay.m — APPROXIMATION synthesis (session-023)
// Source: EVIDENCE/keyinput_relay.md (dylib-side; KeyApp nội bộ = HYPOTHESIS session-001).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên, không suy đoán.
// Semantics phải giữ: guards thứ tự, post-conditions notify, budgets, secure-bypass.

// ---- Đăng ký (EVIDENCE §0) ----
// SB-side 27E20 (once 163CB0): 8 Darwin observer=nullptr/Coalesce —
//   begin→37978, type→3798C, end→379A0, kbframe→379B4, kbshown→379C8,
//   othertap→379DC, kblost→379F0, retap→37A04 (27E20.c:392-447);
//   sau đó 30BA0() + 30F48(0) + post dismiss (:448-450).
// UIApp-side 4CBDC (env DUODASH_AB_UIAPP_IPC_HOOKED): KeyProbeObserver 163F68;
//   4 Darwin observer=163F68/Coalesce — apply→4CF3C, dismiss→4CFBC,
//   card→4D03C, fallback→4D050; + NSNotification WillShow/Hide→onKbShow:/onKbHide:,
//   DidEndEditing→onEndEditing: (body onKbShow/onKbHide UNKNOWN).

// ---- 8 stub SB-side: fire-and-forget hop (EVIDENCE §1.1) ----
static void DDKeyStubToMain(void *block_stru_12D7Fx /* 8 blocks, bodies UNKNOWN */) {
    // Mỗi stub: dispatch_async(main, block) — không payload, không condition.
    // Xử lý sau hop UNKNOWN (thunks 4D064→4C59C, 4D068→4C650: HYPOTHESIS linkage).
}

// ---- UIApp handlers (EVIDENCE §1.2) ----
static void DDOnApplyNotify(id observer /*163F68*/) {
    // 4CF3C: build block {4D0AC, ctx 1461F8, retain observer} → async main (4CF3C:15-21)
    // 4D0AC: [observer onApply:0] — luôn nil arg (4D0AC:11).
}
static void DDOnDismissNotify(id observer) { /* 4CFBC→4D0A0→[observer onDismiss:0] */ }
// card→4D03C→async 12DCA8 (UNKNOWN); fallback→4D050→async 12DCC8 (UNKNOWN).

// ---- Purge + card state (EVIDENCE §1.3-1.4) ----
static void DDKeyPurge(void) {
    // 30BA0: 163CA0 non-empty → xóa per-bid duodash_keyinput.plist + _in.plist
    //   (via 31080=containerDir(bid)/tmp/+name, 31120=removeItem error:0);
    //   LUÔN xóa /var/tmp/seed.plist + out.plist.
}
static void DDKeyCardSet(uint64_t on) {
    // 30F48(on): lazy register_check(card,&162EF4) nếu -1; ok → set_state+post card;
    //   fail → -1, không set/post. UIApp đọc via 4C59C:27.
}

// ---- Focus intercept + publish, phía UIApp trong pane (EVIDENCE §2.4) ----
static void DDFieldDidFocus(id field /*firstResponder*/) {
    // 4B90C gates theo thứ tự (fail bất kỳ → passthrough native + return):
    //   --163054; 163ED9==0 → passthrough; 162F88==0 (keypane off) → clear + passthrough;
    //   knob nokeypane (453B8, TTL 1s) → bypass; đã focus (weak==field) → passthrough;
    //   cooldown (now < 164138) → passthrough; !CNABUIApp.isSplit → passthrough;
    //   session đủ → post retap + --162F58.
    if (!DDFieldIsSecurable(field)) { /* 4BF44 restore + orig, return — PASSWORD BYPASS (§4) */ return; }
    // store weak 163F30 + class 163F38; 164130==1 + responds setInputView: →
    //   gán dummy 163F40 (chặn native keyboard); gọi orig;
    //   163F58==1 + weak → snapshot 163F48 + DDPublishField(field) + post begin +
    //   after 1.5s 4C44C + async 4C4FC (bodies UNKNOWN).
}
static void DDPublishField(id field) {
    // 4C000: gate 45568 (secure → return); path = NSTemporaryDirectory()/duodash_keyinput.plist
    //   (rỗng → return); đọc text/keyboardType/returnKeyType (respondsTo guard);
    //   dict {bid||"", text||"", selLoc=len, selLen=0, kbType, returnKey, secure=@NO CỨNG, ts} →
    //   serialize(200) + write 536870913 + chmod off_154400. Serialize fail → nuốt.
}

// ---- Seed writers, phía SB (EVIDENCE §2.1-2.2) ----
static int DDRebuildSeed(NSString *why /*log*/) {
    // 37CBC: 163CA0 rỗng → teardown; ưu tiên seed.plist, fallback per-bid plist;
    //   merge out.plist (out.text NSString && out.ts >= seed.ts → dùng out.text);
    //   chỉ ghi nếu 38240!=0 && bid non-empty:
    //   dict {text||"", selLoc, selLen=0, kbType||0, returnKey||0, ts=now} →
    //   3896C → seed.plist; success → post keyinput.seed.
    //   Trước đó 30C2C teardown + 38240 dựng card. Return = 38240 result.
    // 3A588 (pane-side, generation check): quét hostedSlotBids; per-bid ts window
    //   0<=now-ts<=10.0s (KHÔNG phải 30s); giữ ts lớn nhất; secure==1 → return (bypass);
    //   38240 ok → bid→163CA0, ++163D18, 163D20=80 → dict 6-entry → seed.plist + post seed.
    return 0; // APPROXIMATION returns
}

// ---- Apply path: SB forward + UIApp patch (EVIDENCE §2.3 + §2.5) ----
static void DDForwardOutToIn(void) {
    // 3A2E0: 163CA0 rỗng → return; đọc out.plist (nil/text sai type → return);
    //   {text, ret||0, ts=now} → per-bid tmp/duodash_keyinput_in.plist →
    //   post keyinput.apply + --163D20 nếu >=1.
    // 4CF3C (observer apply) → async main 4D0AC → [probe onApply:0] →
    // 44B1C: gates 163ED9&&163F58; đọc in.plist (nil/non-dict → return);
    //   text NSString bắt buộc; ret||0; --162F58; weak nil/không-45568 → return (bypass lần 2);
    //   diff prefix + deleteBackward/insertText HOẶC setText: +
    //   EditingChanged/TextDidChange notifications; snapshot; ret==1 →
    //   textFieldShouldReturn: HOẶC insertText:@"\n" (UITextView/field).
}

// ---- Dismiss/fallback/teardown (EVIDENCE §2.7) ----
static void DDDismissSB(NSString *why) {
    // 30AC4: main → purge + clear bid + (từng có bid → post dismiss) + 30C2C;
    //   background → async 30B98 (UNKNOWN).
    // 30960: main + (card||bid) → ++163CA8 + 30AC4 (toast OFF cũng teardown).
    // 37C48 fallback: ++163CA8 + purge + clear bid + (từng có → post fallback) + 30C2C.
    //   Kích hoạt: lost-twice / rebuild-failed (37A7C + watchdog 37A18 ≥3s, tôn trọng nokprecover).
    // 30C2C teardown: hop main; clear cards/sizes/flags; ++163CE8; 30F48(0); animate/30FB8 (UNKNOWN chi tiết).
    // 38240 dựng card: từ chối nếu card có (return 1) / 162DDC!=1 / file nokeypane (return 0);
    //   aux scene duodashkey + containers + overlays + 39260 + after 1.5s + 30F48(1).
    // UIApp: 4C650 (clear + post end có điều kiện + cooldown + restore + re-become);
    //   4D068→4C650(reason,0) không post; 49778 luôn post end + restore; 449C8 teardown khi tắt switch.
    // Posts: end (45180/49778/4C650), othertap throttled 0.3s (48924), retap/begin (4B90C).
}

// ---- Password bypass (§4): gate duy nhất isSecureTextEntry via 45568 ----
// 45568(a1): nil→NO (fail-closed); !responds→YES; isSecure==1→NO.
// Enforces: focus 4B90C (native kb) / publish 4C000 (không ghi) / apply 44B1C (không patch).
// SB-side 3A588 đọc plist["secure"] (dự phòng writer ngoài; dylib luôn ghi NO).
// Secure field KHÔNG BAO GIỜ vào relay. (Grep password literal: 0 hit.)

// ---- keypane_enabled=0 (§5) ----
// Đọc SB 8058: YES→1 else (missing→ON); lưu 162DDC. Push+toast 29400: OFF → 30960 teardown+dismiss;
//   active → push {keypane_enabled,bundleIdentifier} per-bid via 8C28 (Darwin keypane.changed→29400).
// Nhận UIApp onKeyPaneSwitch:/onState: (default 1) → 448B4: ON → clear cooldown; OFF → clear session + 449C8.
// Hệ quả OFF: focus passthrough + knob nokeypane độc lập + 38240 từ chối + teardown/resign.

// ---- KeyApp side: HYPOTHESIS (EVIDENCE §3b, không verify binary) ----
// KeyApp observe seed → đọc seed.plist → hiện keyboard → ghi kb.plist/out.plist +
//   post kbshown/kbframe/type. Dylib chỉ xác nhận nửa đọc (đăng ký notifies, đọc plists).
// CẢNH BÁO: window 10s (3A588) và 600s (38CE8) là hằng dylib; ts<30s là HYPOTHESIS.

// ---- Swizzle _UIKeyboardLayerHostView: KHÔNG thuộc relay (§1.6) ----
// 372CC installer (once 163C48, class-nil skip, 9C190 ×3). 37398/374C4 ép center/frame
//   về target 376DC (chỉ khi card-active + màn ngoài + bounds hợp lệ; budget 162EF0,
//   tolerance 0.25pt) rồi gọi ORIG. 375B8 gọi ORIG trước rồi re-center. (Ghi chú, không implement ở đây.)
