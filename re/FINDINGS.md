# FINDINGS.md — Discoveries (Evidence-First)

## F-001 CONFIRMED: Tweak identity + injection scope
- `DuoDash-STL-1.0` (strings.txt:100 `0xba9bc`).
- `DuoDash.plist`: Filter Bundles=[com.apple.springboard, com.apple.Preferences, com.apple.CarPlayApp, com.apple.UIKit] Mode:Any, Executables=[mediaserverd, kbd]. Evidence: plist decode session-001.
- Dylib 3087248B, 4018 funcs, exports rỗng, imports có `_MSHookFunction/_MSHookMessageEx` (imports.txt:333-334).

## F-002 CONFIRMED: Master enable + process gating
- `sub_AC5FC` suffix-match `_NSGetExecutablePath` (AC5FC.c:9, AC738.c:9-20 strcmp).
- `sub_AC7A4` maps role 1..6 → bridge/prefsrefresh/appbridge_cp/carplay/appbridge_uiapp/kbdpoc, sets `byte_168D19` (AC7A4.c:57-322).
- `sub_44C0` dispatcher theo role (44C0.c:29-123). Mọi ctor check `byte_168D19==1` (4A80.c:22, 4C34.c:1168/1295/1448, 27E20.c:252, 163EC.c:126).
- Idempotence via `getenv/setenv DUODASH_AB_*_HOOKED` (HOST, ELIG, DOCK, UIAPP, UIAPP_IPC, CLOAK).

## F-003 CONFIRMED: Mega-ctor sub_4C34 order
1. TrueDash→DuoDash import (4C34.c:275-906). 2. defaults bootstrap (908-1119). 3. CarSleeper daemon (1121-1273, 6 Darwin observers + IOPS source + dispatch_after 8s). 4. SiriProbe 7 hooks (1279-1392). 5. SBApplication 2 hooks (1394-1459). 6. ACF1C+9BB24 (1460-1463).

## F-004 CONFIRMED: Prefs source-of-truth + cache publish
- Domain `com.sensetechlab.duodash.settings` (CFPreferences*).
- `sub_74C8` resolver/publisher → `/var/tmp/com.sensetechlab.appbridge.plist` (14 keys) + `notify_post(resolved)`. `sub_7044/70FC` consumers. `sub_7EA4` fontFloor (+file force), `sub_8058` keypane_enabled, `sub_746C` layout setter 0..8. Evidence: 7044.c/70FC.c/74C8.c/7EA4.c/8058.c/746C.c.

## F-005 CONFIRMED: IPC matrix
- Darwin CFNotification: settings/autostart/keypane/fontfloor/language/ble.action/navprovider/voicecmd + appbridge.* + keyinput.seed/card? (xem API_MAP.md).
- libnotify notifyd: settings.changed/voicecmd.changed/siriprobe.fakepress + cpconnect/cpdisconnect + carplay/perftweak.
- NSNotificationCenter + CPDistributedMessaging wrappers `sub_887C/8934/8D78/8CC0` cho host/uiapp/carwindow/cpui.
- Files: `/var/tmp/com.sensetechlab.{appbridge,navprovider,speed,camera}.plist`, `duodash_keyinput_{seed,out,kb}.plist`, toggles `duodash_ab_*/duodash_cpui_*/duodash_kp_*`; persistent `/var/mobile/Library/DuoDash/*` + `/var/mobile/Library/CarSleeper/*`.

## F-006 CONFIRMED: License ECDSA + server
- Pubkey verify ECDSA P-256 SHA256 X9.62 (`SecKeyCreateWithData/VerifySignature`, A397C.c). Blob `b64url(json).b64url(sig)`, schema {v==1,device_hash,iat/exp ms,product,kid?}, codes 0-10.
- Base `https://license.sensetechlab.com`: POST `/api/v1/activate` (30s, A574C.c), `/api/v1/info` (6s, A8A88.c), `/api/v1/env` (6s, ABB7C.c), GET `/healthz` (6s throttle 3s, AAD40.c). Client `1.1.5+b1d14e0`. Footer "needs internet, will not open".

## F-007 CONFIRMED: DuoDash.app = black launcher
- `com.sensetechlab.duodash`, hidden, Portrait, location bg, 17 locales. `main→UIApplicationMain(DDAppDelegate)`, `didFinishLaunching` chỉ tạo black UIWindow+VC. 25 funcs, imports 19, strings 0 hit sensetechlab. Evidence: DuoDash_export_for_ai/*.

## F-008 CONFIRMED: DuoDashKey.app = transparent keyboard relay
- `com.sensetechlab.duodashkey`, hidden, LandscapeRight, no bg modes. 255 funcs. `DKViewController viewDidLoad` tạo 1x1 DKField + observers kb/lifecycle + `notify_register_dispatch(card)` + Darwin `seed`. Out via `NSPropertyListSerialization→writeToFile atomic + chmod 0x1B6` + `notify_post(kbshown/kbframe/type/kblost)`. In via `card` state + `seed.plist {text,kbType,returnKey,ts<30s}`. Log `/var/tmp/duodash_keypane_relay.log`.

## F-009 CONFIRMED: Prefs UI spec
- Full 30 items trong `PreferenceLoader/Preferences/DuoDashPrefs.plist` (defaults=com.sensetechlab.duodash.settings): license/server/HUD/perf/appbridge/splash/tweaks/language/about. `Root.plist` bundle chỉ subset 11 items. Principal `DuoDashRootListController`. Actions `openLicenseActivation:/chooseAppsToBridge:/openTweakManagement:` — nhưng binary `DuoDashPrefs` chỉ chứa `chooseAppsToBridge:` (636 strings, 2 classes). 2 actions còn lại UNKNOWN location.

## F-010 CONFIRMED: Direct MSHook sites (17 grep hits)
- H1-H4: PSListController 4 (4A80.c:27-31). H5-H6: SBApplication 2 (4C34.c:1451-1452). H7: objc_exception_throw via MSHookFunction (27E20.c:262). H8: off_164450 conditional (4DEB4.c:27). H9-H11: generic wrappers 88A80/9C044/9C0F0. Chi tiết HOOKS.md.

## F-011 CONFIRMED (session-002): dyld init = 4 ctors, role dispatch qua blocks
- FAT binary 2 slices; `__init_offsets` slice0 = {0x44C0, 0x7F010, 0x842EC, 0x9460C} (dump hex session-002). 7F010/9460C = thunk `return AC5FC()`; 842EC = role==1 → `++dword_164C74`.
- Block invoke table (memory `0012CBD8--00146AD8.txt:7-20`): 12CBD8→4C34 (role1 SpringBoard/main), 12CBF8→4A80 (role2 Prefs/main), 12CC18→49A8 (role3/global), 12CC58→48FC (role4/global), 12CC78→4838 (role5-listed/main), 12CC98→47C4 (role6 kbd/main), 12CC38→4A08 (từ 49A8).
- `stru_146AB8` invoke = AC7A4 (pointers.txt:51415); `dispatch_once(165508/146AB8)` ở đầu 47C4/4838/48FC/49A8/4A80/4C34 → AC7A4 chạy trước mọi role body: set role-name + `byte_168D19` + latch memcpy.
- Chuỗi once lồng nhau: 4A08→163EC (12CD20/163600); 4C34:1278→27E20 (12D378/163A78); 27E20:282→4DEB4 (12DD08/164448); 4888(←4838) →455D0 (12DA78/163F70) +4CBDC (12DAB8/164088); 47C4→4C858 (12DA98/164080); 4760(roles2+5)→4D0B8 stub (12DCE8/164430).

## F-012 CONFIRMED (session-002): AC5FC suffixes (pointers.txt:27884-27892)
1=/SpringBoard.app/SpringBoard (AC65C), 2=/Preferences.app/Preferences (AC67C), 3=/CarPlay.app/CarPlay (AC69C), 4=/mediaserverd (AC6BC), 6=/TextInput/kbd (AC6DC), else=5/appbridge_uiapp. `backboardd` (0x10FB4C) tồn tại nhưng KHÔNG thuộc chain AC5FC.

## F-013 CONFIRMED (session-002): off_164450 = BKSDisplayServicesSetScreenBlanked
- `4DDC0.c:19-20`: `off_164450=dlsym(BKSDisplayServicesSetScreenBlanked)`, `off_164468=dlsym(BKSHIDServicesGetBacklightFactor)`. H-005 bác bỏ (không phải IOMobileFramebuffer).
- `4DEB4.c:16-30`: nếu `duodash_ab_display_held` tồn tại + backlight<0.2 → `SetScreenBlanked(1)` + unlink; nếu `duodash_ab_keepawake_off` KHÔNG tồn tại → MSHook SetScreenBlanked→4DF94 (blank gate + dispatch_after 1s).

## F-014 CONFIRMED (session-002): sub_4001C = passthrough probe
- `4001C.c:16-25`: đọc `reason`, gọi `containsString:"foreground status"` rồi BỎ kết quả, luôn tail-call orig `off_163E30`. Không swallow exception. Q-06 đóng.

## F-015 CONFIRMED (session-002): missing prefs actions nằm trong dylib
- `openLicenseActivation:/openTweakManagement:` KHÔNG có trong prefs-bundle binary nhưng dylib có native classes `CNLicenseActivationController` + `CNTweakManagementController` (strings 0x125CF9/0x125D95, function_index ~40 methods: observe/viewDidLoad/cnLicense*/cnApplyStrings/cnDone). Q-08 đóng: impl = dylib, được push từ PSListController hooks (94610/948C0).

## F-016 CONFIRMED (session-002): crash upload = configurable endpoint, default nil
- `9DE28.c:18-35`: getter `CFPreferencesCopyValue(duodash.settings, key)` chỉ trả NSString else nil — KHÔNG default literal.
- `9E014.c:228-231`: `crashreport_endpoint` empty → "Saved on device (no server configured)", không network. Non-empty → POST `<endpoint.trim('/')/v1/reports` multipart (meta.json + bundle.tar.gz), timeout 60s, headers X-DuoDash-Protocol/Idempotency-Key/optional Bearer `crashreport_token`, semaphore 300s. Queue `reports/outgoing` giữ tối đa 3 (xóa từ index 3). Kill-switch `duodash_cr_off`; dryrun `duodash_cr_dryrun` = local-only.
- `license_endpoint` (strings 0xC253D): grep toàn decompile 0 hit đọc key → dead/legacy (4 module license hardcode base). H-006 đóng (negative).

## F-017 CONFIRMED (session-002): 12DB98 loop = AZ* CarPlay-state spoof (7 hooks)
- Table stride 32B (pointers + memory): AZCPConnectionState{carPlayConnected→49870, carPlayActive→498A0}, AZCPNavigationCoordinator{isCarPlayConnected→498D0}, AZCarPlayManager{isCarPlayConnected→49900, isCarPlaySceneActive→49930, evaluateIsCarPlayConnected→49960, evaluateIsCarPlaySceneActive→49990}; origs off_164358-88.
- Body: `++counter; if (byte_163ED8&1) return 0; else return orig()`. H-004 đóng (không phải keyboard hooks).

## F-018 KNOWN-UNKNOWN (session-002): 10 SB hooks qua 4049C KHÔNG resolve được từ artifacts
- `4049C.c:9-18`: `(className, sel, a3..a6)` → `9C044`; nhưng mọi call-site 27E20.c:263-274 chỉ còn 2 args (X2-X5 bị strip), call-graph không chứa IMP (truyền qua register), và export chỉ có 2 file asm (63CE4/6D244, không gồm 27E20). Cần raw ARM64 disasm 10× `BL sub_4049C` (X2=check int, X3=types, X4=replacement, X5=orig-slot). P0-3 chuyển thành blocked-on-artifacts.

## F-019 CONFIRMED (session-003): TrueDash là tiền thân, migrate một chiều True→Duo (EVIDENCE/4C34_import_defaults.md)
- Guard `import.done` once-only (275,729); `import.running` abort path (280-293); pre-check blob/key/settings/rescuer counts (295-321).
- Wipe-then-migrate prefs 2 hosts với rename map + denylist + substring filter `truedash` + xóa nguồn `SetMultiple(nil)` (322-385; rename nội dung UNKNOWN).
- License 4 nhánh A/B1/B2/C theo (TrueDash valid?, DuoDash valid?, iat mới hơn?) với import/reseal/delete/keep + xóa `off_154238` (386-906; verify blob cũ dưới product `"duodash"`).
- airplay/iconstate copy True→Duo (417-480); navapps merge union hidden + Duo-đè-True hiddenClasses + `dashboardModeLastSeen` True-ưu-tiên (482-693); flags msrv/standdown (686-689); log import.done + remove running (698-727).
- Kết luận rename/fork kế nhiệm (HYPOTHESIS mạnh, 6 evidence): chiều duy nhất, xóa nguồn, layout song sinh, compat keys, verify chéo, once-only. Bundle-id TrueDash.app UNKNOWN.

## F-020 CONFIRMED (session-003): defaults bootstrap seed đúng 3 keys = false
- Guard `defaults.done` (912); existing = airplay marker || settings keys || import.done (914-944).
- existing==1: seed keys thiếu trong `85C5C` (`pane_unload_close_enabled, appbridge_autostart, disconnect_close_enabled`) = `kCFBooleanFalse` + sync ok/failed (949-1048). fresh: không seed (946,1052). `85D30` chỉ format join/none.
- Record `at/v/result/why/pinned/kept/sync` (existing) hoặc `at/v/result=new` + append `\n` UTF-8 (1054-1114).

## F-021 CONFIRMED (session-003): CarSleeper daemon đầy đủ
- 6 observers bt/cell/airplane on/off → save/restore prior (85D8C/85E20/85ED4/85F08/85F28/85FA0, 1124-1166).
- Full daemon khi `168D19==1 && latch off`: RadiosPreferences, os_log carsleeper/daemon, mkdir+chmod 0x1FD/0x180, observers settings.changed + testunblank, boot_id vào state.plist (sysctl kern.bootsessionuuid), IOPS source + `dispatch_after(8s)` (1175-1268).

## F-022 CONFIRMED (session-003): DataRouter/navprovider/voicecmd pipeline (component mới: 7F14C + 715C0)
- 7F14C đăng ký 17 Darwin notifies: duo/truedash navUpdate+speedLimit+cameraAlert (7F5A4/7F974/7FBA4, so timestamp GMaps vs Waze plists → DataRouter submit → relayed), navprovider.update/rescan/selftest (ingest queue 1647C0), voicecmd.rescan, settings.changed (full reload), ble.action (pair/unpair theo hud_paired), latch.reset, respring.request/ack, crashreport.send, mapBgUpdate/Clear (JPEG SOI/EOI check).
- CNABNavData relayed ingest (715C0). Chi tiết EVIDENCE/notify_matrix.md §B.

## F-023 CONFIRMED (session-003): latch.reset → respring pipeline
- `80574` (7F14C.c:121-127): nếu `duodash_reenable_tweaks` → unlink DuoDash/*.plist + flag=false + unlink crashreport_collecting + Post(respring.request).
- `8097C` (128-135): guard norespring + respring_last throttle 8/60s + carsleep check + 9C790 → Post(respring.ack) (`96D60` set 164B4E=1) + after 21.6s + thực hiện respring.
- UI controllers tự relocalize theo language.changed (8C41C/8EFE4/920C0/93A3C/948C0/9B848, chung thunk 9B314).

## F-024 CONFIRMED (session-003): BLE HUD pairing flow
- `80468` (7F14C.c:114-120): Sync prefs; `hud_paired ? BLEManager.shared pair : unpair` (guard 1647C8). Prefs UI toggle `hud_paired` Post `ble.action`.
- `96174` (948C0.c:148-154): ble.status.changed → Sync + async UI refresh. Server health + firmware rows hiển thị state.

## F-025 CONFIRMED (session-004): prefs resolver 14 keys + kill semantics (EVIDENCE/prefs_split_autostart.md)
- `74C8` publish đúng 14 keys (375-381); `split_enabled` luôn YES hằng; `enabled=1 iff true AND exists`; autostart via `85CDC` (missing=TRUE); clearpanes one-shot (mtime>done+0.5, xóa 8 keys); fontFloor file-force + clamp 97 (7EA4); keypane missing→ON (8058); layout setter chỉ 1..8 (746C); int-validator mã 0/1/2/3 (7E63C); cpuiMain/More phải trùng pane (7E908).
- **Kill = `kill(pid,9)` SIGKILL sau sysctl+proc_pidpath verify** (763E0.c:247, 7792C.c:321); không SBApplication terminate/FBScene ở 2 path kill. `85CDC(nil)=1` trap + NSNumber≠CFBoolean trap.
- Disconnect-close: arm 12s (override file 0-120s), gate `7BB90 && !nodiscoclose && tracked non-empty`, fire gate `!connected && ...`, cancel via gen++ (7BD58). pane_unload: diff old−new, trừ frontmost (76AF8), resolve SBApplicationController (76BF4), enumerate sysctl (76E08), OFF→defer 78224/drop.
- Autostart: tweak không post `autostart.changed` (chỉ observe→29198); toggle UI 637E8 vs 836C (resolved-plist, default khác 74C8); trigger 1A820 gate panes+flags+throttle 30s nhưng **scheduler UNKNOWN**.

## F-026 CONFIRMED (session-004): CNAB observers + NSDistributed IPC fabric (EVIDENCE/cnab_observers.md)
- 12 methods inventory (2 CarPlay + 10 SB). Transport: `887C`=NSDistributed addObserver, `8D78`=post deliverImmediately — 5 notify appbridge.* đi NSDistributed+NSDictionary (cross-process HYPOTHESIS).
- `onHostRequest:` 4 nhánh (hide/spike/fast-represent/full-host) + mọi exit ack `host.state` via 9424; `onHostRequestSplit:` envOnly short-circuit + reapdelay clamp (0,60] + delayed verify + deactivate gate file; `onCarPlayUIStatus:` async handoff + prune-once failed bid (85B8); connChanged/screenDisconnect → cnabDoCarPlayDisconnect; pollTick 3s self-loop + cpconnect post + retry 5→0 + UI flush; disconnect chỉ khi DDz2.active (dismiss+invalidate+zero states+post cpdisconnect).
- `onCarWindow:` size/pid maps + debounce nudge (nonudge knob, +4.0s, after 1s); `onHostState:` 775 dòng — refused-rollback, sbPid/activated/bid header, base-rect fast/already/evict paths, cpuiMore 2-pass + GC + spawn, acks via 986C.
- Ma trận produce/consume 7 notifies với key names+types: frame keys chỉ C→S, rect keys chỉ S→C, carWin namespace riêng, `layout` produce-nhưng-không-đọc-trực-tiếp.
- Chưa bóc: 208F4/218D8/217EC/279F4/27AC8 + B*/C*/D* callees + 365D4/371AC/370F8 poll helpers (Q-11 còn lại).

## F-027 CONFIRMED (session-005): Unified Keyboard relay end-to-end (EVIDENCE/keyinput_relay.md)
- Focus intercept 4B90C (gates: armed/session/off/nokeypane/cooldown/split + secure-bypass) → dummy inputView chặn native → 4C000 ghi per-bid plist → post begin → SB 3A588 (window 10s, secure-check, dựng card, seed.plist + post seed) / rebuild 37CBC (merge theo ts).
- Apply: SB 3A2E0 (out.plist → in.plist + post apply + apply-budget 80) → UIApp 4CF3C → onApply:0 đọc in.plist → diff/patch (deleteBackward/insertText/setText + change notifications) + ret handling.
- Dismiss/fallback/teardown: 30AC4/30960/37C48 (purge + clear bid + post) + 30C2C (card teardown + card-off) + 38240 (dựng card, từ chối khi keypane OFF/nokeypane) + watchdog 37A18 (≥3s) → 37A7C rebuild (tôn trọng nokprecover).
- Password bypass duy nhất = `isSecureTextEntry` via 45568 (3 enforces: focus/publish/apply; SB-side dự phòng đọc plist["secure"]).
- keypane OFF: teardown+dismiss hiện tại (30960→30AC4) + resign (449C8) + focus passthrough + 38240 từ chối.
- UNKNOWN: 8 block SB sau hop + 2 block UIApp (card/fallback); ts<30s KeyApp (dylib chỉ có 10s/600s); writers kb/out phía KeyApp.

## F-028 CONFIRMED (session-005): CarPlay elig cloak + dock/focus/statusbar (EVIDENCE/elig_cloak.md)
- Helpers: 1CAF8 = bid==duodash duy nhất; 114B4 = bridged check (enabled + contains − navprovider_selected − split_carplay_ui); 1CA4C = split-member; 1E770 roster gate (noroster); 1C3C8 master kill-switch (hosting_off); F83C int-probe (−1 nếu không responds).
- Elig: policy mutate tại chỗ (launchUsingTemplateUI=0, CarPlaySupported/CanDisplay=1) — không fake số; declaration synth {bundle, SupportsMaps=1} khi orig nil + bridged/DuoDash (1DB14); library injector 1DBE8 (DuoDash luôn add + ivar _carPlayDeclaration + nhánh iconadd); icon synth DualAppsIcon.png chỉ DuoDash; displayName literal "DuoDash".
- Dock 1BB20: nuốt DuoDash (debounce 1.5s)/split-member/bridged (clear split + host 1CC04), forward app lạ + teardown/warm. Focus 1BF1C: luôn forward, teardown trước (bảo vệ 0.5s/notification/đúng-app; aggressive-file mở rộng). Home 1C29C: luôn forward + knob nohomedismiss + debounce UNKNOWN writer. Icon-tap 1D1D4: mirror dock không debounce (lưu ý use-after-release mặt chữ 53-54, HYPOTHESIS artifact).

## F-029 CONFIRMED (session-006): SiriProbe swallow-vs-log + fakepress + voicecmd (EVIDENCE/siriprobe.md)
- Latch `siriprobe` + master enable mới cài (4C34:1294-1295); dlopen fallback (1297-1306); 7 hooks validate signature (88A80:29-64); counters init 0xA (1279-1291); 88FD0 reload + 3 notify blocks opaque (1364-1390).
- Gate 894F0 = file-exists throttle 0.5s + cache; swallow thêm cặp riêng + file `swallow` (89764:21). Writers siriprobe_* files: 0 hit (ngoài, UNKNOWN). Logger 89590 rate-limit + backtrace — **sink UNKNOWN**.
- Swallow gate 89764: off→passthrough; 89880(bid==6+enabled+selected)→swallow không cần file; file swallow vắng→passthrough; swallow_id khớp/rỗng→swallow (rỗng=wildcard HYPOTHESIS).
- Ma trận: swallow chỉ 4 hooks nút khi off-vắng + swallow==1; 88BC8 luôn post voicecmd.press trước cả khi sắp swallow; 88EA0 log-only; 88E2C/88F48 passthrough thuần.
- Voicecmd cache 891F0 (enabled cần key+true; selected reverse-DNS) + 88FD0 reload + 890A0 cached 2s. fakepress poster duy nhất prefs-UI (92DFC:64); handler opaque (ứng viên 89334→89338 HYPOTHESIS). voicecmd.changed posters + rescan pipeline (worker 81CE4 v==2 + migrate + luôn post listchanged); consumer press.<bid> ngoài tweak.

## F-030 CONFIRMED (session-006): version/device + language + info-schema (EVIDENCE/version_device_ainfo.md)
- 4008 = generic OS>=X.Y.Z (fallback plist ProductVersion); caller duy nhất 46340 (threshold UNKNOWN). **A3558 đính chính = device_hash (UDID hash), KHÔNG hw.machine.** ACF1C = announce installed, không branch.
- Branch version duy nhất: 3AE50 CF<1946.102 chọn evict selector (map iOS HYPOTHESIS). operatingSystemVersion chỉ telemetry. MinimumOS 0 hit (floor external 14.0). Không blacklist device (fail-soft). Locale hệ thống 0 hit.
- Language: write 6A4E4 → 6 observers (clear + main-reload); read 9AFB0 4-tầng + whitelist 17 (16 strings UNKNOWN) + cache; truedash_language dead; en_US_POSIX chỉ date formatter.
- Q-10 partial: info POST 16+ keys, parse off-main queue geo; 4 nhánh (403/429/200/error — số HYPOTHESIS mạnh); keys table + validators (AA9FC/AAAD0 UNKNOWN); side-effects verdict file + retry 429 một lần + cache geometry + async blob persist (đích A7E04 UNKNOWN); return via A850C→main.

## F-031 CONFIRMED (session-007): hosting engine hostSlots/hostSplit/switchInPlace (EVIDENCE/hosting_engine.md)
- hostSlots(bids,skipEvict,onHosted-block): dirty-check (layout/slots/sizes/CPUI-flags) → reshow (89D8+70248+234A0/23AB0+9424+log) hoặc full-host (no-display/degenerate errors via 97A0; reset globals; 7 files /var/tmp: nopanepad/panepad/nopaneround/layout/panefracs/paneratio+noratio; log hình học; gen++; block 2410C captures → A8424 async queue 165118). Không CFPrefs/notify_post trong body. skipEvict chỉ ảnh hưởng async 2410C (cơ chế UNKNOWN).
- hostSplitL 2-pane wrapper → hostSlots(...,nil). switchInPlace(bids,gen)→bool: guards nặng (active/split/visible/swap/max/gen/layout/count/flags) → phân loại slots (22E40 eligible vs CPUI) → convert/replacePane/rebuildMat → async 26FE4 continuation (evict 85B8 + spike + geometry + 9424 + log) hoặc delay-100ms 25EDC.
- onHosted block = delay-wrapper → 27AE4 gen-guard → 7792C reap/kill(old,new). Delayed verify 27AC8 gen-guard → 792C4 nav-hide. reapdelay file clamp (0,60].
- `layout` string chỉ đọc từ file duodash_ab_layout + fallback plist (218D8:421-444); 2 methods kia 0 hit — request layout truyền gián tiếp via globals (HYPOTHESIS).

## F-032 CONFIRMED (session-007): spawn/teardown callees + KB observers + poll helpers (EVIDENCE/spawn_teardown_kb.md)
- 17 callees onHostState: B768 (SB visible+dock refresh), BBF8 (evict theo gen), BCDC (cancel timer), BD18 (register size + bump gen), BE34 (is-base predicate), BEE4 (move view, tolerance 0.5), BFF4 (confine/retry/timeout + acks launch_timeout/confine_failed), C2A4 (killed-list predicate + nodeathwait), C37C (event-launch DB/CAR 3 tầng + reasons), CB08 (waiter 50ms), CCEC (lazy 7 containers), D01C (gate base → D4C4/retry + ack is_base_app), D154 (teardown 1 bid: background+detach+tombstone+BBF8), D4C4 (router: fast D684 hay CB08), CE5C (teardown toàn cục), B9A8 (abort/reset + grace 3s), B144 (dock-hide ticker 1s + nodockhide + pid-alive).
- KB observers: onKbShow/onKbHide = stub rỗng (no-op dù đã đăng ký); onDismiss = force resign + clear probe (449C8); onEndEditing = teardown có điều kiện + post end (knob đảo, weak-match, double-decrement).
- Poll helpers: 365D4 = probe resolution (FBSDisplayConfiguration → 480p/720p/1080p → prefs headunit_* + post ble.status.changed); 371AC = dropOverdueNotice flush; 370F8 = nudgePresent:"tick" (knobs visible/running/nonudgetick).
