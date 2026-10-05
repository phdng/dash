# BEHAVIOR.md — Behavioral Reconstruction (partial, APPROXIMATION)

## B-01 Init (CONFIRMED session-002 — xem F-011, thay APPROXIMATION cũ)
dyld 4 ctors → 44C0 role dispatch (blocks 12CBD8/12CBF8/12CC18/12CC58/12CC78/12CC98) → `dispatch_once(165508/AC7A4)` set role-name + master `byte_168D19` → role body. Chuỗi lồng: 4C34 ⊃ 27E20 (1278) ⊃ 4DEB4 (27E20:282); 4838 ⊃ 4888 ⊃ 455D0+4CBDC; 49A8 ⊃ 4A08 ⊃ 163EC; 47C4 ⊃ 4C858; 4760 ⊃ 4D0B8 stub. Queue: role1/2/5-listed/6 = main, role3/4 = global→main. Giữ nguyên queue semantics khi reconstruct.

## B-01b SpringBoard host (CONFIRMED từ deep-read 27E20)
Tmp migrator `carnav_*→duodash_*` (rename + fallback copy giữ atime/mtime); suspended-killer `kill(pid,19)`; retire `dashboard_mode`; gate `appbridge_sb` latch; config_repair (`noconfigrepair` knob → skipped/repaired/clean + record append); keyinput reset (`card=0` + post dismiss); navbubble_dock_mode bị xóa.

## B-02 Prefs resolver (CONFIRMED static)
Input: CF domain `com.sensetechlab.duodash.settings` + semaphore `duodash_ab_clearpanes`. Transform: nếu clearpanes mới hơn .done → xóa 8 keys + sync; đọc appbridge_enabled/bridgedApps (lọc 7E568)/autostart/bulk list/7E908 panes → build dict 14 keys + navprovider_* → write `/var/tmp/com.sensetechlab.appbridge.plist` + `notify_post(resolved)`. Error: file missing → nil; CF type mismatch → fallback 0/nil.

## B-03 AppBridge split/layout (HIGH CONFIDENCE)
Keys `split_left/right/third, layout 0-8, ratio, frac_a/b/layout, carplay_ui{,_more}, enabled=YES forced`. Setter `746C` chỉ nhận 0..8. Consumer `7044/70FC` đọc cache file (không CF). Side-effects: autostart mở DuoDash sau CarPlay connect vài giây; disconnect-close chờ ~12s; pane_unload_close kill app cũ (music stop, unsaved lost); phone app never closed.

## B-04 Keyinput relay (CONFIRMED static)
Dylib→Key: `card` (UP/DOWN int) + `seed` Darwin → đọc `seed.plist {text,kbType,returnKey,ts<30s}`. Key→Dylib: `kb.plist {h,sh,dark,ts}` + `notify kbshown/kbframe` (debounce |Δh|≥0.5, h≥1); `out.plist {text,ret,ts}` + `notify type`; `kblost` khi cardUp && !kbVisible cùng gen. SuppressEcho chống loop. Password fields bypass unified keyboard (dylib-side, chưa locate).

## B-05 CarPlay cloak (HIGH CONFIDENCE)
Elig hooks fake policy/declaration/library/icon/displayName để bridged apps hiện trên car home. Dock/focus/statusbar intercept giữ pane. Scene/layout/publisher/monitor hooks giữ geometry + chống kill/reap. Kill-switches `duodash_cpui_*` (fileExists=disable).

## B-06 License (CONFIRMED static)
Blob verify offline ECDSA trước; online activate/info/env/healthz sau. Fail `will not open` nếu no internet. Verdicts: not_activated/activating/active/invalid_key/device_limit/device_blocked/no_connection/unavailable/no_device_id/revoked/invalid_blob/expired/no_server/clock/update. Pending_key/email stored; email recorded, never required to unlock.

## B-07 CarSleeper/perf (HIGH CONFIDENCE)
Sleeper: bt/cell/airplane Darwin → radios prefs + IOPS source + state.plist. Perf: `perf_tweak_enabled` lowers CarPlay fps (carplay/fps) → cooler + recover; cần reconnect CarPlay (unplug/replug). DeepSleep separate toggle.

## B-08 Crash reporting (CONFIRMED session-002)
Guard `crashreport_collecting` (re-entrancy) + kill-switch `duodash_cr_off`; collect `9EE88` → `bundle.tar.gz` + meta.json; queue giữ 3; upload IFF `crashreport_endpoint` non-empty → POST `<ep>/v1/reports` (60s, Bearer optional); dryrun = local-only.

## B-09 License client (CONFIRMED session-002)
Verify offline (codes 0-8,10, fehl 9) → activate (30s, key/device_hash/email/model/udid/ios/client/product) → info/env telemetry (6s, obfuscated keys, rate-limit env<8 + healthz 3s + spinlock) → verdict map (rate_limited/invalid_key/device_limit/blocked/unavailable) + 24h retry. Base hardcode, endpoint key dead.

## B-10 TrueDash→DuoDash migration (CONFIRMED session-003, EVIDENCE/4C34_import_defaults.md)
Once-only (`import.done/running` + abort path) → pre-check (blob/key/counts) → wipe-then-migrate prefs 2 hosts (copy/rename/drop/remove counters, xóa nguồn) → license 4 nhánh (import/reseal/delete/keep theo valid+iat) → copy airplay/iconstate → merge navapps (hidden union, hiddenClasses Duo-wins, modeLastSeen True-wins) → log import.done. Error: write-fail giữ lock để retry; deviceId rỗng → skip license; file corrupt → skip merge.

## B-11 Defaults bootstrap (CONFIRMED session-003)
existing? → seed đúng 3 keys thiếu = false → sync → record existing/new + `\n` UTF-8. Idempotent qua `defaults.done`.

## B-12 CarSleeper daemon (CONFIRMED session-003)
6 radio prior save/restore + RadiosPreferences + IOPS source + boot_id state + 8s delayed start + testunblank force-wake. Kill-switch qua latch `carsleep` + master enable.

## B-13 DataRouter pipeline (CONFIRMED session-003, EVIDENCE/notify_matrix.md §B)
Nav sources (GMaps/Waze plists, duo+true variants) → timestamp race → submitNav/submitSpeed → relayed notifies → car pane + `/var/tmp/speed.plist`. Voice rescan, provider rescan/selftest trên queue 1647C0. Settings.changed → full reload. mapBg JPEG-gated upload.

## B-14 Latch/respring + BLE (CONFIRMED session-003)
latch.reset (guard reenable_tweaks) → wipe plists → respring.request (throttle 8/60s, carsleep-aware) → ack flag → thực hiện. ble.action: hud_paired ? pair : unpair; status → UI refresh.

## B-15 Prefs/split/autostart/disconnect (CONFIRMED session-004, EVIDENCE/prefs_split_autostart.md)
74C8 5-phase (clearpanes → sync/floor/keypane → bridgedApps → bulk+7E908 → publish 14 keys + post resolved). split_enabled hằng YES; consumers quyết định on/off. fontFloor file > prefs, clamp 97. keypane default ON. layout 1..8. cpui* phải trùng pane + self-healing writes. Disconnect 12s + nodiscoclose + gen-cancel + SIGKILL tracked. pane_unload diff + frontmost-exempt + SIGKILL verified pids. autostart: observe-only + UI toggle + 1A820 gated (scheduler UNKNOWN).

## B-16 SB↔CarPlay hosting protocol (CONFIRMED session-004, EVIDENCE/cnab_observers.md)
NSDistributed + NSDictionary fabric. C→S: host.request(.split) + carwindow (size/pid) + cpui.status (ack). S→C: host.state (activated/bid/sbPid + cond rect/more/gen/killed) + refused variant. SB: request→hide/spike/represent/host + ack; split→in-place/slots+reapdelay; status→handoff+prune; poll 3s + connect/disconnect transitions. CP: window→maps+nudge; state→refused-rollback/base-rect/more-GC-spawn + acks. Mọi error graceful, không throw/retry trong handlers.

## B-17 Unified Keyboard relay (CONFIRMED session-005, EVIDENCE/keyinput_relay.md)
Intercept (4B90C gates + dummy inputView) → publish per-bid plist (4C000, secure=@NO) → begin → SB seed (3A588 window 10s + secure-check + card + seed.plist + post seed; rebuild 37CBC merge-ts) → KeyApp (HYPOTHESIS writers) → SB forward out→in + post apply (3A2E0, budget 80) → onApply: diff/patch + change notifications + ret. Dismiss/fallback/teardown hai phía + watchdog rebuild (tôn trọng nokprecover). Password = isSecureTextEntry duy nhất (45568, 3-4 enforces). keypane OFF = teardown + native passthrough + từ chối dựng card. Swizzle _UIKeyboardLayerHostView chỉ dời native kb màn ngoài (376DC 3 điều kiện). UNKNOWN: 10 blocks sau hop, ts<30s, KeyApp writers.

## B-18 Elig cloak + dock/focus/statusbar (CONFIRMED session-005, EVIDENCE/elig_cloak.md)
Bridged check 114B4 (enabled + contains − navselected − cpui) vs first-party 1CAF8; gates roster/hosting_off. Elig: mutate policy tại chỗ (TemplateUI=0, Supported/Display=1), synth declaration {bid,Maps=1} khi orig nil, library injector (+DuoDash luôn add), icon chỉ DuoDash, displayName "DuoDash". Dock nuốt (DuoDash debounce 1.5s / split-member / bridged→host), forward app lạ. Focus luôn forward + teardown có bảo vệ (0.5s/notification/đúng-app; aggressive mở rộng). Home luôn forward + nohomedismiss + debounce. Icon-tap mirror dock không debounce.

## B-19 SiriProbe (CONFIRMED session-006, EVIDENCE/siriprobe.md)
Latch + master enable → dlopen fallback → 7 hooks validate-signature + counters + cache reload + 3 notify blocks. Gate file-exists throttle 0.5s. Swallow chỉ 4 hooks nút (off-vắng + gate==1: bid==6 voicecmd hợp lệ, hoặc file swallow + id khớp/rỗng). 88BC8 luôn post voicecmd.press trước cả khi swallow. 88EA0 log-only; prewarm/voiceTrigger passthrough. Logger backtrace sink UNKNOWN. Voicecmd cache (enabled cần key+true; selected reverse-DNS; reload 2s-cache). fakepress từ prefs-UI test; rescan pipeline quét VoiceHandlers + migrate + post listchanged.

## B-20 Version/device/language + info-schema (CONFIRMED session-006, EVIDENCE/version_device_ainfo.md)
Floor iOS 14.0 khai báo; runtime weak-link + plist fallback (chạy OS cũ); branch version duy nhất CF<1946.102 (evict selector); không blacklist device (fail-soft everywhere); device_hash = UDID hash (đính chính A3558). Language: write→post→6 observers clear+reload; read 4-tầng + whitelist 17 + cache; legacy carnav migrate; truedash_language dead. Info-schema: 16+ keys POST → parse queue geo → 4 nhánh (403 verdict-file + conditional blob-verify; 200 cache geometry + persist; 429 retry một lần; error D) → callback main. Validators AA9FC/AAAD0 + đích A7E04 + 16 strings UNKNOWN.

## RECONSTRUCTION INCOMPLETE — init + prefs + IPC + license + crash + import/defaults + sleeper + datarouter + split/kill + hosting-protocol static DONE; 10 SB hook bodies + ObjC callees (208F4/218D8/B*/C*/D*) + poll helpers + opaque blocks + 1A820/7B9EC schedulers chưa bóc; chưa dynamic verify.
