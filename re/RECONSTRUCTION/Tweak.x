// RECONSTRUCTION/Tweak.x — APPROXIMATION skeleton (session-007)
// Behavior-equivalent intent; KHÔNG compile ở đây (không toolchain).
// Mọi hằng số + thứ tự từ EVIDENCE (F-011 init, HOOKS hooks, F-025 prefs, F-026/F-031 IPC).
// Semantics phải giữ: dispatch_once guards, main-vs-global queues, getenv idempotence,
// byte_168D19 master enable, orig call-through mặc định.

#import "DuoDashShared.h" // DD_* domains/notifies/paths/roles

// ---- P0 init (F-011/F-012) ----
// dyld __init_offsets (slice0): 44C0, 7F010, 842EC, 9460C.
// 7F010/9460C = thunk return AC5FC(); 842EC = role==1 → ++dword_164C74.
// 44C0: role = AC5FC() (suffix match _NSGetExecutablePath:
//   1=/SpringBoard.app/SpringBoard, 2=/Preferences.app/Preferences,
//   3=/CarPlay.app/CarPlay, 4=/mediaserverd, 6=/TextInput/kbd, else 5).
// Dispatch blocks (invoke table, memory 12CBD8..): role1→4C34 (main),
// role2→4A80+4760 (main), role3→49A8 (global)→4A08→once→163EC,
// role4→48FC (global), role5-listed→4838→4888→once→455D0+4CBDC (main),
// role6→47C4→once→4C858 (main). Role5 check .app path + !=com.apple.siri
// + bundle trong off_12CCC0 (44C0.c:41-98).
// Mọi role ctor mở đầu dispatch_once(165508/146AB8)=AC7A4:
//   set role-name + byte_168D19 master + latch memcpy.
// Once lồng: 4A08→163EC (12CD20); 4C34:1278→27E20 (12D378);
//   27E20:282→4DEB4 (12DD08, BKS blank hook); 4888→455D0 (12DA78)
//   +4CBDC (12DAB8); 47C4→4C858 (12DA98); 4760→4D0B8 stub (12DCE8).
%ctor {
    // APPROXIMATION: Logos %ctor ~ 44C0 dispatcher.
    // Hỏi AC5FC() role rồi dispatch_async block tương ứng (queue như trên).
    // Idempotence: setenv DUODASH_AB_*_HOOKED ở mỗi ctor chuyên biệt.
}

// ---- Prefs publish (F-025/B-15) ----
// 74C8 hex-phase: clearpanes one-shot (mtime>done+0.5 → xóa 8 keys) →
//   AppSynchronize + 7EA4 (floor, clamp 97) + 8058 (keypane, missing=ON) →
//   bridgedApps (non-array→empty) + autostart raw → bulk off_154208 (10 keys)
//   + 7E908 compute → publish ĐÚNG 14 keys (split_enabled hằng YES;
//   enabled=1 iff true AND exists; autostart=85CDC) + navprovider ×2 →
//   write /var/tmp/com.sensetechlab.appbridge.plist (atomic) →
//   notify_post(appbridge.resolved). Không synchronize cuối.
// 746C: layout 1..8 mới SetAppValue+Sync+74C8(), else return nguyên.

// ---- IPC fabric (F-026/B-16, EVIDENCE/notify_matrix.md, cnab_observers.md) ----
// NSDistributed (887C add / 8D78 post deliverImmediately):
//   C→S: host.request(.split) + carwindow + cpui.status;
//   S→C: host.state (+refused) + uiapp.*.
// notifyd: cpconnect/cpdisconnect, settings/voicecmd/fakepress,
//   perftweak, license.*, health.refresh.
// NSNotification local: CarPlay connect, screen disconnect, app
//   active/background, keyboard show/hide, end-editing.
// File: seed/out/kb plists + per-bid container plists (EVIDENCE/keyinput_relay.md §6).

// ---- Hooks đã map (HOOKS.md + F-017/F-013/F-028) ----
// PSListController ×4 + PSTableCell swizzle (prefs UI, 4A80).
// SBApplication ×2 (4C34). objc_exception_throw passthrough probe (4001C).
// BKSSetScreenBlanked → 4DF94 (gated keepawake_off) + backlight reader.
// SiriActivationService ×7 (validate-signature wrapper 88A80; swallow 4 nút).
// SB scene ×10 via 4049C — BLOCKED (F-018, orig/hook-fn UNKNOWN).
// CarPlay elig (mutate 0/1/1 + synth declaration + injector + icon/name),
//   dock/focus/statusbar/icon-tap (nuốt có điều kiện, forward mặc định).
// UIApp keyboard/orientation 43 + AZ* spoof 7 (163ED8→0).
// _UIKeyboardLayerHostView ×3 (dời native kb màn ngoài).

// ---- Kill semantics (F-025) ----
// SIGKILL sau sysctl+proc_pidpath verify (763E0/7792C). Disconnect 12s
// (override file, gates, gen-cancel). pane_unload diff (frontmost-exempt).
// autostart observe-only + gated trigger (scheduler UNKNOWN — Q-13).
