# LOG/session-004.md
_Date: 2026-10-05. Tiếp tục từ STATE session-003, không artifact mới, không git._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/LOG-003 + check filesystem (re/ đủ + 2 EVIDENCE). Xác định: P2-1/P2-4 + Q-11 (theo LOG-003 "Tiếp theo"), TESTS update.
2. 2 subagents song song: (A) P2-1+P2-4 — prefs resolver family + split/autostart/disconnect-close/pane_unload (14 keys table, kill SIGKILL, 12s timer, autostart observe-only); (B) Q-11 — 12 methods inventory + 8 bodies FULL (1FB5C/202D0/20010/229FC/22A8C/22AD0/227E4/99D4/9D64) + produce/consume matrix 7 notifies.
3. Persist ngay: `EVIDENCE/prefs_split_autostart.md`, `EVIDENCE/cnab_observers.md`; cập nhật FINDINGS (F-025/F-026), BEHAVIOR (B-15/B-16), TODO (P2-1/P2-4 checked, P2-5 partial), TESTS (rewrite asserts session-002..004 + dynamic list), OPEN_QUESTIONS (Q-11 partial, +Q-13/Q-14), STATE.md (sau cùng).

## Evidence / quyết định
- Kill semantics khóa: cả 2 paths SIGKILL sau verify (không SB terminate). Traps: 85CDC(nil)=1, NSNumber≠CFBoolean, 836C vs 74C8 default khác nhau.
- Hosting protocol NSDistributed + key namespaces tách biệt (frame C→S, rect S→C, carWin riêng); `layout` produce-nhưng-không-đọc là UNKNOWN đáng chú ý.
- Schedulers 1A820/7B9EC/7BD58 UNKNOWN (callers:none) → Q-13. HYPOTHESIS mở gom vào Q-14 + TESTS dynamic.

## File thay đổi
- Mới: EVIDENCE/prefs_split_autostart.md, EVIDENCE/cnab_observers.md, LOG/session-004.md.
- Sửa: FINDINGS (+F-025/F-026), BEHAVIOR (+B-15/B-16), TODO, TESTS (rewrite), OPEN_QUESTIONS, STATE.

## Chưa làm
- P2-2 keyinput relay model, P2-3 elig cloak model (H2 hooks đã map, bodies chưa), Q-11 còn lại (208F4/218D8/B*/C*/D* callees), Q-12 blocks, Q-10 A9840 schema, P3-1 toggle matrix, P3-4/P3-5, P4 git/EVIDENCE chuẩn hóa, RECONSTRUCTION bodies.

## Tiếp theo (session-005)
1. P2-2 keyinput relay (dylib-side 37978~/4CF3C/30BA0/30F48 + đối chiếu KeyApp report session-001).
2. P2-3 elig cloak bodies (17EC4/18318/1842C/18490/185C8/1875C/18888/18918) + dock/focus/statusbar (1BB20/1BF1C/1C29C).
3. P3-1 toggle matrix từ HYPOTHESES list + EVIDENCE grep.
