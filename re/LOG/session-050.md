# LOG/session-050.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: cpuigen lifecycle (nhỏ, bounded — 30-dòng evidence). Git HEAD 29ffd0c clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE + git log/status + re-read cpuigen_trace.md FULL (30 dòng). Scope decision: Cpuigen.m (P4 rows / touch-up 042-045 sau).
2. Viết `RECONSTRUCTION/Cpuigen.m` — lifecycle (BSS-init HYPOTHESIS + post-increment idiom + consume-duy-nhất-9424 + readers/echo + stale-check-duy-nhất) + bảng 5 hits (H1 đọc + H2-H5 ghi + H5 callers maximize).
3. COVERAGE touch-up cpuigen row (EVIDENCE-only → SYNTH). TODO (R-037 done, R-038 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- Init/reset, tên biến phụ trợ, reshow-ngữ-nghĩa giữ UNKNOWN/HYPOTHESIS.
- 20010/9D64 readers + 4 writers + 9424-consume cross-ref records hiện có.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/Cpuigen.m, LOG/session-050.md.
- Sửa: COVERAGE (cpuigen row), TODO (R-037), STATE.

## Chưa làm
- R-038 (P4 rows? touch-up 042-045? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: Cpuigen.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-051): R-038 — chọn 1 trong: P4 SIDE_EFFECTS/COMPARISON rows cho synthesis bodies (meta — audit 2 files trước để định cỡ), COVERAGE touch-up 042-045 (spawn row 039-040→042-044 + Evict row — nhỏ), hoặc scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope (COVERAGE.md rows 28/32 + RECONSTRUCTION/*.m list nếu touch-up; SIDE_EFFECTS/COMPARISON heads nếu P4).
- EVIDENCE NEEDED: đã đủ; 4C34 FULL infeasible + P0-3 blocked giữ nguyên.
