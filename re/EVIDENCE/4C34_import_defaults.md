# EVIDENCE/4C34_import_defaults.md — P1-3 deep-read (session-003)
_Nguồn: subagent general đọc `4C34.c` (1465 lines) + helpers + strings/pointers. Mỗi claim có file:line + CONFIRMED/HYPOTHESIS/UNKNOWN._

## 0. Helpers đã xác minh
* `sub_84F74(path)->bool` = `NSFileManager fileExistsAtPath:` — `84F74.c:15-20` CONFIRMED.
* `sub_85028(path,str)->bool` = `str+"\n" writeToFile:atomically:encoding:4` (UTF-8) — `85028.c:13-20` CONFIRMED.
* `sub_84FD8()->int64` = `(int64)([NSDate date].timeIntervalSince1970*1000)` ms — `84FD8.c:15-18` CONFIRMED.
* `sub_8509C(domain)->int` = tổng `CFPreferencesCopyKeyList(AnyHost)+CurrentHost` count — `8509C.c:20-37` CONFIRMED.
* `sub_85664(domain,host)->NSDictionary` = `Synchronize + CopyKeyList + CopyMultiple`, nil/empty → `__NSDictionary0__struct` — `85664.c:20-43` CONFIRMED.
* `sub_85748(code,dict)->int64` = code!=0 → 0; else `dict["iat"]` NSNumber → longLongValue else 0 — `85748.c:21-37` CONFIRMED.
* `sub_85800(filename)->bool` = nếu `/var/mobile/Library/TrueDash/<name>` tồn tại thì `remove DuoDash/<name> + copy TrueDash->DuoDash`, return copy-ok; else 0 — `85800.c:22-39` CONFIRMED.
* `sub_8597C(arr)` = chỉ giữ `NSString length>0` qua `NSMutableOrderedSet->array`; non-NSArray → nil — `8597C.c:29-70` CONFIRMED.
* `sub_85B14(dict)` = chỉ giữ cặp `NSString:NSString` — `85B14.c:19-35` + `85BCC.c:19-23` CONFIRMED.
* `sub_85C5C()->NSArray[3]` = `["pane_unload_close_enabled","appbridge_autostart","disconnect_close_enabled"]` — `85C5C.c:13-16` CONFIRMED.
* `sub_85D30(arr)` = `count? join(",") : "none"` — `85D30.c:15-20` CONFIRMED.
* `sub_A3558()` = deviceId cached `qword_1650C0` via `dispatch_once(1650C8)` — `A3558.c:11-13` CONFIRMED.
* `sub_A4450(&dict)` = đọc+trim `DuoDash/license.blob`, verify `A397C(blob,deviceId,"duodash")`; rỗng → 1 — `A4450.c:18-45` CONFIRMED.
* `sub_A4558(TrueDashBlobStr)` = `A397C(...,"duodash")`; nếu 0 thì `mkdir DuoDash + write DuoDash/license.blob`; write-fail → 9 — `A4558.c:20-50` CONFIRMED.
* `sub_A50CC(keyStr)` = `A4744(keyStr) ? A5114(keyStr) : 0`; caller map `!=0 ? "resealed" : "failed"` — `A50CC.c:15-19`, `4C34.c:842-845,894-897` CONFIRMED.

## 1. Guard import.done / import.running (4C34.c:275-293)
* `import.done` tồn tại → `goto LABEL_162` (4C34.c:908), skip import — `4C34.c:275,729` CONFIRMED.
* `mkdir("/var/mobile/Library/DuoDash",0x1ED=493=rwxr-xr-x)` — `4C34.c:277` CONFIRMED.
* `import.running` tồn tại → ghi `import.done="at=<ms> result=aborted\n"`; write-ok → `remove import.running`; rồi `goto LABEL_162` — `4C34.c:280-293` CONFIRMED. Write-fail → giữ lock, vẫn goto (lần sau abort tiếp).

## 2. Pre-check (4C34.c:295-321)
* Inputs: `TrueDash/license.blob` (295), `TrueDash/license.key` (302-306), `8509C(truedash.settings)`, `8509C(truedash.rescuer)` (296-312) CONFIRMED.
* Skip nếu blob absent AND key absent AND settings==0 AND rescuer==0 — `4C34.c:310-314` CONFIRMED.
* Ngược lại viết `import.running="at=<ms>"`; fail → goto LABEL_162 — `4C34.c:317-321` CONFIRMED.
* Strings: `/var/mobile/Library/TrueDash` (1396/0xc23ab), `license.blob/key` (1390-1391), `truedash.settings/rescuer` (1388-1389) CONFIRMED.

## 3. Wipe-then-migrate prefs truedash.settings, loop 2 hosts (4C34.c:322-385)
* `sub_85148(srcDomain,dstDomain,counters*)` — prototype suy từ thân `85148.c:9,73,169,127-142,192-203` (HYPOTHESIS cho mapping arg tại call-site; CONFIRMED cho semantics 4 counters `[copy,renamed,dropped,removed]`).
* Rename map `qword_164860` (off_154718) + denylist `qword_164868` (off_154250), init `85928.c:15-20` CONFIRMED; nội dung dict/set UNKNOWN (cần raw ARM64/`__objc_dictobj` decode).
* Filter: chỉ copy trực tiếp nếu `rangeOfString:"truedash" options:1==NSNotFound` — `85148.c:132-133` CONFIRMED. `truedash_language` (strings 1418), substring `truedash` (1423) CONFIRMED.
* Sub-loop mỗi host (AnyHost rồi CurrentHost): intersect TrueDash dict với `off_154268` → `CFPreferencesSetMultiple(nil,array,"...truedash.settings",CurrentUser,host)+Synchronize` = **xóa keys đã migrate khỏi source** — `4C34.c:341-379` CONFIRMED. Nội dung `off_154268` UNKNOWN (pointers.txt:255, `__objc_arrayobj` 55044).

## 4. License branch (4C34.c:386-906)
* `v19=TrueDash/license.blob, v20=exists; v21=TrueDash/license.key, v22=exists; v23=DuoDash/license.key, v24=exists; old_key="present"/"absent"` — `4C34.c:387-403` CONFIRMED.
* `deviceId=A3558()` rỗng → `licence="no-device-id" (nếu TrueDash có blob/key) else "none"`, blob/key="none", `goto LABEL_91` — `4C34.c:404-415` CONFIRMED.
* TrueDash blob non-empty → `A397C(blob,deviceId,"duodash",&payload)` (`v31==0` valid) — `4C34.c:731-764` CONFIRMED. Pubkey array `off_1542E0` (pointers 279,55054; A397C.c:94-101) HYPOTHESIS.
* TrueDash key 3-valued `"unreadable"/"absent"/"readable"` (A4BC0 read+trim+exists, 766-776); DuoDash key tương tự (778-782) CONFIRMED.
* DuoDash blob verify `A4450` (784-785); so `iat` TrueDash vs DuoDash via `85748` (786-788); ưu tiên `v46=(DuoDash invalid && TrueDash iat < DuoDash iat)` (789-793) CONFIRMED.
* Nhánh A Import (`TrueDash valid && !v46`): `A4558` → blob="imported"/"failed"; TrueDash key rỗng → key="none"/"kept" (theo v24), else `A50CC` → "resealed"/"failed"; licence="imported"; xóa loạt `off_154238` khỏi DuoDash/ — `794-846` CONFIRMED; nội dung `off_154238` UNKNOWN (pointers 311,55040).
* Nhánh B1 (DuoDash invalid + TrueDash có key): xóa DuoDash blob → "deleted"/"none", reseal — `850-866` CONFIRMED.
* Nhánh B2 (DuoDash invalid + TrueDash không key): "none"/"kept" logic theo `v40==1` (empty-blob, HYPOTHESIS khớp A4450) — `868-881` CONFIRMED.
* Nhánh C (DuoDash valid): giữ "kept", reseal nếu DuoDash không key mà TrueDash có — `883-899` CONFIRMED.
* Product strings 3 thế hệ cùng tồn tại: `duodash/license.key/v1|` (6469), `truedash-key v1` (6470), `truedash/license.key/v1|` (6471) CONFIRMED. Import verify blob TrueDash cũ dưới product `"duodash"` (`4C34.c:754`, `A4558.c:23`) CONFIRMED.

## 5. airplay/iconstate/navapps (4C34.c:417-693)
* `airplay_backup.plist`/`airplay_absent`: skip nếu DuoDash đã có; else `85800` copy True→Duo, một cái ok → undo+="airplay" — `419-443` CONFIRMED. Paths strings 1353/1408.
* `iconstate_backup`: copy True→Duo nếu Duo absent + True present → undo+="iconstate" — `445-480` CONFIRMED. Paths strings 1106/1411.
* `navapps.plist` merge (482-685) CONFIRMED: cả hai phải NSDictionary (511-526); hidden union `hiddenByDuoDash ∪ hiddenByTrueDash` (fallback `hiddenByCarNav`), dedup qua NSMutableOrderedSet (527-580); `hiddenClasses` Duo đè True (581-605); ghi `hiddenByDuoDash`, remove `hiddenByCarNav` (606-615); `dashboardModeLastSeen` NSNumber: remove nếu cả hai nil/0 else True-ưu-tiên (616-657); write atomically → undo+="navapps" (671-682). Keys strings 1076/1078/1079/1413-1414/1424.
* Flags `airplay_msrv_pending→"msrv"`, `airplay_uninstalling→"standdown"` via `85800` (686-689); `undo=join(",") or "none"` (690-693) CONFIRMED.
* Chốt: log `at=%lld result=ok settings=%lu renamed=%lu dropped=%lu removed=%lu rescuer=%lu licence=%s blob=%s key=%s old_key=%s undo=%@` → `import.done`, ok → remove `import.running` — `698-727` CONFIRMED.

## 6. Defaults bootstrap (4C34.c:908-1119)
* Guard `stat(defaults.done)!=0` mới chạy — `912` CONFIRMED. Path strings 1426.
* existing = `(airplay marker || settings keys) ? 1 : (import.done existed)` — `914-944` CONFIRMED.
* existing==1: với 3 keys `85C5C` (`pane_unload_close_enabled, appbridge_autostart, disconnect_close_enabled`), keys nào `CopyValue(AnyHost)` nil → seed `CFPreferencesSetValue(key,kCFBooleanFalse,...,CurrentUser,AnyHost)` — **luôn false** — `949-1032` CONFIRMED. `sync ok/failed` (1040-1048).
* existing==0 (fresh): không seed — `946,1052` CONFIRMED.
* Ghi `defaults.done`: existing → `at=<ms> v=1 result=existing why=<import/airplay/keys:N> pinned=<join missing> kept=<join kept> sync=<ok/failed>`; new → `at=<ms> v=1 result=new`; append `\n` UTF-8 — `1054-1114` CONFIRMED. `85D30` chỉ format, không đọc prefs.

## 7. TrueDash = rename/fork kế nhiệm một chiều (HYPOTHESIS mạnh, 6 evidence CONFIRMED)
1. Import một chiều True→Duo duy nhất, không chiều ngược (386-685 + 85800.c). 2. Xóa nguồn sau migrate (SetMultiple nil truedash.settings 367-378; xóa blob cũ 856-860; xóa off_154238 812-832). 3. Layout song sinh đổi prefix (dirs TrueDash vs DuoDash; domains truedash.settings/rescuer vs duodash.settings). 4. Rename map + compat keys (hiddenByTrueDash đọc → hiddenByDuoDash ghi; truedash_language dư). 5. License verify chéo product "duodash" cho blob cũ + 3 prefix key cùng tồn tại. 6. `import.done` once-only; defaults coi import.done là tín hiệu existing.
* Bundle-id TrueDash.app riêng: UNKNOWN (không thấy trong export; chỉ còn domains + `/Library/Application Support/TrueDash/VoiceHandlers` path cũ strings 1342).

## 8. CarSleeper tóm tắt (4C34.c:1121-1273)
* Guard `byte_164878` once (1121-1123). 6 Darwin observers carsleeper/{bt,cell,airplane}-{off,on} → 85D8C/85E20/85ED4/85F08/85F28/85FA0 (1124-1166; strings 1433-1438).
* Nhẹ nếu `168D19!=1 || 9C530("carsleep")!=0` (1167-1173). Full daemon: RadiosPreferences (1175-1177), os_log "com.sensetechlab.carsleeper/daemon" (1178), mkdir CarSleeper + chmod 0x1FD/0x180 (1180-1192), observers settings.changed + carsleep.testunblank (1193-1206), 86338→16487C/D (1207-1209), 863E8 vs 888B4("autolock_prior")+864C4 (1210-1219), 85FB0/86028/86218 (1220-1222), sysctl kern.bootsessionuuid → state.plist {boot_id} (1231-1243), IOPSNotificationCreateRunLoopSource(87D84)+AddSource (1247-1255), `dispatch_after(8s)` nếu 16487C && !87CA0 && !88648 (1256-1268). Paths state.plist/carsleeper.log/suspended_pids.plist (strings 1481-1482,1550,1559).
* SiriProbe once 164A00 + atomic 0xA slots + 7 hooks SiriActivationService + 3 notify_register_dispatch (1279-1385). SBApplication once 164828: dict {com.apple.Preferences: DuoDashPrefsRefresh.dylib} (1401-1414), scan 6 selectors + `rocess/tate`, MSHook `_processDidLaunch:/_noteProcess:didChangeToState:` → 84318/845B8 + dispatch_after 3s (1419-1457).
