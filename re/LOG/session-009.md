# LOG/session-009.md
_Date: 2026-10-05. Tiếp tục từ STATE session-008, không artifact mới, git HEAD 2e4d345 clean._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/LOG-008 + `git log/status` (HEAD 2e4d345, tree sạch). Xác định: spikeHostSlots: + 85B8/7764C + P4-2 (theo LOG-008 "Tiếp theo").
2. 2 subagents song song: (A) spikeHostSlots: FULL 347 + spikeCreateSlot 226 + degradeSlot 59 + scheduleGeometryPushes 83 — skipEvict truth (1 use duy nhất 3CC44:311), slots create/degrade/push, globals, errors; (B) 85B8 + 7764C FULL + callers grep (9 matches) — verdict kill-vs-unhost (cả hai KHÔNG kill).
3. Persist: `EVIDENCE/spike_hostslots.md`, `EVIDENCE/evict_helpers.md`; cập nhật FINDINGS (+F-035/F-036), BEHAVIOR (+B-25/B-26), OPEN_QUESTIONS (Q-11 update).
4. P4-2 audit: đếm CONFIRMED/file:line mỗi EVIDENCE (kết quả trên) → đánh PARTIAL (claims chính có citations trong FINDINGS; verbatim reports không lưu).
5. Checkpoint: commit + STATE/TODO/LOG session-009.

## Evidence / quyết định
- Sửa giả thiết cũ "skipEvict forward nguyên vẹn" → giữ tại 3CC44, check 1 lần rồi bỏ.
- evictFromPhone nội bộ vẫn UNKNOWN (ngoài 4 file) → Q-11 tàn dư mới.
- 7764C -1 truthy khi ép boolean (fail-closed?/bug UNKNOWN). 25C4C:113 pure-call bỏ kết quả (tàn dư).
- P4-2 không viết lại verbatim (budget) — tiêu chuẩn tối thiểu đạt.

## File thay đổi
- Mới: EVIDENCE/spike_hostslots.md, EVIDENCE/evict_helpers.md, LOG/session-009.md.
- Sửa: FINDINGS (+F-035/F-036), BEHAVIOR (+B-25/B-26), TODO (P4-2), OPEN_QUESTIONS (Q-11), STATE.

## Chưa làm
- Q-11 tàn dư: evictFromPhone, DDz3 bodies/buildKitLevel, DDz4, a3 codes, 162E60 setter, snapshot nguồn.
- Q-10 validators/A7E04/whitelist/MITM, Q-12 blocks, Q-13 schedulers, Q-14 runtime, Q-09 entitlements, Q-03 blocked, Tweak.x bodies mở rộng, dynamic verify.

## Tiếp theo (session-010, nếu có)
1. evictFromPhone (3AE50 FULL + 3AE48) — mảnh skipEvict cuối.
2. Tweak.x bodies: present/commit/ack path (2565C + 9424 + onHosted).
3. AA9FC/AAAD0 validators (Q-10) — nhỏ, đọc nhanh 2 files.
