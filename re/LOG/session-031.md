# LOG/session-031.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: (A10) Tweak.x HUD/BLE bodies (synthesis, bounded). Git HEAD 3b05d88 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-030 + git log/status. Scope decision: (A10) — synthesis từ F-024 + strings scan/prefs/speed/brightness (2 greps mới, không đọc decompile bodies).
2. Grep strings: scan machinery (_beginScan/timeout/peripheral/discoverServices), HUD keys (paired/uuid/sha256/firmware/orientation/brightness/status), speed (source/correction/simspeed/plist/notifies/navbubble), BKS brightness — rồi viết `RECONSTRUCTION/HudBle.m`: pairing flow (CONFIRMED wiring), scan mapping (bodies UNKNOWN), prefs keys, brightness hooks, speed sources/correction/publish.
3. Cập nhật TODO (R-018 done, R-019 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis + strings-grep mới) → không FINDINGS mới (strings hits là evidence search, không phải behavior mới).
- Pairing/scan/bodies phân biệt CONFIRMED-wiring vs UNKNOWN-bodies.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/HudBle.m, LOG/session-031.md.
- Sửa: TODO (R-018), STATE.

## Chưa làm
- R-019 (bodies tiếp hoặc records 4C34/163EC...); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: HudBle.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-032): R-019 — Tweak.x bodies tiếp (còn lại gì? audit RECONSTRUCTION/ vs subsystems) HOẶC record 4C34 mega-ctor (passes offset 1/350/700/1050/1300 theo phases F-003).
- FILES TO READ NEXT: tùy scope đã chọn.
- EVIDENCE NEEDED: đã đủ trong records/EVIDENCE cho scope synthesis; scope records cần re-read decompile tương ứng.
