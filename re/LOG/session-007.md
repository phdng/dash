# LOG/session-007.md
_Date: 2026-10-05. Tiếp tục từ STATE session-006, không artifact mới, git HEAD 766f171 clean._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/LOG-006 + `git log/status` (HEAD 766f171, tree sạch). Xác định: Q-11 callees + RECONSTRUCTION + P4-2 (theo LOG-006 "Tiếp theo").
2. 2 subagents song song: (A) Q-11A hosting engine — FULL 218D8 (717 lines) + 208F4 (624) + 217EC + 279F4 + 27AC8 + helpers (dirty-check, full-host vs reshow, 7 knob files, async 2410C/A8424, convert/rollback, continuation 26FE4, reap/kill, nav-hide verify, layout-chỉ-từ-file); (B) Q-11B — 17 spawn/teardown callees FULL (B768→B144) + onKbShow/onKbHide (stub rỗng!) / onDismiss / onEndEditing FULL + poll helpers 365D4/371AC/370F8.
3. Persist: `EVIDENCE/hosting_engine.md`, `EVIDENCE/spawn_teardown_kb.md`; cập nhật FINDINGS (+F-031/F-032), BEHAVIOR (+B-21/B-22), OPEN_QUESTIONS (Q-11 update), TODO (P2-5 done).
4. RECONSTRUCTION mở rộng: `Tweak.x` (init/prefs/IPC/hooks/kill APPROXIMATION từ evidence) + commit session-007.

## Evidence / quyết định
- **Bất ngờ:** onKbShow/onKbHide là stub rỗng (no-op dù đã đăng ký) — keyboard show/hide phía UIApp không xử lý gì.
- 365D4 là headunit resolution probe (ghi prefs + post ble.status.changed), không phải bringup blind-retry.
- skipEvict chỉ ảnh hưởng async 2410C (cơ chế suppress UNKNOWN); `layout` request key không đọc trực tiếp (chỉ file + plist).
- Tweak.x là pseudocode APPROXIMATION có dẫn evidence từng block, không compile (ghi rõ).

## File thay đổi
- Mới: EVIDENCE/hosting_engine.md, EVIDENCE/spawn_teardown_kb.md, RECONSTRUCTION/Tweak.x, LOG/session-007.md.
- Sửa: FINDINGS (+F-031/F-032), BEHAVIOR (+B-21/B-22), TODO (P2-5), OPEN_QUESTIONS (Q-11), STATE.

## Chưa làm
- Q-11 còn lại: 2410C/2565C async bodies, 162E60 setter, D684, DDz1/DDz2 classes, view providers (15F40/12988/FAF0).
- Q-10 (AA-validators, A7E04, whitelist strings, MITM), Q-12 blocks, Q-13 schedulers, Q-14 runtime, P4-2 EVIDENCE chuẩn hóa, Q-09 entitlements, Q-03 blocked, dynamic verify.

## Tiếp theo (session-008)
1. 2410C async body (host thực thi: slots/evict/DDz present) — Q-11 lõi cuối.
2. DDz1/DDz2 class inventory (methods wraparound) + D684.
3. Đánh giá STOP conditions: hook map đủ? init flow? core behavior? unknowns liệt kê? → tuyên bố coverage.
