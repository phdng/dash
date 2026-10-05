# LOG/session-006.md
_Date: 2026-10-05. Tiếp tục từ STATE session-005, không artifact mới, chưa có git (sẽ init trong session)._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS/LOG-005/HYPOTHESES + check filesystem (re/ đủ + 7 EVIDENCE). Xác định: P3-4/P3-5 + Q-10 (theo LOG-005 "Tiếp theo"), P4-1.
2. 2 subagents song song: (A) P3-4 SiriProbe end-to-end (installer, gate 894F0, logger 89590 sink-UNKNOWN, swallow 89764/89880, 7 bodies, voicecmd cache, fakepress poster duy nhất + handler opaque, rescan pipeline); (B) P3-5 + Q-10 (4008 generic, A3558 đính chính device_hash, ACF1C announce, branch CF duy nhất 3AE50, language 4-tầng + 6 observers, A9840 schema 4 nhánh + keys table + side-effects).
3. Persist: `EVIDENCE/siriprobe.md`, `EVIDENCE/version_device_ainfo.md`; cập nhật FINDINGS (+F-029/F-030), BEHAVIOR (+B-19/B-20), TODO (P3-4/P3-5 checked), OPEN_QUESTIONS (Q-10 partial).
4. P4-1: `git init` + config local + `git add re` (chỉ state, không commit binaries Applications/ + Library/) + commit (sau khi xong LOG/STATE/TODO).

## Evidence / quyết định
- **Đính chính quan trọng:** A3558 = device_hash (UDID hash), không phải hw.machine — sửa hiểu lầm từ session-001.
- 403/429/200 mapping từ log args (HYPOTHESIS mạnh, cần xref disasm để chốt tuyệt đối).
- Logger 89590 sink UNKNOWN; writers siriprobe_* files 0 hit; truedash_language dead (0 hit decompile).
- Git: chỉ track re/, binaries giữ untracked (ghi rõ trong commit message).

## File thay đổi
- Mới: EVIDENCE/siriprobe.md, EVIDENCE/version_device_ainfo.md, LOG/session-006.md (+ .git/).
- Sửa: FINDINGS (+F-029/F-030), BEHAVIOR (+B-19/B-20), TODO (P3-4/P3-5), OPEN_QUESTIONS (Q-10 partial), STATE.

## Chưa làm
- Q-11 còn lại (208F4/218D8/B*/C*/D* callees, onKbShow/onKbHide/onDismiss), Q-12 blocks, Q-13 schedulers, P4-2 EVIDENCE chuẩn hóa, RECONSTRUCTION bodies (P2-5), dynamic verify.

## Tiếp theo (session-007)
1. Q-11 callees: hostSlots/hostSplit/switchInPlace (218D8/217EC/208F4) + B*/C*/D* spawn/teardown (BFF4/C37C/D01C/D154/D4C4/B9A8/B144).
2. RECONSTRUCTION mở rộng: Tweak.x entry/init/prefs/IPC (APPROXIMATION) từ Shared.h + F-011/HOOKS.
3. P4-2 EVIDENCE chuẩn hóa (nếu còn sức).
