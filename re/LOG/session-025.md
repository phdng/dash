# LOG/session-025.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: (A4) Tweak.x license bodies (synthesis, bounded). Git HEAD 0bf4616 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-024 + git log/status. Scope decision: (A4) — synthesis từ license evidence hiện có, không đọc decompile mới.
2. Đọc EVIDENCE/aa_validators.md FULL (27 dòng) + F-006/B-06/B-09/F-016/F-030 (đọc lại sections) rồi viết `RECONSTRUCTION/License.m` — bodies: ECDSA verify contract + codes, validators exact (finite-mask + llround traps), 4 clients (timeouts/payloads/verdicts), unrefuse exact (đính chính persist SAI), 4C34 license branch (import/reseal/delete/keep), prefs-UI cross-ref.
3. Cập nhật TODO (R-012 done, R-013 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (pure synthesis) → không FINDINGS/BEHAVIOR mới.
- F-041-style errata cũ (A7E04 persist SAI) được bake vào bodies.
- A7D54→A7E04 chain + refused.plist format giữ exact.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/License.m, LOG/session-025.md.
- Sửa: TODO (R-012), STATE.

## Chưa làm
- R-013 (bodies tiếp hoặc records 4C34/163EC...); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: License.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-026): R-013 — hoặc Tweak.x bodies tiếp (carplay-cloak từ EVIDENCE/elig_cloak.md? siriperf/sleeper?) hoặc record 4C34 mega-ctor (passes offset 1/350/700/1050/1300 theo phases F-003).
- FILES TO READ NEXT: tùy scope đã chọn.
- EVIDENCE NEEDED: đã đủ trong records/EVIDENCE cho scope synthesis; scope records cần re-read decompile tương ứng.
