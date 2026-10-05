# EVIDENCE/notify_matrix.md — Full notify sweep rebuild (session-003)
_Nguồn: subagent general grep `notify_register_dispatch` + `CFNotificationCenterAddObserver` toàn decompile/ + đọc stub callbacks. 12 notifyd + 68 Darwin + 8 NSNotification._

## A. notifyd (`notify_register_dispatch`) — 12
| Notify | Site | Handler/queue/token | Effect |
|---|---|---|---|
| appbridge.cpdisconnect | 163EC.c:168-172 | stru_12CD40 / main / &16360C | CarPlay-disconnect branch (opaque). Posters: 227E4.c:59, 3CC44.c:301, 41730.c:111 |
| appbridge.cpconnect | 163EC.c:174-178 | stru_12CD60 / main / &163638 | CarPlay-connect branch (opaque). Poster 22AD0.c:46 |
| settings.changed | 4C34.c:1366-1370 | stru_130618 / main / stack token | Siriprobe refresh branch (opaque). Posters Darwin+notifyd: 6A740.c:35, 8B624.c:170 |
| voicecmd.changed | 4C34.c:1372-1376 | stru_130638 / main / v243 | VoiceCmd-list reload (opaque). Posters: 81CE4.c:530 (via 82830), 9332C.c:23 |
| siriprobe.fakepress | 4C34.c:1379-1383 | stru_130658 / main / v242 | Fake Siri button-press test (opaque). Poster 92DFC.c:64 |
| appbridge.listchanged | 525D8.c:185-189 | sub_70140+12DEC0 / main / DDz3._listChangedTok | DDz3 refreshAppsAsync (weak). Posters: 6C2EC.c:16, 8B624.c:112,171, 8BD94.c:22 |
| carplay/perftweak | 970FC.c:20-22 | stru_130CF0 / 970BC() queue / &1632A4 + timer 30s 130D10 + 971FC() | Perf-tweak toggle. Check/poster: 7FF7C.c:47,61, 971FC.c:24 |
| license.activate | A7E6C.c:25-29 | stru_146268 / license queue 1650E0 / stack | License-activate branch + 1h timer 1462E8 + async 1462C8/1461D8. Poster 8CDAC.c:101 |
| appbridge.cpconnect | A7E6C.c:30 | stru_146288 / license queue / v8 | License-daemon re-validate khi CarPlay lên |
| license.refresh | A7E6C.c:31 | stru_1462A8 / license queue / v7 | License-refresh. Poster 948C0.c:97 |
| appbridge.cpconnect | AAC00.c:26-30 | stru_146398 / health queue 1652C0 / stack | Health-daemon nghe cpconnect + timer 60s + after 10s |
| health.refresh | AAC00.c:31 | stru_1463B8 / health queue / v8 | Health-refresh. Poster 948C0.c:98 |

## B. Darwin (`CFNotificationCenterAddObserver`) — 68
### AppBridge (163EC ×3, 27E20 ×6)
| appbridge.listchanged | 163EC.c:146-152 | 17344 / unk_163608 / Immediate | 163800++, after 0.35s → 1FB40 (debounce tay) |
| appbridge.resolved | 163EC.c:153-159 | 17344 chung / Immediate | Như trên |
| appbridge.exit | 163EC.c:160-166 | 173FC / Immediate | async main 12D0C8 (teardown CP pane) |
| dashboardmode.changed | 27E20.c:204-210 | 7B648 / null / Coalesce, guard 1646C4 | 7B29C (retired flag) |
| appbridge.navhideundo | 27E20.c:211-217 | 7B654 / Coalesce | async queue 793F4 12E7C8 (undo nav-hide) |
| appbridge.navhideundo.media | 27E20.c:218-224 | 7B68C / Coalesce | async 12E7E8 (media variant) |
| settings.changed | 27E20.c:313-319 | 29198 / unk_163A80 / Immediate | 74C8()+792C4() (SB reload) |
| navbubble.changed | 27E20.c:321-327 | 291AC / Coalesce | guard 163A90, after 0.35s 12D3C8 |
| appbridge.listchanged | 27E20.c:329-335 | 29198 chung / Immediate | SB host refresh song song notifyd 525D8 |
| autostart.changed | 27E20.c:337-343 | 29198 chung / Immediate | Full SB reload |
| fontfloor.changed | 27E20.c:345-351 | 291F4 / Immediate | 7EA4() floor → broadcast uiapp.fontfloor {bridged_font_floor,bundleId} via 8C28 |
| keypane.changed | 27E20.c:353-359 | 29400 / Immediate | 8058() → 30960 nếu OFF → broadcast uiapp.keypane |
| appbridge.paneactivity | 27E20.c:360-367 | 2961C / Coalesce | throttle 0.25s (CACurrentMediaTime), --164568, async 701D0/12E530 + 3723C() |
| appbridge.exit | 27E20.c:369-375 | 29748 / Immediate | after 1s 12D3E8 (SB-side exit; CP-side 173FC) |
| appbridge.cproleup | 27E20.c:453-459 | 29778 / Coalesce | async main 12D408 (sau post từ 163EC.c:502) |
### keyinput (27E20 ×8 + 4CBDC ×4)
| keyinput.begin/type/end/kbframe/kbshown/othertap/kblost/retap | 27E20.c:392-447 | 37978/3798C/379A0/379B4/379C8/379DC/379F0/37A04 / null / Coalesce, guard 163CB0 | Mỗi fn async main 12D7F8→12D8D8 (forward → key probe). Kèm post keyinput.dismiss (27E20.c:450) + reset card=0 via 30F48 |
| keyinput.apply | 4CBDC.c:70-76 | 4CF3C / KeyProbeObserver 163F68 / Coalesce | async main 4D0AC (apply unified-KB text) |
| keyinput.dismiss | 4CBDC.c:78-84 | 4CFBC / Coalesce | async main 4D0A0 (dismiss KB) |
| keyinput.card | 4CBDC.c:86-92 | 4D03C / Coalesce | async main 12DCA8 (card/pane switch) |
| keyinput.fallback | 4CBDC.c:94-100 | 4D050 / Coalesce | async main 12DCC8 (fallback stock KB) |
### carsleeper (4C34 ×8)
| carsleeper/bt-off | 4C34.c:1125-1131 | 85D8C / Coalesce, guard 164878 | BT mgr 87974: save powered→16487F, setPowered/Enabled 0, after 2.5s 130288 |
| carsleeper/bt-on | 4C34.c:1132-1138 | 85E20 / Coalesce | restore powered/Enabled, clear 16487E, 88960(), after 2.5s 1302A8 |
| carsleeper/cell-off | 4C34.c:1139-1145 | 85ED4 / Coalesce | 879E8(0)→164881 (nhớ prior) |
| carsleeper/cell-on | 4C34.c:1146-1152 | 85F08 / Coalesce | nếu 164881 → 879E8(1) |
| carsleeper/airplane-on | 4C34.c:1153-1159 | 85F28 / Coalesce | save BT, 87868(1)→164880, 879A0 |
| carsleeper/airplane-off | 4C34.c:1160-1166 | 85FA0 / Coalesce | 87868(164880) restore |
| settings.changed | 4C34.c:1193-1199 | 862DC / Coalesce | 86338→16487C; on/off → 863E8 / 864C4+88648 (fail → 86E80); update 16487D |
| carsleep.testunblank | 4C34.c:1200-1206 | 86334→8843C / Coalesce | once 1649C8 + off_1649C0(0) + off_1649B0(1.0) force unblank |
### navprovider/voice (715C0 ×1, 7F14C ×13)
| navprovider.relayed | 715C0.c:17-23 | 71664 / Coalesce, guard !started | CNABNavData ingestProvider + publish |
| duodash.navUpdate | 7F14C.c:22-28 | 7F5A4 / Immediate | 83FDC phân biệt duo/true → đọc duodash_nav_data.plist (GMaps) + duodash_waze_nav.plist (Waze) so timestamp → DataRouter submitNav → 82830(navUpdate.relayed) |
| duodash.speedLimit | 7F14C.c:29-35 | 7F974 / Immediate | duodash_waze_data.plist → submitSpeed + write /var/tmp/com.sensetechlab.speed.plist + 82830(speedLimit.relayed) + 84040 |
| duodash.cameraAlert | 7F14C.c:36-42 | 7FBA4 / Immediate | 83FDC→84040 passthrough |
| truedash.navUpdate/speedLimit/cameraAlert | 7F14C.c:43-63 | 7F5A4/7F974/7FBA4 chung / Immediate | Variants TrueDash: truedash_waze_nav.plist + cache 164790 / truedash_waze_data.plist + 164788 |
| navprovider.update | 7F14C.c:64-70 | 7FBBBC→7FBBC / Coalesce | once 1647F8 + async queue 1647C0 12FB10 (ingest) |
| navprovider.rescan | 7F14C.c:71-77 | 7FC04 / Immediate | async 1647C0 12FB30 (rescan BLE/sources) |
| navprovider.selftest | 7F14C.c:78-84 | 7FC4C / Immediate | async 1647C0 12FB50 |
| voicecmd.rescan | 7F14C.c:89-95 | 7FD94 / Immediate | async 1647C0 12FBD0 (cặp notifyd voicecmd.changed) |
| settings.changed | 7F14C.c:104-110 | 7FDDC / Immediate | 80E50 + DataRouter reloadSettings + 7FE78/7FF7C/8009C + async 12FC10 + 7FC94 (full DataRouter+BLE reload) |
| ble.action | 7F14C.c:114-120 | 80468 / Immediate | Sync prefs + hud_paired ? BLEManager pair : unpair (guard 1647C8) |
| latch.reset | 7F14C.c:121-127 | 80574 / Immediate | nếu duodash_reenable_tweaks → unlink DuoDash/*.plist + flag=false + unlink crashreport_collecting + 9DEEC(Idle) + Post(respring.request) |
| respring.request | 7F14C.c:129-135 | 8097C / Immediate | guard duodash_norespring + respring_last throttle 8/60s + carsleep check + 9C790 → touch respring_last + Post(respring.ack) + after 21.6s 12FC70 + 811B0/81624 hoặc async 812F4/81304/81344 |
| crashreport.send | 7F14C.c:136-142 | 80C04 / Immediate | spinlock 1650B0 → async 9DFD4-queue 146158; busy → 9DEEC(Already sending) |
| duodash.mapBgUpdate | 7F14C.c:165-171 | 80C74 / Immediate | duodash_map_bg.jpg check JPEG SOI/EOI → 97564 nếu 1647C8 + write /var/tmp/duodash_map_bg.jpg |
| duodash.mapBgClear | 7F14C.c:172-178 | 80E04 / Immediate | nếu 1647C8 → ImageUploader sendClear |
### license/language/settings UI (8C41C ×2, 8EFE4 ×2, 920C0 ×2, 93A3C ×1, 948C0 ×3, 96D2C ×1, 9B848 ×1)
| license.changed | 8C41C.c:23-29 | 8E0F0 / self CNLicenseActivationController / Immediate | async main 8E190 (refresh activation UI) |
| language.changed | 8C41C.c:30-36 | 8E0F0 chung | Refresh license UI text |
| language.changed | 8EFE4.c:23-29 | 91DCC / self CNNavBubbleSettingsController | 9B314 + async main 91E58 |
| navprovider.listchanged | 8EFE4.c:30-36 | 91DCC chung | Reload navbubble source list |
| language.changed | 920C0.c:23-29 | 933FC / self CNVoiceCmdSettingsController | 9B314 + async main 93488 |
| voicecmd.listchanged | 920C0.c:30-36 | 933FC chung | Reload voicecmd list |
| language.changed | 93A3C.c:20-26 | 93B3C / self CNTweakManagementController | 9B314 + async main 93BC8 |
| ble.status.changed | 948C0.c:148-154 | 96174 / panel once-guard / Immediate | Sync prefs + async main 96DC8 (BLE→UI) |
| language.changed | 948C0.c:156-162 | 96220 / Immediate | 9B314 + async main 96D70 |
| settings.changed | 948C0.c:167-173 | 9635C / Immediate | 962AC() so assoc 164B4B; khác → async main 96480 (tránh loop) |
| respring.ack | 96D2C.c:14-20 | 96D60 / unk_164B58 | byte_164B4E=1 (ack flag) |
| language.changed | 9B848.c:14-20 | 9B87C=thunk 9B314 / unk_164C58 | Global language refresh |

## C. NSNotification local — 8
| CarPlayIsConnectedDidChange | 27E20.c:294-300 | onCarPlayConnChanged: (SBObserver 163A70) | SB poll tick path |
| UIScreenDidDisconnectNotification | 27E20.c:303-309 | onScreenDisconnect: | Screen cleanup |
| UIApplicationDidBecomeActiveNotification | 4CBDC.c:46-52 | onActive: (UIAppObserver 163F28) | Foreground + 8934 uiapp.* + 8CC0 |
| UIApplicationDidEnterBackgroundNotification | 4CBDC.c:55-61 | onBackground: | Suspend |
| UIKeyboardWillShowNotification | 4CBDC.c:102-108 | onKbShow: (KeyProbe 163F68) | Cặp Darwin kbshown/kbframe |
| UIKeyboardWillHideNotification | 4CBDC.c:109-115 | onKbHide: | Cặp kblost/dismiss |
| UITextFieldTextDidEndEditingNotification | 4CBDC.c:116-122 | onEndEditing: | Apply/dismiss decision |
| UITextViewTextDidEndEditingNotification | 4CBDC.c:123-129 | onEndEditing: chung | Variant |
