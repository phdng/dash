# LOG/session-008.md
_Date: 2026-10-05. Tiếp tục từ STATE session-007, không artifact mới, git HEAD 4cdbce8 clean._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/LOG-007 + `git log/status` (HEAD 4cdbce8, tree sạch). Xác định: 2410C + DDz inventory + STOP verdict (theo LOG-007 "Tiếp theo").
2. 2 subagents song song: (A) 2410C FULL 878 dòng (3 passes) + 2565C FULL + helpers (gen-guard, refused/license-map/notice-state, host parse/globals/diff, evict-delay 2 tầng, skipEvict-forward, onHosted-chỉ-success, 2565C present-commit); (B) DDz1/DDz2/DDz3 inventory (251 methods đếm tay + headers) + 8 methods trung tâm FULL + D684 FULL 626 dòng (đính chính: không gọi DDz) + phân công shell-vs-state + DDz3 clusters.
3. Persist: `EVIDENCE/async_host_2410C.md`, `EVIDENCE/ddz_inventory.md` (rút gọn phụ lục DDz3 153 dòng, ghi rõ range + clusters); cập nhật FINDINGS (+F-033/F-034), BEHAVIOR (+B-23/B-24 + STOP VERDICT), OPEN_QUESTIONS (Q-11 update).
4. Checkpoint: commit + STATE/TODO/LOG session-008.

## Evidence / quyết định
- **Đính chính:** D684 không gọi DDz (tầng scene-VC thấp hơn); 7792C không thuộc chain 2410C (thuộc trigger 202D0); skipEvict không ức chế gì trong 2410C.
- **Bất ngờ:** headers "Called by: none" không đáng tin (vd present gọi 2 methods nhưng headers ghi none); DDz4 tồn tại ngoài phạm vi; DDz3 153 methods không +shared.
- STOP verdict: STATIC COMPLETE, overall INCOMPLETE (dynamic + P0-3 + bodies liệt kê).

## File thay đổi
- Mới: EVIDENCE/async_host_2410C.md, EVIDENCE/ddz_inventory.md, LOG/session-008.md.
- Sửa: FINDINGS (+F-033/F-034), BEHAVIOR (+B-23/B-24 + verdict), OPEN_QUESTIONS (Q-11), STATE.

## Chưa làm
- Q-11 tàn dư: 85B8/7764C, spikeHostSlots: nội bộ, DDz3 bodies/buildKitLevel, DDz4, a3 codes, 162E60 setter.
- Q-10 validators/A7E04/whitelist/MITM, Q-12 blocks, Q-13 schedulers, Q-14 runtime, Q-09 entitlements, Q-03 blocked, P4-2, dynamic verify.

## Tiếp theo (session-009, nếu có)
1. spikeHostSlots: nội bộ (3CC44 FULL) — mảnh hosting cuối cùng đọc được.
2. 85B8 (evict helper) + 7764C (poll check) — đóng kill-vs-unhost.
3. P4-2 EVIDENCE chuẩn hóa + RECONSTRUCTION Tweak.x bodies mở rộng (present/commit/ack).
