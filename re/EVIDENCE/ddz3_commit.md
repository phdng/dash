# EVIDENCE/ddz3_commit.md — DDz3 picker→host bridge (session-011)
_Nguồn: subagent general đọc FULL 5F044/5F224/5F538/5F74C/5F8A4 + helpers + call-sites. Mỗi claim có file:line + nhãn._

## 0. Commit chain (kết luận trước)
onTilePressed: [5EDC4:76-77] → close + commitPick:(cnabBid) → resolveSlotBids [5F538:25] → dedup + validate 6A13C [5F538:40-65] → commitSlotBids:why:("picked %@ for slot %ld") [5F538:67-80] → bakeLiveSwapForCommit:(why) [5F8A4:72] → SetValue left/right/third + Sync [5F8A4:73-94] → CarPlay-UI reconcile 7044/70FC/86A0/84D8 [5F8A4:99-147] → 74C8() → write plist + post resolved [74C8:416-419].
**Host KHÔNG được gọi trực tiếp** (không hostSlots/hostSplit/onHostRequest trong 5 files — grep corpus CONFIRMED). Host nhận gián tiếp qua prefs-file + Darwin: 17344 debounce 350ms [17344:17-28]; CFNotification resolved/listchanged [163EC:145-159]; Darwin 29198 → 74C8+792C4 [29198:9-12]; host thực thi hostSlots [218D8:9] từ onHostRequestSplit: [202D0:237] / hostSplitL [217EC:40].
`commitSlotBids:why:` là biên cuối picker; không DDz1/DDz2/CNAB IPC mảng bids; `why` chỉ string chẩn đoán → bake, không persist.

## 1. 5F044 resolvePairL:R: (0x5f044, void (out L,out R), callers:none [5F044:5])
- Inputs: self->_pairL/_pairR retain (:21-22). Không _pairC/_openSlot/picks/why.
- 3 tầng fallback + dedup 2-slot: (1) rỗng → +DDz2 shared补 hostedBundleId (L) / hostedBundleId2 (R) (:25-39, lần duy nhất chạm DDz2; không DDz1/CNAB/host/notify); (2) vẫn rỗng → 7044("appbridge_split_left"/"right") (:40-51; 7044:18-42 NSString non-empty else nil); (3) dedup: 162E90!=1 && cả hai non-empty && equal → R=@"" (:52-59; 162E90 layout-id, !=1 cấm trùng — HYPOTHESIS ý nghĩa layout).
- Ghi out-params (nil→@""), luôn ghi nếu con trỏ non-null (:60-75). Không prefs/notify/global/error path.
- Vai trò: **legacy 2-slot, không ai gọi** (callers none + grep). HYPOTHESIS tàn dư trước slot thứ 3 (pairC).

## 2. 5F224 resolveSlotBids (0x5f224, return NSMutableArray [L,R,C] autoreleased)
- Header callers 0x56b24/56e7c/571b8/5a314 [5F224:5]; grep thực còn 5F538:25, 5FD10:37, 626B4:34, 628F4:27, 627D0:21, 67C38:86, 69824:85,94 — header thiếu (HYPOTHESIS không đầy đủ).
- Inputs duy nhất: self->_pairL/_pairR/_pairC (retain từng cái, arrayWithCapacity:3) (:33-40). Không why/prefs trực tiếp.
- Vòng i=0..2 (:42-87): slot rỗng → hostedBundleId/2/3 nếu DDz2.shared!=nil (:45-66; khác 5F044: check nil trước); vẫn rỗng → 7044("..._left/right/third") (:67-80); nil→@"" addObject (:81-86).
- Dedup 3-slot (:88-124): v13 = (162E90-1)>7 ? 2 : BA7C8[162E90-1] (bảng slot-count theo layout — HYPOTHESIS tên bảng từ use-sites 208F4:190/218D8:187/5F538:39); v13<2 → bỏ dedup (:95-96); loop j=1..v13-1: bids[j] non-empty && equal bids[0..j-1] → bids[j]=@"" (:98-124, chỉ trong phạm vi layout).
- Gọi DDz2 (+shared, hostedBundleId/2/3) (:41,53,57,61). Không DDz1/CNAB/hostSlots/CFPrefs/notify_post. Read-only resolve, không bake/validate.

## 3. 5F538 commitPick: (void (bid), why tạo bên trong)
- Caller duy nhất: onTilePressed: [5EDC4:76-77] — lấy cnabBid từ CNABTileControl (:39-41), bid.length!=0 (:43), bid ∈ self->_apps[][bid] (:70-74); đã lọc long-press/swipe/arrange-exit (cnabLongPressed/cnabSwiped/time-_arrExitAt>=0.5 :32-36); close + commitPick:v7 (:76-77, picker đóng dù commit thành công hay không).
- 5 bước (:25-80): resolveSlotBids → mutableCopy (:25-27); guard openSlot (âm/vượt count → silent return :28-29,85-87); setObject (v4?:@"") tại openSlot (:30-35); dedup slot-count layout (BA7C8, bỏ qua openSlot; trùng bid pane khác → **hủy commit giữ prefs cũ** :36-55,85 — khác commitSwapOfPositions swap tường minh); validate `!length || 6A13C(v4)` mới commit (:65).
- **6A13C** [6A13C:9-60]: ""→0; không SBApplicationController→-1; có class không responds→-1; applicationWithBundleIdentifier:!=nil→1; nil + Preferences tồn tại→0 else -1. Commit iff clear HOẶC đã cài (1) HOẶC môi trường lỗi (-1); drop chỉ khi chưa cài mà SB còn sống (0). v4 nil → length 0 → pass clear (nil-messaging HYPOTHESIS).
- why 2 bước: "slot %ld" (:67-72) → "picked %@ for %@" (:73-79) → commitSlotBids:bids why: (:80, đường duy nhất user-pick→host). Không DDz1/DDz2/CNAB/host/prefs trực tiếp. Error silent, không alert/log.

## 4. 5F74C bakeLiveSwapForCommit: (why forward/debug, không parse)
- Callers: 56B24 (header :5) + thực 5F8A4:72 + 67C38:81 (header thiếu).
- Guard: chỉ bake khi KHÔNG ở live-swap special-mode (word_162ED8 / byte_163AF1... pattern lặp 571B8:47/67C38:77-80/75F38:18-21; :21). Ý nghĩa bit UNKNOWN (218D8:359-360 set 256/2 ở host-no-display path).
- Nhánh layout==2 (162E90==2): 163AF1==1 && llround(162EB8*100)-1<=0x62 → SetValue split_ratio NSNumber (integer elided — UNKNOWN giá trị) (:24-32).
- Nhánh else (163AF3==1): v7=69E20(0), v8=69E20(1), 8270(layout,v7,v8) (:34-39); 8270 = ghi frac_a/b/layout (clamp 1..99 else 0) + Sync, layout 2..8 ([8270:25] range HYPOTHESIS) [8270:38-70].
- Sau đó nếu không special-mode: 75F38(v3=why, thực bỏ qua arg, tự 752E4 lấy live index → 75E14 reorder) (:40-41, 75F38:9-30; chỉ reorder khi result 1..3 + not-special :22 — HYPOTHESIS "bake swap drag vào prefs").
- Không DDz1/DDz2/CNAB/host. Ghi prefs ratio hoặc fracs. Không Sync riêng nhánh ratio (Sync cuối do commitSlotBids/commitGutter). UNKNOWN: 69E20, 752E4/75E14, 162EB8/162ED8/163AF1/163AF3 chi tiết.

## 5. 5F8A4 commitSlotBids:why: (a3=array 3 bids, a4=why chẩn đoán)
- Callers: 571B8:69 + 5F538:80 (header :5 khớp grep). Guard count<3 → silent drop (:52). Unpack [0]/[1]/[2] nil→@"" (:54-71).
- **Bake trước**: bakeLiveSwapForCommit:(why) (:72) — geometry/frac bake trước bids flush.
- Persist: SetValue split_left/right/third + Synchronize (:73-94). v15 = array 3 bids (:95-98, chỉ dùng CarPlay test).
- CarPlay-UI reconcile (:99-147): v34=7044(carplay_ui)?:@""; v18=70FC() (ui NSString? + more array → 7E730 merge [70FC:18-38]); v19=86A0 predicate isEqual tuyến tính trên v15 (86A0:36-48); v21 = v34.length && v19(v34) ? v34 : @"" (:113-116, chỉ giữ main nếu đang pick); v22 = filter v18 qua v19 (:117-141); đổi → 84D8(v21,v22) (:143-147; SetAppValue ui+more + Sync + 74C8 [84D8:28-31]). **Luôn 74C8()** (:156) dù CarPlay đổi hay không.
- 74C8 (430 dòng): clearpanes (:100-206); Sync + 7EA4/8058 (:207-209); đọc prefs build dict 14 keys + write plist (:272-416); **notify_post resolved** (:419, tín hiệu duy nhất tới host). Không CPDistributedMessagingCenter send, không hostSlots call.
- Không DDz1/DDz2/CNAB/hostSlots/hostSplit/onHost*. HYPOTHESIS sai thường gặp "commitSlotBids gọi onHostRequestSplit" — **SAI** (onHostRequestSplit là CNABSpringBoardObserver đăng ký CPDistributedMessagingCenter host.request(.split) [27E20:287-291] via 887C wrapper [887C:20-21]; hostSplitL→hostSlots [217EC:40]).

## 6. why strings (grep corpus, chỉ 2 call-sites commitSlotBids)
- "picked %@ for slot %ld" format 2 bước [5F538:67-79] — duy nhất user-pick. "gutter re-host swap" [571B8:69] — swap path. "gutter drag" [56B24:41] → bake trực tiếp (không qua commitSlotBids). "layout apply" [67C38:81] → bake trực tiếp. Không why khác (trong decompile; UNKNOWN indirect objc_msgSend miss).
- why không persist (arg → bake → 75F38 bỏ qua [5F74C:19-41, 75F38:9-10]; HYPOTHESIS log/debug).

## 7. Đường song song (không qua commitSlotBids — commitSlotBids KHÔNG phải bottleneck duy nhất)
- commitGutterFrac [56B24:41-119]: bake("gutter drag")+resolve+prefs left/right/third+ratio/fracs+74C8.
- commitSwapOfPositions:with: [571B8:21-69]: resolve→mutableCopy swap→notePanesSwapped/geometry→commitSlotBids("gutter re-host swap").
- onLayoutTilePressed: [67C38:81-142]: bake("layout apply")+prefs+Sync trực tiếp, **không qua commitSlotBids** (cuối gọi 746C [67C38:221]).

## 8. Prefs/globals (5 files)
- Ghi CFPreferences left/right/third + Sync [5F8A4:73-94]. Đọc 3 keys via 7044 plist [5F044:42,48 / 5F224:77 / 5F8A4:99]. ratio ghi (giá trị UNKNOWN elided) [5F74C:27-32]. fracs via 8270 [5F74C:38]. carplay_ui/_more đọc 7044/70FC + ghi có điều kiện 84D8 + Sync [5F8A4:99,105,143-147]. plist + post resolved via 74C8 [74C8:416-419].
- Đọc điều khiển: 162E90 layout-id, BA7C8 slot-count table, word_162ED8/byte_163AF1... mode, _pairL/R/C, _openSlot (HYPOTHESIS semantics layout/mode). Không ghi globals khác. Không DDz1.shared/CNAB/host/notify trực tiếp.

## 9. Tàn dư / UNKNOWN
- resolvePairL:R: không caller — tàn dư 2-pane (HYPOTHESIS tương thích).
- split_ratio NSNumber arg elided [5F74C:28-29] — cần assembly 0x5f74c.
- buildKitLevel:pane: (0x63CE4) không decompile — không trong callees 5 files (không 0x63ce4 trong headers) nên không liên quan chain.
- Host re-host ngay sau resolved hay debounce: 17344 after 350ms → 1FB40 [17344:20-27] là debounce CarPlay/listchanged; SpringBoard hostSlots trigger chính xác sau picker-notify UNKNOWN (cần 1FB40/792C4).
