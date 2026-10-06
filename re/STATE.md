# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-114 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-45 (session-114): GitHub Actions session-113 (`b8e355d`) đã xanh theo user. Executable target thêm data-only `3F3F0` post-resize publish exception outcome được xác nhận bằng LSDA `0x114994` + raw ARM64: only protected `89D8` publish range `0x3F4BC..0x3F4D4` lands at typed catch `0x3F5A8`; expected discriminator catch/swallow rồi rejoin `0x3F4D4`, nên counter normalization + `DDz2 shared`/`probeSceneForSlot:` + possible landscape-adjusted `3F5C0` follow-up vẫn eligible; nonmatching discriminator nhảy `0x3F5BC` resume unwind. Không invoke `89D8`, private scene probe/`3F5C0`, synthesize/catch exception hay mutate counters/state.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-114):
- R-113 data-only 3F3F0 publish exception continuation: protected `89D8` throw→swallow+continue post-publish follow-up; nonmatching type→resume unwind.

## CURRENT TASK:
- R-113 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-114 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-114 promote exact `3EDFC` LSDA `0x1148F4`: protected SpringBoard/frontmost-app/string-identity throw→common typed catch swallow+false return; nonmatching type→resume unwind. Chỉ data-only swallow→false/unwind metadata, không private SpringBoard selector/object traversal, invoke `3EFD4` hay synthesize exceptions. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

## BLOCKERS:
- Workspace hiện tại Windows không có Xcode/iOS SDK nên chưa compiler-build local. P0-3 vẫn blocked (raw asm 27E20); không device jailbroken; các private-hook contracts chưa đủ evidence vẫn chưa đưa vào executable target.

## IMPORTANT DISCOVERIES:
- `DuoDash.plist` Filter: Bundles=[springboard,Preferences,CarPlayApp,UIKit] Mode:Any + Executables=[mediaserverd,kbd]. CONFIRMED.
- Master enable `byte_168D19` set bởi `sub_AC7A4`, mọi ctor check nó. CONFIRMED.
- Prefs source-of-truth `com.sensetechlab.duodash.settings` + cache `/var/tmp/com.sensetechlab.appbridge.plist` via `sub_74C8` publish + `notify_post(resolved)`. CONFIRMED.
- License ECDSA P-256 verify + server `https://license.sensetechlab.com/{activate,info,env,healthz}`. CONFIRMED (static).
- KeyApp là transparent keyboard relay qua `seed/kb/out` plists + `card/kbshown/kbframe/type/kblost` notifies. CONFIRMED.
- DuoDash.app chỉ là black-screen launcher (hidden, location bg). CONFIRMED.

## CONFIRMED BEHAVIOR (short):
Xem FINDINGS.md + HOOKS.md + API_MAP.md. Tóm tắt: process-gated multi-ctor init; SpringBoard AppBridge host; CarPlay eligibility cloak; UIApp keyboard/orientation hooks; SiriActivation 7 hooks; SBApplication 2 hooks; PSListController 4 hooks + 1 swizzle; Darwin+notifyd IPC; CFPreferences persistence; ECDSA license.

## UNRESOLVED QUESTIONS:
Xem OPEN_QUESTIONS.md (Q-03 blocked, Q-09 entitlements, Q-10 server schema, Q-11 ObjC bodies, Q-12 opaque blocks; Q-01/Q-02/Q-04..Q-08 closed).

## FILES CHANGED (session-114):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-114.md`.

## TEST STATUS:
Session-113 GitHub Actions build GREEN (`b8e355d`, user-confirmed). Session-114 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
