# API_MAP.md

## CFPreferences domain chính
`com.sensetechlab.duodash.settings` — keys: license_status/server_health/hud_{pairing_status,paired,firmware_version,paired_uuid,orientation,brightness}/deepsleep_enabled/perf_tweak_enabled/pane_unload_close_enabled/appbridge_autostart/disconnect_close_enabled/keypane_enabled/appbridge_enabled/bridgedApps/bridged_font_floor/appbridge_split_{left,right,third,enabled,ratio,frac_a,frac_b,frac_layout,carplay_ui,carplay_ui_more}/appbridge_layout/pane_chip/picker_order/app_sections/navprovider_{selected,autostart,seen,keepalive,status,last}/navbubble_*/voicecmd_*/headunit_{resolution,video_quality}/splash_selected/duodash_language + truedash compat.

## File cache /var/tmp (volatile)
`com.sensetechlab.{appbridge,navprovider,speed,camera}.plist`, `duodash_keyinput_{seed,out,kb}.plist`, `duodash_ab_{bubble_pos,suspended,ui_tokens}.plist`, `duodash_map_bg.jpg`, toggles `duodash_ab_*` (168 entries) / `duodash_cpui_*` / `duodash_kp_*` / `duodash_*`.

## Persistent /var/mobile
`Library/DuoDash/{license.blob,navapps.plist,notice.state,geometry.state,health.state,panel.state,iconstate_backup,config_repair.record,airplay_*,import.*,defaults.done,respring_*,ckpt_*,reports/*}`, `Library/CarSleeper/{carsleeper.log,state.plist,suspended_pids.plist}`, `Library/TrueDash`, `Library/Preferences/com.apple.airplay.plist`.

## Darwin notifies — full matrix (session-003, chi tiết EVIDENCE/notify_matrix.md)
- notifyd 12: appbridge.{cpdisconnect,cpconnect×3 Lisbon/health, listchanged(DDz3)}, settings/voicecmd/siriprobe.fakepress (siriprobe), carplay/perftweak, license.{activate,refresh}, health.refresh.
- Darwin 68: AppBridge 15 (163EC×3 + 27E20×12: listchanged/resolved/exit/dashboardmode/navhideundo×2/settings/navbubble/autostart/fontfloor/keypane/paneactivity/exit/cproleup); keyinput 12 (27E20×8 + 4CBDC×4 apply/dismiss/card/fallback); carsleeper 8 (bt/cell/airplane on/off + settings.changed + testunblank); navprovider/voice 14 (relayed, duo+true navUpdate/speedLimit/cameraAlert, update/rescan/selftest, voicecmd.rescan, settings.changed, ble.action, latch.reset, respring.request, crashreport.send, mapBgUpdate/Clear); license/language UI 14 (8C41C/8EFE4/920C0/93A3C/948C0×3/96D2C/9B848).
- NSNotification local 8: CarPlayIsConnectedDidChange, UIScreenDidDisconnect, UIApplication active/background, Keyboard willShow/Hide, TextField/View endEditing.
- Đích cũ: F-005 / subagent-2 §6b (tóm tắt) — ma trận mới thay thế.

## Network
`https://license.sensetechlab.com/api/v1/{activate,info,env}` POST JSON + `/healthz` GET; `https://www.sensetechlab.com/duodash` link; crash POST `<crashreport_endpoint>/v1/reports` multipart (configurable, default nil — F-016).

## ObjC classes (hook targets + data-plane mới session-003)
CNAB{CarPlayObserver,SpringBoardObserver,HostUIAppResponder,UIAppObserver,KeyProbeObserver,NavData}, DD{z1,z2,z3}, DataRouter, BLEManager, ImageUploader, CN{LicenseActivationController,TweakManagementController,NavBubbleSettingsController,VoiceCmdSettingsController}, CRCarPlay{AppPolicyEvaluator,AppDeclaration}, DB/CAR{ApplicationInfo,LeafIcon*,ApplicationController,AppDock,Focus,RootStatusBar,SceneUpdate,Dashboard,ProcessMonitor}, FB{Scene,DisplayLayoutPublisher}, SB{Application,DeviceApplicationScene*,SuspendedUnderLockManager,AppViewController,ToAppsWorkspaceTransaction,HIconManager,LeafIcon}, AZ{CPConnectionState,CPNavigationCoordinator,CarPlayManager}, SiriActivationService, PSListController/PSTableCell, UI{TextField,TextView,Screen,Window,KeyboardImpl,KBScreenTraits,PeripheralHost,Device,Bundle}, AVExternalDevice, DuoDash{RootListController,AppPickerController}, DK{AppDelegate,ViewController,Field}.

## Selectors (key)
Xem HOOKS.md. Entry actions `openLicenseActivation:/chooseAppsToBridge:/openTweakManagement:` → impl dylib F-015 (không còn UNKNOWN).
