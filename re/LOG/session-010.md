# LOG/session-010.md
_Date: 2026-10-05. Tiếp tục từ STATE session-009, không artifact mới, git HEAD 29afcf5 clean._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/LOG-009 + `git log/status` (HEAD 29afcf5, tree sạch). Xác định: evictFromPhone + Tweak.x bodies + AA-validators (theo LOG-009 "Tiếp theo").
2. 2 subagents song song: (A) evictFromPhone FULL (3AE48 12 dòng + 3AE50 187 dòng + helpers + grep callers 14 matches) — verdict Home-transition không kill + 2 callers (3CC44 gate, 3B2D8 ×2) + đối lập 7792C/85B8; (B) AA9FC/AAAD0 FULL (30 dòng mỗi cái) + A7E04 + A761C/A78B8/A7D54/A7338 — verdict finite-mask + llround + A7E04 đính chính unrefuse (SAI persist) + đích refused.plist.
3. Persist: `EVIDENCE/evict_from_phone.md`, `EVIDENCE/aa_validators.md`; cập nhật FINDINGS (+F-037/F-038), BEHAVIOR (+B-27/B-28), OPEN_QUESTIONS (Q-10/Q-11 thu hẹp).
4. Tweak.x bodies: present/commit/ack path + kill 3-hệ-thống (F-035..F-038).
5. Checkpoint: commit + STATE/TODO/LOG session-010.

## Evidence / quyết định
- evictFromPhone = SB transition về Home (không kill/prefs/views) — mảnh skipEvict cuối CLOSED.
- A7E04 đính chính hypothesis persist SAI → conditional-unrefuse; đích refused.plist format dict nonce.
- AAAD0 không strict-int (1.6→2), không whitelist/overflow-check — range-check (nếu có) ở caller A9840.

## File thay đổi
- Mới: EVIDENCE/evict_from_phone.md, EVIDENCE/aa_validators.md, LOG/session-010.md.
- Sửa: FINDINGS (+F-037/F-038), BEHAVIOR (+B-27/B-28), OPEN_QUESTIONS (Q-10/Q-11), RECONSTRUCTION/Tweak.x, STATE.

## Chưa làm
- Q-11 tàn dư: DDz3 buildKitLevel + bodies, DDz4, a3 codes 0-4, 162E60 setter, snapshot nguồn.
- Q-10 tàn dư: mapping số v4, 16 strings whitelist, threshold 46340→4008, MITM.
- Q-12 blocks, Q-13 schedulers, Q-14 runtime, Q-09 entitlements, Q-03 blocked, dynamic verify.

## Tiếp theo (session-011, nếu có)
1. DDz3 bodies trọng tâm: commitSlotBids/resolveSlotBids/commitPick (5F8A4/5F224/5F538) — picker→host bridge.
2. 162E60 setter trace (cpuiGen nguồn) — grep gán.
3. Đóng project static: FINAL verdict + ARCHITECTUREiót cập nhật + tag.
