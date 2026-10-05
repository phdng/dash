# LOG/session-001.md
_Date: 2026-10-05. First session (no prior STATE)._

## Làm gì
1. Session-start protocol: kiểm tra repo (không có STATE/TODO/git; chỉ có Applications/ + Library/), đọc DuoDash.plist/DuoDashPrefs.plist/Info.plists (bplist decode via strings + python logic từ subagents).
2. Inventory: dylib 4016 decompile files (~4018 funcs) + DuoDash.app 25 + DuoDashKey 255; exports/imports/strings/function_index.
3. Tạo `re/{STATE,TODO,FINDINGS,HYPOTHESES,ARCHITECTURE,BEHAVIOR,API_MAP,HOOKS,TESTS,DECISIONS,OPEN_QUESTIONS}.md` + `EVIDENCE/ RECONSTRUCTION/ LOG/`.
4. Launch 3 subagents song song: (a) hooks+entry, (b) prefs/IPC/network, (c) apps+prefs bundle. Tổng hợp vào state.

## Evidence phát hiện
- Filter inject, master enable byte_168D19, mega-ctor 4C34 6-phase, 17 MSHook sites, prefs resolver 74C8 + cache plist, ECDSA P-256 + 4 license endpoints, KeyApp relay seed/kb/out, black launcher app, prefs spec 30 vs 11 items (2 actions missing impl).

## File thay đổi
- Chỉ tạo mới `re/**` (11 md + LOG). Không sửa artifacts, không code.

## Decision
- Static-first, APPROXIMATION labels, P0/P1 trước code; chưa init git.

## Chưa làm
- P0-1..5 (mod_init, AC5FC, 4049C, 12DB98, 164450), P1-1..8 (đọc full 27E20/163EC/4C34/455D0/9E014/license chain), RECONSTRUCTION skeleton.

## Bước tiếp theo
- Theo TODO.md NEXT TASK: dump mod_init + resolve strip-addrs → cập nhật HOOKS.md; đọc full 5 ctor files → BEHAVIOR.md; grep 2 missing actions → FINDINGS.md.
