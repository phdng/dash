# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-112 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-43 (session-112): GitHub Actions session-111 (`a9914d4`) đã xanh theo user. Executable target thêm data-only `3F100` activating-entity setter exception outcome được xác nhận bằng LSDA `0x114948` + raw ARM64: only protected `respondsToSelector:setActivatingEntity:`/setter-send range `0x3F128..0x3F144` lands at `0x3F158`, unconditionally begin/end-catches rồi branches `0x3F144` normal cleanup/return; không discriminator branch, reason probe, retry hay counter/state mutation. Không invoke private setter, touch captured entity hay synthesize/catch exception.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-112):
- R-111 data-only 3F100 exception outcome: protected `setActivatingEntity:` capability/send throw→local swallow+cleanup/return.

## CURRENT TASK:
- R-111 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-112 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-112 promote exact `3F224` LSDA `0x114960`: protected userInfo/bundle lookup, bundle/host-slot string matching, final `89D8` request throw→common typed catch swallow+cleanup; nonmatching type→resume unwind. Chỉ data-only swallow+cleanup/unwind metadata, không dictionary/string traversal, invoke `89D8` hay mutate hosting state. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-112):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-112.md`.

## TEST STATUS:
Session-111 GitHub Actions build GREEN (`a9914d4`, user-confirmed). Session-112 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
