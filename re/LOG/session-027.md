# LOG/session-027.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: (A6) Tweak.x SiriProbe bodies (synthesis, bounded). Git HEAD f8985a1 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-026 + git log/status. Scope decision: (A6) — synthesis từ EVIDENCE/siriprobe.md hiện có, không đọc decompile mới.
2. Đọc EVIDENCE/siriprobe.md FULL (62 dòng) rồi viết `RECONSTRUCTION/SiriProbe.m` — bodies: installer (latch+master+dlopen+7 hooks+cache+notifies+counters), gate 894F0, logger 89590 (sink UNKNOWN), swallow 89764 + eligible 89880, 7 hook bodies (ma trận swallow-vs-log), voicecmd cache (891F0/88FD0/890A0), fakepress poster/handler, rescan pipeline.
3. Cập nhật TODO (R-014 done, R-015 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (pure synthesis) → không FINDINGS/BEHAVIOR mới.
- UNKNOWN cũ (sink, opaque blocks, writers, bid==6, encoding) giữ nguyên nhãn.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/SiriProbe.m, LOG/session-027.md.
- Sửa: TODO (R-014), STATE.

## Chưa làm
- R-015 (bodies keyboard/sleeper hoặc records 4C34/163EC...); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: SiriProbe.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-028): R-015 — hoặc Tweak.x bodies tiếp (keyboard hooks từ HOOKS.md 43 hooks? sleeper từ F-021?) hoặc record 4C34 mega-ctor (passes offset 1/350/700/1050/1300 theo phases F-003).
- FILES TO READ NEXT: tùy scope đã chọn.
- EVIDENCE NEEDED: đã đủ trong records/EVIDENCE cho scope synthesis; scope records cần re-read decompile tương ứng.
