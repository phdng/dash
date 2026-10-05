# EVIDENCE/prefs_split_autostart.md — P2-1 + P2-4 deep-read (session-004)
_Nguồn: subagent general đọc decompile/*.c + memory/strings/pointers. Mỗi claim có file:line + nhãn._

## 1. Central resolver sub_74C8 (74C8.c:9, void, callers 746c/84d8/27e20/29198/56b24/5f8a4/637e8/69824)
Publisher duy nhất `notify_post(resolved)` (419) + ghi `/var/tmp/com.sensetechlab.appbridge.plist` (416).

### Phase 0: clearpanes one-shot (100-206)
- Inputs: `/var/tmp/duodash_ab_clearpanes` (mtime) + `.done` (string double) (105,113).
- `clearpanes` tồn tại → đọc `.done` (length!=0 ? doubleValue : 0.5, +0.5) (118-126); nếu `mtime > done+0.5` (128): ghi `.done="%.3f"` (130-137), xóa 8 keys `split_left/right/third, layout, frac_a/b/frac_layout, carplay_ui/_more` về nil (139-192), Synchronize (193), removeItem clearpanes (197-201).
- Error: attributes/fileModificationDate nil → skip (109); `.done` missing/empty → v5=0.5 (124).

### Phase 1: fontFloor + keypane
- `AppSynchronize` (207), `7EA4()` (208), `8058()` (209). Thứ tự cố định.

### Phase 2: bridgedApps (210-271)
- `GetAppBooleanValue(appbridge_enabled)` (211), `CopyAppValue(bridgedApps)` (215); non-NSArray → empty (218-222).
- Filter `74C8.c:251-252` hiển thị đảo (add non-string/excluded vào v16) — HYPOTHESIS decompiler artifact; ground truth = `7E908.c` + `7E568.c`.
- `appbridge_autostart` raw CopyValue (272-276), CFRelease (278-279); `v66=85CDC()` (277; arg inline v24 — HYPOTHESIS như 7BB90.c:20).

### Phase 3: off_154208 (10 keys, count CONFIRMED từ memory 00154070: isa=0x169258, count=0x0A, backing=0x153A48) → v25 dict (280-310) → `v34=7E908(v25)` (311) → panes[0/1/2] (312-320), ratio/layout/fracA/fracB/fracLayout/cpuiMain/cpuiMore/fixes (321-330).
- 10 keys HYPOTHESIS mạnh = split_left/right/third, layout, split_ratio, frac_a/b/frac_layout, carplay_ui, carplay_ui_more (consumer-side CONFIRMED 7E908.c:56-88,89,117).

### Phase 4: publish CHÍNH XÁC 14 keys (dictionaryWithObjects:forKeys:count:14, 375-381)
| # | key | value |
|---|---|---|
|0|appbridge_enabled|numberWithInt(!((AppBool)? keyExists==0 : 1)) → 1 iff true AND exists (331-337)|
|1|bridgedApps|filtered array (338,341)|
|2|appbridge_split_enabled|**kCFBooleanTrue hằng, không điều kiện (339,342)**|
|3-5|split_left/right/third|panes[0/1/2] (343-351)|
|6|split_ratio|numberWithInteger (352-354)|
|7|layout|numberWithInteger (355-357)|
|8-10|frac_a/b/frac_layout|(358-366)|
|11|autostart|numberWithBool(85CDC()) (367-369)|
|12-13|carplay_ui/_more|(370-374)|
- Sau đó mutableCopy (382) + `navprovider_selected` (CFString else "", 391-406) + `navprovider_autostart` (407-414) → plist 16 entries, core 14.
- Side-effects: writeToFile atomically:1 (416), CFRelease (417-418), notify_post(resolved) (419). Không synchronize cuối.

## 2. sub_7EA4 fontFloor (7EA4.c:9, callers 74c8/291f4)
- File `/var/tmp/duodash_ab_fontfloor_force` (28) ưu tiên nhất: trim (37), all-digits (41-49), integerValue (53), clamp <97→0 (54-57). Force-file rỗng = giữ 0, không đọc prefs (62-65, HYPOTHESIS intent: disable floor).
- Prefs `bridged_font_floor` (67): nil→0 (88); non-CFNumber→0 (82); CFNumber→int + clamp (74-78).
- Output `qword_163448` (91-92). 0=OFF, >=97=ON. Consumers: 6AFC4(==27)/6AFE8(==19)/6B00C(!=0)/87F0(store).

## 3. sub_8058 keypane (8058.c:9, callers 74c8/29400)
- `ret!=0 → 1; else exists==0 → 1` (20-28): true→1, false-explicit→0, **missing→1 (default ON)**.
- Output `byte_162DDC` (29). Consumer 38240.c:83. Publisher 29400 push `keypane_enabled` qua 8C28(uiapp.keypane) (31,60,71); log "switched OFF" khi 0 (32-33).

## 4. sub_746C layout setter (746C.c:9, callers 2565c/51f18/67c38)
- Guard `(result-9)>=0xFFF...F8` = chấp nhận **1..8** (HYPOTHESIS từ wrap-unsigned), reject còn lại.
- Pass → SetAppValue(layout)+Synchronize+74C8() (15-20). Fail → return nguyên, không sync/republish (21).

## 5. Helpers
- **85CDC(a1)** (85CDC.c:9, callers 74c8/7792C/7BB90): nil→1; else CFBoolean&&value!=0. **Missing = TRUE** cho autostart/pane_unload/disconnect. NSNumber 1/0 → FALSE (trap!).
- **7E63C(a1,a2,a3,a4,*a5)** (7E63C.c:9): nil→default a4, *a5=0; NSNumber non-float→1; NSString coerce→2; float/khác→3; range [a2,a3] trong→giữ class, ngoài→3+default. Mã: 0=missing,1=num-ok,2=str-ok,3=error. Callers bounds: 8154 (0,99,0), 81EC (0,8,0); 73E8/80D0 mất args (HYPOTHESIS (0,N,0)).
- **7EEDC** (7EEDC.c:9): objectForKey→7E63C→nếu (v23&~1)==2 ghi NSNumber vào writes + fix-name vào fixes (25-34). Dùng cho layout/ratio/frac_* (7E908.c:84-88).
- **7E568** (7E568.c:9): non-NSString/empty→nil; else dispatch_once + containsObject qword_164758 (19-21). Blacklist nội dung UNKNOWN. Dùng 74C8.c:251, 7E908.c:65,99,137.
- **7E730(a1=more,a2=main)** (7E730.c:9, callers 70FC/84D8/7E908): non-NSArray→empty (74); giữ element iff NSString+non-empty (54-55) + khác main (56) + chưa có (57). Giữ thứ tự, dedup.
- **7044(key)** (7044.c:9): đọc plist (19-23), trả về iff NSString&&length!=0 else nil (26-37). Missing-file/type-mismatch→nil.
- **70FC()** (70FC.c:9): carplay_ui+_more (23-28), main non-string→nil (29-33), return 7E730(more,main) (34).
- Consumer lớn **17410.c:118-265**: enabled→163770 (boolValue else 0), bridgedApps→163450, split L/R/T→163458/60/68, ratio/layout via 80D0/73E8, frac_a/b via 8154, frac_layout via 81EC, autostart→163809 via 836C, carplay_ui→163470 + more→163478, diff→F654 cleanup, publish cpcount notify (258-265).

## 6. 7E908 panes compute (7E908.c:9, callers 74C8/27E20)
- Slots split_left/right/third (base off_12FA78, 53-56): nil→""; non-string→fix type; 7E568==1→fix excluded; empty-string giữ "" không fix (64-78, HYPOTHESIS "trống hợp lệ"); non-empty dup→fix dup:i + "" (66-72). writes[slot]="", fixes+=...
- Numerics via 7EEDC (84-88). cpuiMain: nil/empty→"" không fix (91-114); non-string→fix; giữ iff 7E568==0 && contains(panes) — **phải trùng một pane** (99-108). cpuiMore: 7E730 merge (124), giữ iff excluded==0 && contains(panes) (137-138); raw!=filtered → writes+fixes+=cpui_more (150-158, self-healing; 27E20.c:595-651 ghi ngược prefs khi count!=0).
- Output ABCfgResult{panes,layout,ratio,fracA/B/Layout,cpuiMain/More,writes,fixes} (83-162).

## 7. Split behavior
- split_enabled luôn YES ở resolved plist; on/off thực tế do consumers (panes rỗng / appbridge_enabled=0 — nửa sau HYPOTHESIS).
- 746C chỉ đổi layout 1..8 + auto-republish.
- **84D8.c:9-31** setter carplay_ui/more: main empty→"", more nil→[], more=7E730, SetAppValue cả 2, Synchronize, 74C8(). Callers 85B8/5F8A4/628F4.

## 8. Disconnect-close 12s (7B9EC/7BB90/7BC14/7BD58)
- Arm 7B9EC (callers UNKNOWN): default **12s** (12000000000ns, 7B9EC.c:27); override file `/var/tmp/duodash_ab_discoclose_secs`: trim+doubleValue, chấp nhận [0,120]s (37-50); 0 = fire ngay.
- Arm gate (25): `7BB90() && stat(nodiscoclose)!=0 (VẮNG) && count(1646F8)!=0`. Thiếu một → không arm.
- **7BB90()** (7BB90.c:9): Sync+CopyValue(disconnect_close_enabled)+85CDC → **missing=TRUE**. Chỉ CFBoolean false mới disable.
- Fire gate 7BC14.c:19-27: gen match (else stale), `!carPlayConnected && 7BB90() && nodiscoclose vắng` mới kill. Reconnect trong 12s → skip.
- Cancel 7BD58: byte_164708==1 → =0, ++164700 (stale timer). Caller UNKNOWN (HYPOTHESIS: connect path).
- Tracking list 1646F8: set tại 7B8E4 (từ paneactivity), qua 7B6D8→7B924 dispatch, gate byte_164709==1 + dedup (7B6D8.c:34,58-64,72-78). Sau kill: 1646F8=0 (7BC14.c:32-33).
- Kill: **7BC14.c:31 → 763E0(v3,"carplay.disconnect",0)**; **763E0.c:247 `kill(pid,9)` = SIGKILL**. Dry-run a3!=0 chỉ log (245-286). Skips: noreap tồn tại (92), Preferences/duoDash protected (126-142), phone-frontmost (144-157), unresolvable-path (199-208), proc_pidpath mismatch (243). SBApplicationController chỉ resolve bundleURL→path (76BF4.c:30-60). FBScene không liên quan kill.
- ON: key true/missing + không nodiscoclose + panes non-empty + vẫn disconnected sau 12s → SIGKILL tracked. OFF/reconnect/list-rỗng → skip.

## 9. pane_unload_close (7792C.c:9 + 763E0 + 85C5C)
- Gate (115-133): Sync + CopyValue(pane_unload_close_enabled) + 85CDC (missing→1) (119-126); `stat(noreap)` vắng + `carsleep/sleeping==0` (128-133). Thêm once 1646A8/1646A1==1 (97-99) + isMainThread (101).
- Inputs a1=oldPanes, a2=newPanes (nil→[], 103-114). v63 = old−new (string, non-empty, dedup, 135-203). count==0 → release, hết (204,365-368).
- Trừ phone-frontmost via 76AF8 (SpringBoard _accessibilityFrontMostApplication, 76AF8.c:18-35; 206,229-241): frontmost → chỉ log, không kill.
- Resolve 76BF4 (272): fail → LABEL_92 bỏ toàn batch (275-279). 76BF4 dùng SBApplicationController applicationWithBundleIdentifier → bundleURL/info.bundleURL → path (30-60); return 1 khi app không cài (74).
- Enumerate 76E08 (295): sysctl KERN_PROC_ALL, lọc pid!=self + proc_pidpath chứa /Applications/ hoặc /containers/Bundle/Application/ + ".app/" không "/" sau (38-103). Lỗi → -1 → bỏ kill (296).
- Kill: proc_pidpath==expected && !kill(pid,9) (319-321) = SIGKILL, log "%@ (pid %d)".
- OFF-path: v7==0/noreap/sleeping → async main 78224(copy old,new) (379-392); 78224 gọi lại 7792C (defer một lần). 1646A1!=1 → drop (99-101,393).
- ON + unload + !frontmost + !noreap/sleeping → SIGKILL; else defer/drop.

## 10. Autostart trigger
- **Tweak không post autostart.changed** (grep 0 hit notify_post) — chỉ observe tại 27E20.c:340-343 → 29198 (74C8+792C4). External (prefs UI) đổi → republish.
- Toggle UI 637E8.c:14-22: đọc 836C, flip CFBoolean, SetAppValue+Sync+74C8+refresh/watchdog. **836C đọc resolved plist** (boolValue, nil→0, 836C.c:20-24) — khác 74C8 đọc raw prefs via 85CDC (nil→1): hai tầng default khác nhau.
- Trigger sau connect: **1A820** (callers:none): gate không `noautostart` + 163809==1 (từ 836C via 17410.c:168) + 1635F0==0 + 16380A==0 + một pane non-empty (18-26). Throttle uptime-last>=30s (32), 163630=now, 19330(0,0) (34-35). **"Sau connect mấy giây" UNKNOWN** — không thấy caller/scheduler (HYPOTHESIS gọi từ connect/timer ngoài, không qua Darwin notify vì không có AddObserver(1A820)).
- Nhánh navprovider riêng: 116D4.c:20-63 (cache 2s/60s + knob nodashkeep); 19330.c:81-120: 116D4==0/flags → 196B0 ngay, else resolve navprovider_selected via 7044, knob nodashlaunch (90), dispatch 0.55s (117). Không phải appbridge_autostart.
- Delays khác (tránh nhầm): 291AC 0.35s, 29748 1s, 17204 throttle 1s + cache 2s.

## 11. ON/OFF matrix
- split_enabled: luôn YES resolved; tắt = enabled=0/panes rỗng (nửa sau HYPOTHESIS).
- pane_unload_close missing→ON; ON→SIGKILL unloaded (trừ frontmost/protected/noreap/sleeping); OFF→defer/drop.
- disconnect_close missing→ON; ON→arm 12s (0-120s override), hết timer vẫn disconnected→SIGKILL tracked; nodiscoclose/reconnect/rỗng→skip.
- Cả hai kill bằng kill(pid,9) sau sysctl+proc_pidpath verify; không SBApplication terminate/FBScene/exit() ở hai path này (grep CONFIRMED).
- appbridge_autostart missing→1 (republish) nhưng 836C missing→0; ON cho 1A820→19330 (throttle 30s); OFF/noautostart→không launch. Scheduler 1A820 UNKNOWN.

## 12. Partitioning UNKNOWN cần runtime
- Blacklist 164758 (7E568). 10 keys off_154208 (count CONFIRMED, mapping HYPOTHESIS). Caller/scheduler 7B9EC/7BD58/1A820 (callers:none). Bounds 73E8/80D0 (mất args). 74C8.c:251 đảo logic (dùng 7E908 làm ground truth).
