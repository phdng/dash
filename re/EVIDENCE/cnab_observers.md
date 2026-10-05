# EVIDENCE/cnab_observers.md — Q-11 ObjC bodies (session-004)
_Nguồn: subagent general đọc decompile + function_index/strings. Mỗi claim có file:line + nhãn._

## 0. Inventory (function_index.txt CONFIRMED)
| Class | Method | Addr | File |
|---|---|---|---|
| CNABCarPlayObserver | onCarWindow: | 0x99d4 | 99D4.c |
| CNABCarPlayObserver | onHostState: | 0x9d64 | 9D64.c |
| CNABSpringBoardObserver | onHostRequest: | 0x1fb5c | 1FB5C.c |
| CNABSpringBoardObserver | onCarPlayUIStatus: | 0x20010 | 20010.c |
| CNABSpringBoardObserver | onHostRequestSplit: | 0x202d0 | 202D0.c |
| CNABSpringBoardObserver | switchCarPlayUIInPlace:gen: | 0x208f4 | 208F4.c |
| CNABSpringBoardObserver | hostSplitL:right:skipEvict: | 0x217ec | 217EC.c |
| CNABSpringBoardObserver | hostSlots:skipEvict:onHosted: | 0x218d8 | 218D8.c |
| CNABSpringBoardObserver | cnabDoCarPlayDisconnect: | 0x227e4 | 227E4.c |
| CNABSpringBoardObserver | onCarPlayConnChanged: | 0x229fc | 229FC.c |
| CNABSpringBoardObserver | onScreenDisconnect: | 0x22a8c | 22A8C.c |
| CNABSpringBoardObserver | carPlayPollTick | 0x22ad0 | 22AD0.c |
- Đăng ký: CarPlay side 163EC.c:131-136 (CarPlayObserver.new→1635F8 + 887C host.state→onHostState:, carwindow→onCarWindow:); SB side 27E20.c:283-311 (SBObserver.new→163A70 + 887C host.request→onHostRequest:, .split→onHostRequestSplit:, cpui.status→onCarPlayUIStatus: + NSNotification CarPlayIsConnectedDidChange→onCarPlayConnChanged:, UIScreenDidDisconnect→onScreenDisconnect: + carPlayPollTick một lần).
- **887C = NSDistributedNotificationCenter addObserver** (887C.c+8900.c); **8D78 = postNotification deliverImmediately:=1** (8D78.c). 5 notify appbridge.* = NSDistributed + userInfo NSDictionary (HYPOTHESIS cross-process SB↔CarPlay, entitlement chưa đọc).
- Tất cả 8 methods `void`, NSNotification handler hoặc poll — header từng file CONFIRMED.

## 1. onHostRequest: (1FB5C.c, 214 dòng FULL)
- Input: a3 userInfo (nil→empty dict, 66-71). Keys: `bundleIdentifier` (nil→"?", 72-77), `activate`→bool (78-80), frame quartet via 27670 (frameX/Y/W/H, frameWinValid, cpWinW/H, frameWinX/Y/W/H) (81-84; 27670.c). Không đọc bundleIdL/R/C, skipEvict, envOnly, cpui*, carWin*.
- Branch: ++163980 (85); DDz2.shared + DDz1.shared (86-88; semantics HYPOTHESIS: DDz2=overlay/host state, DDz1=shell/view).
  1. !activate → DDz1 hide → LABEL_10 (89-92).
  2. bid=="__spike__" → showSpike + 9424(showSpikeResult) → LABEL_11/22 (94-112).
  3. DDz2 active && !splitHosting && hosted==bid → fast re-present (27B08→setAppContentFrame→carPlayUsableBounds→369E8→present→renderSize→89D8→9424) → LABEL_11/22 (113-148).
  4. Fallthrough: DDz2 active→dismiss (151-152); !prepareShell→LABEL_10 (153-154); 27B08→...→hostBundleId:renderSize: → nil→LABEL_10 else showWithHostView→9424 → LABEL_11/22 (155-194).
  5. LABEL_22 (success): bid non-empty → build [bid] + 7B6D8() (195-206). LABEL_11: 4D0F4("host.request") (208, gated logger byte_164440). LABEL_10: 9424(0,...Zero) (166-177).
- State: ghi duy nhất 163980++ (85). Không CFPrefs/file trực tiếp. Gián tiếp: 89D8 phát uiapp.state, 9424 phát host.state (mọi exit đều ack SB→CarPlay: 98,134,167,182 + 9424.c:102).
- Transform: không số học trực tiếp; 27670 decode frame, 27B08 intersect frame∩usableBounds (loại null/<40pt, set off_162E68 "single-app"/"single-app+dock"), 369E8 (HYPOTHESIS log frame), 89D8 build uiapp.state 8 keys (89D8.c:29-56).
- Không kill/notify_post/file-write trực tiếp. Mọi error graceful, không throw/retry.

## 2. onHostRequestSplit: (202D0.c, 272 dòng FULL)
- Input: userInfo double-read (frame v7 + split keys v17, nil→empty, 89-112). Keys: `bundleIdL` (113), `bundleIdR` (119), `bundleIdC` (125, nil→@""), `activate` (131-133), `skipEvict`→v69 (134-136), `envOnly`→v70 (137-140). Frame → cache 163998/9A0/9A8/9B0 (96-104). Entry: dword_162E70-- nếu >=1 (87-88, debounce).
- hostedSlotBids (141-143); count==0 → fallback từ hostedBundleId/hostedBundleId2 (144-177).
- activate (179): ++163980, retain L/R/C (183-188); envOnly==1 → build {L,R,C} → switchCarPlayUIInPlace:gen: → true thì short-circuit bỏ hostSlots (189-196; intent HYPOTHESIS); else đọc `/var/tmp/duodash_ab_reapdelay` trim+doubleValue clamp (0,60] else 0.0 (198-224) → hostSlots:skipEvict:onHosted:(new3, skipEvict, block 279F4+reapdelay+old) (225-238) → dispatch_after(reapdelay, main, 27AC8 gen-check) (239-246).
- !activate (257-264): ++163980; sub_23454() (=exists split_deactivate_dismiss, 23454.c) → DDz2 dismiss; DDz1 hide; 4D0F4("split.deactivate"); 76224.
- Không nhánh __spike__. Không post host.state trực tiếp (ack trong callees). Không CFPrefs trực tiếp. `layout` produce nhưng không đọc trực tiếp (UNKNOWN downstream). Malformed reapdelay→0.0 (dispatch ngay).

## 3. onCarPlayUIStatus: (20010.c, 91 dòng FULL)
- Input: userInfo đọc 4 lần: `cpuiGen`→ULL (35-36), `cpuiBid` (40), `cpuiOk`→bool (43-45), `cpuiWhy` (48). Guard bid NSString&&length>0 else early-return (50-51,88-90).
- Build block 37924(bid,gen,ok) (=DDz1 noteCarPlayUIStatus:gen:ok:, 37924.c) → main-thread trực tiếp else async (53-68).
- Failure tracking: !ok && gen+1==162E60 (69): lazy NSMutableSet 163990 + 163988=gen khi nil/khác gen (71-80); !contains bid → add + 85B8(bid) (81-85). 85B8 loại bid khỏi split-UI prefs (85B8.c). Mỗi (gen,bid) prune một lần (intent HYPOTHESIS "evict bad split app"). 162E60 nguồn set UNKNOWN.
- Không file/CFPrefs trực tiếp (gián tiếp 85B8→84D8). Không post/kill. void.

## 4. onCarPlayConnChanged: (229FC.c, 27 dòng) + onScreenDisconnect: (22A8C.c, 16 dòng)
- ConnChanged: userInfo["CarPlayIsConnectedDidChange_IsConnected"]→bool (15-18); true→7BCBC("...") (gated logger 164710/164709) else cnabDoCarPlayDisconnect:"..." (20-26).
- ScreenDisconnect: bỏ qua a3; !DDz1.carPlayConnected → cnabDoCarPlayDisconnect:"UIScreenDidDisconnect" (11-15).
- Cả hai void, không transform/globals.

## 5. carPlayPollTick (22AD0.c, 110 dòng FULL) + cnabDoCarPlayDisconnect: (227E4.c, 64 dòng)
- PollTick: truth = DDz1.carPlayConnected (26). Ghi byte_1652B0=v3 + qword_1652B8=uptime atomics (27-31).
- Transition (32-40): prev!=1 && now==0 → disconnect:"poll"; prev==0 && now==1 → 7BCBC("poll: reconnected").
- Connected (41-72): prev!=1 → 163A68=5 + notify_post(cpconnect Darwin, 45-46); retry 163A68: label poll.retry/connect/bringup → 365D4("label#N",1) N=6-163A68; true→=0 else-- (48-71; 365D4 body UNKNOWN, HYPOTHESIS bringup attempt). Disconnected → 163A68=0 (76).
- Flush UI: 163C40>0 → 371AC (main) else async 12D548 (78-93, UNKNOWN); connected → 370F8 (main) else async 12D4F8 (95-100, UNKNOWN).
- Cuối: 162E74=v3 (prev), dispatch_after(3s, main, 22D5C=self) self-rescheduling (102-109). Không userInfo/CFPrefs/file/kill trực tiếp.
- Disconnect (227E4): reason → 76224 + 7B924 log (21-33); async queue 165118 146308 nếu có (34-35, UNKNOWN); 163C40>0 → 371F4 else async (36-44); **chỉ khi DDz2.active**: dismiss + DDz1 invalidateForDisconnect + notify_set_state(162DD8,0) + zero xmmword_163A98/AA8/AC0+qword_163AD0 + notify_post(cpdisconnect) + 4D0F4("CarPlay disconnect") (45-61). Inactive → chỉ log. Không kill trực tiếp.

## 6. onCarWindow: (99D4.c, 119 dòng FULL)
- Input: userInfo isKindOf NSDictionary else nil (42-47). Keys: `bundleIdentifier` (48), `carWinW` (49), `carWinH` (50), `carWinPid` optional (51). Gates lồng: bid NSString→W/H NSNumber→doubles (52-69); guard length>0 && W,H>=1.0 else return (71).
- Lazy NSMutableDictionary 1635B8 (size) + 1635C0 (pid) (73-88). pid đổi → remove 1635C8[bid] (89-92; 1635C8 init chưa thấy — HYPOTHESIS throttle map, nil-safe).
- Ghi 1635B8[bid]=CGSize value (93-95); pid>=1 → 1635C0[bid]=@(pid) (96-101). Lookup 13AB8 (lock 163648, đọc 163510/163518) → bool (102-104); counter 163640 cap 59. Nếu found → 127F0(bid) (105-106): debounced nudger — skip nếu `/var/tmp/duodash_cpui_nonudge`, CACurrentMediaTime>=1635D0[bid]+?, 12C48 rect, 1635D0[bid]=now+4.0, after 1s → 12D84 (127F0.c).
- Không frame*/cpui*/CFPrefs/post/kill/UI trực tiếp.

## 7. onHostState: (9D64.c, 775 dòng, 3 chunks)
- Branch 0 hostRefused: userInfo["hostRefused"]→bool (198-202); true → refuseReason (else "?", 745-753); nếu 163688==1 && 1635E8==1 → rollback snapshot (1635E8=0, 1635F0=163689, restore 1634B8/C0/C8←1634D0/D8/E0, 162DE8←163690, 163628←1636C8, B144("host refused"), 754-769; HYPOTHESIS rollback) → LABEL_139 (773-774). false → 1635E8=0 (205) → normal.
- Normal header: sbPid→1635EC (206-214), activated→v131 (215-219), bundleIdentifier→v128 (220-222). !activated → B8F8(nil) → LABEL_20 (738-743). empty/__spike__ → LABEL_20 (223-229). 1635F0==1 → async B768(bid) (231-246, UNKNOWN).
- LABEL_20 cpuiBid/cpuiGen/cpuiKilled: v126 (249), v137 ULL (252), cpuiKilled dict enumerate (NSString non-empty + NSArray filter int>=1 → v133, 256-336) → 163570=cop
...[truncated 6150 chars]