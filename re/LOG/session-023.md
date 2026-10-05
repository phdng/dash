# LOG/session-023.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: (A2) Tweak.x keyinput relay bodies (synthesis, bounded). Git HEAD b40d3b2 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-022 + git log/status. Scope decision: (A2) — synthesis từ EVIDENCE/keyinput_relay.md hiện có, không đọc decompile mới.
2. Đọc EVIDENCE/keyinput_relay.md FULL (91 dòng) rồi viết `RECONSTRUCTION/KeyinputRelay.m` — bodies: đăng ký 2 phía, stubs hop, handlers apply/dismiss/card/fallback, purge + card-state, focus intercept + publish, seed writers (SB + pane-side), out→in forward + apply-patch, dismiss/fallback/teardown, password bypass, keypane-OFF, KeyApp HYPOTHESIS, swizzle ghi chú loại trừ.
3. Cập nhật TODO (R-010 done, R-011 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (pure synthesis) → không FINDINGS/BEHAVIOR mới.
- KeyApp side + ts<30s + block bodies UNKNOWN giữ nguyên nhãn (không nâng cấp).
- Swizzle tách riêng khỏi relay (ghi chú trong file).
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/KeyinputRelay.m, LOG/session-023.md.
- Sửa: TODO (R-010), STATE.

## Chưa làm
- R-011 (bodies prefs/license hoặc records 4C34/163EC...); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: KeyinputRelay.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-024): R-011 — hoặc Tweak.x prefs/license bodies (từ functions/74C8.md + EVIDENCE license) hoặc record 4C34 mega-ctor (passes offset 1/350/700/1050/1300 theo phases F-003).
- FILES TO READ NEXT: tùy scope đã chọn.
- EVIDENCE NEEDED: đã đủ trong records/EVIDENCE cho scope synthesis; scope records cần re-read decompile tương ứng.
