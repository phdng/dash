# EVIDENCE/hosting_engine.md — Q-11A hosting engine (session-007)
_Nguồn: subagent general đọc FULL 218D8 (717 lines, 2 passes) + 208F4 (624 lines, 2 passes) + 217EC (42) + 279F4 (35) + 27AC8 (14) + helpers. Mỗi claim có file:line + nhãn._

## 1. hostSlots:skipEvict:onHosted: (218D8.c:9-14)
Signature `(self,a2,a3=bids-array,a4=skipEvict-bool,a5=onHosted-block-or-nil)`. a3: caller 202D0:226-229 build [L,R,C]; caller 217EC:33-37 build [L,R]. a4 từ userInfo["skipEvict"] (202D0:134-135 → :237). a5: 202D0:237 truyền 279F4-block; 217EC:40 truyền 0. Copy a5 tại :177/:630, truyền A8424 tại :647.

### Tiền kiểm tra dirty / reshow-vs-full-host
- Singletons DDz2 (:175) + DDz1 (:176). v117 = !active || isSplitHosting-flip (:178-182). v12 = slot-count kỳ vọng từ 162E90 qua bảng BA7C8, default 2 (:183-187). So 1639C0 vs v12, 162E90 vs 73E8() (:188-199); 73E8 đọc plist appbridge_layout + 7E63C (73E8:15-24).
- Layout khớp (v14==1): validate bids: hostedSlotBids + hostedSlotIsCarPlayUI (:204-205); 3DD4C(v6,v12,1,v16) normalize (SBApplicationController check, dedup, rỗng nếu CarPlayUI — 3DD4C:34-99); loop từng slot isEqualToString + size unk_1639D0>=1.0 (:210-236); v27==1 identical; 22D64 shell-bounds check (:243-263, 22D64:25-48); flags word_163A00/bit0/bit8/byte_163A02; mismatch → v28=1 (:298-303); so CarPlayUI flags cũ/mới via 22E40 (eligible flags: carplay_ui + entitlements 7DBDC + carPlayConnected + !nocpui — 22E40:76-286) (:264-296).
- Quyết định (:307-313): `23454() || !active || !isSplitHosting || visible || 1639B8!=1639BC || v28 || !present` → full-host, else reshow. 23454 = exists split_deactivate_dismiss (23454:15-19).

### Nhánh full-host (:314-654)
- carPlayUsableBounds → CGRectIsEmpty (:315-320). Empty + !prepareShell → 97A0("no-display") + LABEL_115 return (:321-327). 97A0 post host.state {hostRefused=1,refuseReason} via 8D78 (97A0:17-34).
- Geometry 23D94(...,163998..1639B0) (:338-345); w<1||h<1 → degenerate-content → 97A0 (+discardHiddenShell nếu trước đó empty) (:347-352).
- Reset globals split/panel (:359-378): word_162ED8=256, byte_162EDA=2, word_163C18=0, 162E90=2, 162E98/162EA0=-0.5, 162E80/162E88=50...
- Đọc /var/tmp files (KHÔNG CFPrefs/NSUserDefaults, grep 0 hit): nopanepad → defaults cứng (:381-392); panepad → double clamp (0,40] else 4.0 → 162EA8 (:395-415); nopaneround → 13.0 vs 0.0 → 162EB0 (:416-420); **layout → integer clamp 1..8 else 2, rỗng → 73E8(); set 162E90 + byte_163AF2** (:421-444, match `layout` duy nhất); panefracs → parse "a,b" → 163AF8/163B00/163B08, rỗng → 81EC()+8154 (:445-501); paneratio + noratio → 1..99 else 50, flags 163AF1/163AF3 (:502-549).
- 365D4("panel.host",0) (:552). Async log hình học nếu xmmword_163AC0>=1 + queue 1652F0 ("%.2f|..." + async ABB7C, :560-600). Tăng gen 163980/163978 (:601-602).
- Block 2410C (v138, unk_12D348) captures: v139=DDz2, v140=DDz1, v141=onHosted-copy, v145/146=content-size, v147/148, v149-152=usable-bounds, v153="?", v154=a4(skipEvict), v155=v117, panel/pane params, v137="host" (:609-647). A8424(&block,v92,v138) (:647): dispatch_async queue 165118 (A8628) nếu có else sync A850C(v5,0,4) (A8424:34-59).
- skipEvict (a4) chỉ đi đường async này (v154 → a1+168 tại 2410C:721), KHÔNG ở nhánh reshow (grep a4 chỉ 3 hits: decl 13, copy 174, v154 628). Cơ chế ức chế evict trong 2410C/2565C — UNKNOWN. Slots/evict/thứ tự ủy quyền async 2410C; thứ tự L/R/C = index order HYPOTHESIS.

### Nhánh reshow (:656-710, khi hosting + visible==0 + identical + !23454)
- hostedOrientation (:659). Loop tối đa 3 slots (clamp 2, :662-690): slot bid non-empty + chưa push (163D48/163D50 guard) → 89D8(bid,1,orientation,1,w,h), size từ xmmword_163D90 fallback unk_1639D8.
- 70248() (:691, HYPOTHESIS flush geometry). 234A0(DDz2) lấy cpuiBid+cpuiMore; 23AB0 lấy bundleIdentifier; 162E60++ làm cpuiGen (:696-699). 9424(1,...) post host.state (:700; dict 9424:45-102). 4D0F4("host.request.split.reshow") (:706). Không dùng skipEvict/onHosted.

### DDz/IPC/globals/errors
- DDz2: active/isSplitHosting/hostedSlotBids/hostedSlotIsCarPlayUI/hostedOrientation/dismiss. DDz1: visible/present/carPlayUsableBounds/prepareShell/discardHiddenShell:.
- IPC: 9424→8D78 (host.state), 97A0→8D78 (refused), 4D0F4, 365D4, A8424 dispatch. notify_post/CFPrefs/xpc vắng mặt (callees + grep 0 hit).
- Errors: no-display, degenerate-content (+no-display-postanswer tại 2410C:871).

## 2. hostSplitL:right:skipEvict: (217EC.c:10-42)
Sig (self,a2,a3=L,a4=R,bool a5). Nil-coalesce → @"" (:26-32). Build [L,R] arrayWithObjects:count:2 (:33-37). Gọi hostSlots(...,0) (:40, onHosted=nil). Không slots/evict/DDz/IPC/globals/files/error riêng, không `layout` (callees chỉ 218D8 + runtime; grep 0 hit). = wrapper split 2-pane (HYPOTHESIS).

## 3. switchCarPlayUIInPlace:gen: (208F4.c:9-14)
Sig bool (a3=bids-array, a4=gen→25EDC). Return 1=đã xử lý/accept (kể cả rollback một phần), 0=từ chối early/mismatch (:203-206,240-242,605,623).
- Guards (:170-206): từ chối nếu !active || !isSplitHosting || !visible || swapInFlight || maximizedPosition<0 || maximizeInFlight || 163978!=0 || 1639B8!=1639BC || 162E90!=73E8() || hostedSlotCount(1..3)!=1639C0 || !=BA7C8-map || 1639C8<slotCount || word_162ED8!=0x0100 || byte_162EDA!=2 || word_163C18&0x101. Tiếp: bids mới khớp hostedSlotBids + size>=1 (:207-237); 22D64 false (:238) else LABEL_109 return 0.
- Phân loại slots (:244-291): v105=22E40 eligible flags, v104=hiện CPUI. Loop: obj (!eligible && !CPUI → convert); v102 (eligible && !CPUI → HYPOTHESIS replace pane); v99 (eligible && CPUI && word_163A00[i]==1). v112 = bids obj non-empty; v107 = eligible-nonempty (292-348).
- Convert: mỗi obj → convertSlotToCarPlayUI: fail → rollback setSlot:carPlayUI:0 đã làm + return 1 (:368-380); ok → 26F60 tạo view + replacePaneAtSlot:withView:native: (w,h từ unk_1639D0), fail → rollback (:369-408); ok → addObject + word_163A00[slot]=1 (:409-410). Mỗi v102 tương tự (:431-450). Có thay đổi → rebuildMatForEnvironment (:457-460). Index order giữ nguyên (HYPOTHESIS). Evict = setSlot + replacePane + 85B8 trong continuation 26FE4 (HYPOTHESIS).
- Hoàn tất async (:461-605): v100=mutableCopy(v112) + merge v102 bids (:461-491); v95=77244(v100) else empty (:492-495, HYPOTHESIS resolve display items); v72 = v95 + 163970 pending cũ dedup + merge v107 (:502-540); 763E0(v100,"cpui switch in place (R3)",0) nếu có (:542-543); v93=2595C(v72,v83) (killed set? HYPOTHESIS); block 26FE4 captures (DDz2,DDz1,v81,v82,v80,v83,v112,v72,v97,v93) (:544-573); v87(v72).count → 163970=copy + 25EDC(v87,gen,20,0,0,0,block) delay 100ms → 25FE0 (25EDC:15,28-41), else gọi block trực tiếp (:574-584).
- 26FE4 continuation: clear 163970, yêu cầu active&&split&&visible&&carPlayConnected, 7764C check, 85B8 evict, setSlot:carPlayUI:1/0 + spikeCreateSlot: + replacePaneAtSlot: + scheduleGeometryPushesForSlot: + rebuildMatForEnvironment + 9424(1,...,cpuiGen=162E60++) + 4D0F4("split.cpui-in-place") (26FE4:81-260).
- DDz calls: hostedSlotCount/active/isSplitHosting/visible/swapInFlight/maximizedPosition/maximizeInFlight/hostedSlotBids/hostedSlotIsCarPlayUI/convertSlotToCarPlayUI:/setSlot:carPlayUI:/replacePaneAtSlot:withView:native:/rebuildMatForEnvironment/spikeCreateSlot:/scheduleGeometryPushesForSlot:. IPC gián tiếp 26FE4→9424→8D78 + 4D0F4. notify_post/CFPrefs vắng. Không đọc /var/tmp/* (grep duodash_ab_ 0 hit); globals 162E90/1639C0/1639C8/163978/1639B8/1639BC/162ED8/162EDA/163C18/163A00/1639D0/163970/1652Fx.

## 4. 279F4 (onHosted block, 202D0:230-237) + 27AC8 (delayed verify, 202D0:239-246)
- 279F4(a1=ctx,a2=host-result) (9-10): captures *(a1+32)=old-bids snapshot, *(a1+40)=delay double từ reapdelay file (trim, 0<delay<=60 else 0.0 — 202D0:198-225). Logic: v4=163980 hiện tại, dispatch_after(delay, main, 27AE4{v10=v4,v8=old-bids,v9=a2}) (:22-31). Chỉ schedule, không slots/DDz/IPC đồng bộ.
- 27AE4: result[6]==163980 → 7792C(result[4]=old, result[5]=new) else no-op (11-13). 7792C reap/kill bids thay thế (pane_unload gate + noreap + sleeping + proc_pidpath+kill(9): 7792C:115-355).
- 27AC8 block gen=qword_163980, after delay (:239-246): *(result+32)==163980 → 792C4() (11-12, gen-guard HYPOTHESIS khớp 27AE4/2410C:202-203). 792C4: dispatch_once, !nonavhide + !sleeping + 791A4() → async queue 793F4 → 79434 nav-hide verify (:19-37), else đếm 1646B4.

## 5. `layout` trong 3 methods
- Grep: 218D8唯一的 1 hit :425 CFSTR duodash_ab_layout; 217EC 0 hit; 208F4 0 hit. 218D8 đọc file + fallback 73E8() plist (:421-444, set 162E90 + byte_163AF2). 208F4 chỉ so 162E90==73E8() (:184-186). 217EC không chạm.
- HYPOTHESIS: layout request truyền gián tiếp via globals 163998..1639B0 (geometry) + 162E90/1639C0, không phải string key.

## 6. Ma trận nhanh
hostSlots(a3 bids,a4 skipEvict,a5 onHosted) 218D8:9-14,177,628,630; hostSplitL [L,R]→hostSlots(...,0) 217EC:33-40; switchInPlace(bids,gen)→bool 208F4:9-14,580,623; full-host khi 23454||!active||!split||visible||v28||!present 218D8:307-313; no-display/degenerate + 97A0 218D8:323-352; reshow 89D8+70248+234A0+23AB0+9424+4D0F4 218D8:659-706; 9424 post via 8D78 deliverImmediately 9424:102/8D78:21-27; 7 files /var/tmp, không CFPrefs/notify_post 218D8:381-510; 208F4 guards→0, convert-fail rollback nhưng return 1 (return-semantics HYPOTHESIS); 279F4→27AE4→7792C reap/kill(9); 27AC8 gen-guard→792C4; layout string chỉ 218D8:425; L/R/C = index order + skipEvict chỉ async 2410C (HYPOTHESIS, evict-suppress UNKNOWN).
