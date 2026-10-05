# LOG/session-003.md
_Date: 2026-10-05. Tiếp tục từ STATE session-002, không artifact mới, không git._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/HYPOTHESES/FINDINGS + check filesystem (re/ đủ 12 files + Shared.h). Xác định: P1-3 là P1 duy nhất mở; API_MAP merge là nợ P1-8 (sweep cũ chỉ nằm trong conversation đã mất — vi phạm NEVER LOSE CONTEXT đã rút kinh nghiệm).
2. 2 subagents song song: (A) full 4C34 lines 1-1275 (import/defaults/sleeper/SiriProbe/SB) → báo cáo 8 phần kèm file:line; (B) rebuild notify matrix (12 notifyd + 68 Darwin + 8 NSNotification, mỗi dòng file:line + callback + effect).
3. Persist ngay: `EVIDENCE/4C34_import_defaults.md`, `EVIDENCE/notify_matrix.md`; cập nhật FINDINGS (F-019..F-024), HYPOTHESES (H-003 blocked, dọn UNKNOWN), BEHAVIOR (B-10..B-14), API_MAP (merge + classes mới + network crash fix), TODO (check P1-3/P1-8/P3-2/P3-3), OPEN_QUESTIONS giữ nguyên (đã đúng), STATE.md (sau cùng).

## Evidence / quyết định
- TrueDash = tiền thân, migrate một chiều (6 evidence CONFIRMED); defaults seed đúng 3 keys=false; sleeper daemon đầy đủ; DataRouter pipeline là component mới (7F14C/715C0); latch→respring + BLE pairing flows.
- Không bóc thêm hook mới; Q-11/Q-12 vẫn mở. P2-1 dời sang session sau (hết budget persist).

## File thay đổi
- Mới: EVIDENCE/4C34_import_defaults.md, EVIDENCE/notify_matrix.md, LOG/session-003.md.
- Sửa: FINDINGS/HYPOTHESES/BEHAVIOR/API_MAP/TODO/STATE.

## Chưa làm
- P2-1..P2-4 behavioral models đối chiếu, ObjC bodies (Q-11), opaque stru blocks (Q-12), EVIDENCE pointers/strings trích dẫn chuẩn hóa, TESTS update, RECONSTRUCTION bodies.

## Tiếp theo (session-004)
1. P2-1 prefs resolver + P2-4 split/autostart/disconnect (đọc trực tiếp 74C8-family + tìm disconnect 12s/pane_unload impl).
2. Q-11 bắt đầu: CNABSpringBoardObserver/CNABCarPlayObserver method bodies (1FB5C/20010/208F4/218D8...).
3. TESTS.md update + EVIDENCE chuẩn hóa.
