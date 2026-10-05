# LOG/session-005.md
_Date: 2026-10-05. Tiếp tục từ STATE session-004, không artifact mới, không git._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/LOG-004/HYPOTHESES + check filesystem (re/ đủ + 4 EVIDENCE). Xác định: P2-2/P2-3/P3-1 (theo LOG-004 "Tiếp theo").
2. 2 subagents song song: (A) P2-2 keyinput relay dylib-side (20+ files: stubs/hop, seed writers, apply, swizzle, teardown, password, keypane-OFF, end-to-end); (B) P2-3 elig cloak + dock/focus/statusbar (8 hook bodies + helpers 1CAF8/114B4/1CA4C/1E770/1C3C8/F83C).
3. Persist: `EVIDENCE/keyinput_relay.md`, `EVIDENCE/elig_cloak.md`; cập nhật FINDINGS (+F-027/F-028, sửa nhầm header F-024), BEHAVIOR (+B-17/B-18, khôi phục body B-16), TODO (P2-2/P2-3 checked), OPEN_QUESTIONS (Q-11 update).
4. Tự làm P3-1: grep 302 hits `duodash_` → ~100 knobs → `EVIDENCE/toggle_matrix.md` (KILL/VALUE/ONESHOT + 4 đảo semantics); check P3-1, dọn HYPOTHESES UNKNOWN.

## Evidence / quyết định
- KeyApp ts<30s bị hạ cấp HYPOTHESIS (dylib chỉ có 10s/600s). 3723C là splash (loại khỏi relay). 8 block SB + 2 block UIApp sau hop UNKNOWN.
- Elig không fake policy số (mutate tại chỗ 0/1/1); icon chỉ DuoDash; displayName "DuoDash"; dock nuốt có debounce, icon-tap không; focus/home luôn forward; use-after-release mặt chữ 1D1D4:53-54 (HYPOTHESIS artifact).
- Toggle matrix: exists=disable là chuẩn, 4 ngoại lệ đảo.

## File thay đổi
- Mới: EVIDENCE/keyinput_relay.md, EVIDENCE/elig_cloak.md, EVIDENCE/toggle_matrix.md, LOG/session-005.md.
- Sửa: FINDINGS (+F-027/F-028), BEHAVIOR (+B-17/B-18), TODO (P2-2/P2-3/P3-1), HYPOTHESES (dọn UNKNOWN), OPEN_QUESTIONS, STATE.

## Chưa làm
- Q-11 còn lại (208F4/218D8/B*/C*/D* callees, onKbShow/onKbHide/onDismiss bodies), Q-10 A9840 schema, Q-12 blocks, P3-4 (siriprobe swallow chi tiết — còn 89764/89880), P3-5 version/device, P4 git/EVIDENCE chuẩn hóa, RECONSTRUCTION bodies.

## Tiếp theo (session-006)
1. P3-4 SiriProbe end-to-end (889D0/88BC8/88C98/88D7C/88E2C/88EA0/88F48 + 894F0/89764/89880 swallow gate + fakepress).
2. P3-5 version/device-specific (4008 availability + A3558 hw.machine + MinimumOS + locale 17).
3. P4-1 git init + commit (nếu được phép) hoặc EVIDENCE chuẩn hóa + RECONSTRUCTION mở rộng.
