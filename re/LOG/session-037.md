# LOG/session-037.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: spikeHostSlots synthesis (COVERAGE P2 GAP #6, chia nhỏ — chỉ spike internals). Git HEAD 922c5ff clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-036 + git log/status. Scope decision: SpikeHosting.m (bounded — spike_hostslots.md 41 dòng, 4 funcs; hostSplit/switchInPlace + spawn/teardown để dành R-025).
2. Re-read spike_hostslots.md FULL + grep spike/skipEvict cross-refs (PresentCommitAck/Tweak.x/2565C) rồi viết `RECONSTRUCTION/SpikeHosting.m` — bodies: 3CC44 (skipEvict 1-use 3CC44:311 + slots 0..3 + error-path dismiss+cpdisconnect + IPC-FS + globals), 3BBF0 (CPUI tag-7020 / SB entity-VC chain 3 degrade reasons / empty-bid placeholder), 3C1F0 (unhost-không-kill + placeholder), 3D4FC (delays off_154160 + captures gen/size/orient/bid), debug note.
3. Cập nhật TODO (R-024 done, R-025 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- evictFromPhone nội bộ, 3DC38 downstream, off_154160 delays nội dung, 162F08 nghĩa, spike-return-count HYPOTHESIS giữ UNKNOWN.
- Ghi rõ sửa giả thiết cũ "forward nguyên vẹn" (skipEvict không forward vào hàm con).
- Caller cross-ref PresentCommitAck.m + functions/2565C.md; hostSplit/spawn cross-ref hosting_engine/spawn_teardown (R-025).
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/SpikeHosting.m, LOG/session-037.md.
- Sửa: TODO (R-024), STATE.

## Chưa làm
- R-025 (hostSplit/switchInPlace + spawn/teardown records? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: SpikeHosting.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-038): R-025 — hostSplit/switchInPlace records (EVIDENCE/hosting_engine.md: 218D8/217EC/208F4) HOẶC spawn/teardown callees (EVIDENCE/spawn_teardown_kb.md: 17 callees) HOẶC scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope (EVIDENCE hiện có đủ cho cả hai).
- EVIDENCE NEEDED: đã đủ; không cần re-read decompile cho 2 options này.
