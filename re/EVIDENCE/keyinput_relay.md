# EVIDENCE/keyinput_relay.md — P2-2 Unified Keyboard relay phía DYLIB (session-005)
_Nguồn: subagent general đọc decompile dylib. Mỗi claim có file:line + nhãn._

## 0. Đăng ký Darwin
### SB-side init 27E20 (guard once byte_163CB0, 388-389)
8 observers observer=nullptr/Coalesce (392-447): begin→37978, type→3798C, end→379A0, kbframe→379B4, kbshown→379C8, othertap→379DC, kblost→379F0, retap→37A04. Sau đó: 30BA0() purge + 30F48(0) card=0 + notify_post(dismiss) (448-450).
### UIApp-side init 4CBDC (guard DUODASH_AB_UIAPP_IPC_HOOKED env, 27-29)
CNABKeyProbeObserver singleton 163F68 (64-67). 4 Darwin observer=163F68/Coalesce (69-100): apply→4CF3C (→4D0AC→onApply:0), dismiss→4CFBC (→4D0A0→onDismiss:0), card→4D03C (→12DCA8), fallback→4D050 (→12DCC8). Đồng thời NSNotification UIKeyboardWillShow/Hide→onKbShow:/onKbHide:, TextField/ViewDidEndEditing→onEndEditing: (102-129). Body onKbShow/onKbHide UNKNOWN.

## 1. Per-function model
### 1.1 8 stub SB-side (37978/3798C/379A0/379B4/379C8/379DC/379F0/37A04)
Identical `dispatch_async(main, stru_12D7F8...8D8)` (mỗi file :11). Không dùng payload, không condition, fire-and-forget. Block đích không có .c → UNKNOWN. Mọi "SB làm X khi nhận kbshown" phải tra 37CBC/38240/38CE8/39260/37A7C.
### 1.2 4 handlers UIApp-side
- **4CF3C** (9-24): build block {4D0AC, ctx 1461F8, retain a2} (15-20) → async main (21). → **4D0AC**: `[*(a1+32) onApply:0]` (11). Luôn nil arg, onApply tự đọc file.
- **4CFBC** (9-24): identical với block 4D0A0 → onDismiss:0.
- **4D03C** (9-12): async 12DCA8 (UNKNOWN body; ứng viên 4D064→4C59C đọc notify_get_state card — HYPOTHESIS linkage).
- **4D050** (9-12): async 12DCC8 (UNKNOWN; ứng viên 4D068→4C650 — HYPOTHESIS).
### 1.3 30BA0 purge (9-25)
163CA0 non-empty → xóa per-bid `duodash_keyinput.plist` + `duodash_keyinput_in.plist` (via 31080=containerDir(bid)/tmp/+name, 31120=removeItem error:0) (14-22). Luôn xóa `/var/tmp/duodash_keyinput_seed.plist` + `..._out.plist` (23-24). Callers: 27E20 init, 30AC4 dismiss, 37C48 fallback.
### 1.4 30F48 card reset (9-29)
state64 0/1 (callers 27E20:449→0, 30C2C:84→0, 38240:262→1). Lazy notify_register_check(card,&162EF4) nếu -1 (17-21); ok → set_state+post card (24-25). Fail → -1, không set/post (27-28). UIApp đọc via 4C59C:27.
### 1.5 4D0AC/4D0A0: `[observer onApply:0]` / `[observer onDismiss:0]` (mỗi file :11).
### 1.6 Swizzle _UIKeyboardLayerHostView (372CC installer + 37398/374C4/375B8) — native-kb suppressor màn ngoài, KHÔNG phải relay
- Installer once 163C48 (14-16); class nil → skip (18-19); 9C190 3 selectors → origs 163C50/58/60 (21-38).
- 37398 setCenter:: retain kép, 37640 (bỏ kq) + 376DC target rect (25-28); null → passthrough (31-34); lệch >0.25pt cả 2 trục + 162EF0>=1 → --162EF0 (49-51); gọi ORIG với (MidX,MidY) (54).
- 374C4 setFrame:: tương tự, ghi đè (x,y,w,h) target (26-36) → ORIG (37).
- 375B8 didMoveToWindow: gọi ORIG trước (16), rồi center→setCenter: (tự kích hook) (20-24).
- **376DC target-rect** (9-76): passthrough (CGRectNull) trừ khi đồng thời: 163D58!=0 (card active, 30) + window.screen != mainScreen (màn ngoài, 37-42) + superview.bounds>=1, a2/a3>=1 finite (47-52). Đủ → x=bounds.x+max((bounds.w-a2)*0.5,0), y=bounds.y+bounds.h-a3 (neo đáy, căn giữa, 54-55). 37640 chỉ tính width transform (bỏ kq — UNKNOWN mục đích).
### 1.7 3723C — splash timer (dropSplashIfOverdue), KHÔNG phải relay. Loại khỏi sequence.

## 2. Relay thực sự
### 2.1 SB seed writer 37CBC (9-181)
- Inputs: a1 log string; 163CA0 bid; đọc seed.plist + per-bid duodash_keyinput.plist + out.plist (49-73). 163CA0 rỗng → teardown (53-54,122-124).
- Ưu tiên seed, fallback per-bid plist (55-72). Merge out: out.text NSString && out.ts >= seed.ts → dùng out.text (92-120; 105-109 giữ seed).
- Chỉ ghi seed mới nếu 38240(v2)!=0 && bid non-empty (125-127). Dict 6 keys {text||"", selLoc=len, selLen=0, kbType||0, returnKey||0, ts=now} → 3896C → seed.plist (129-173); success → post keyinput.seed (173-174). Trước đó 30C2C teardown + 38240 dựng card (124-125). Return = 38240 result (180). 3896C fail → không post. 3815C nil nếu thiếu/không dict (22-49).
### 2.2 Pane-side seed writer 3A588 (9-254, generation check *(a1+32)==163CA8, :75)
- Quét hostedSlotBids DDz2 (77-84). Mỗi bid: đọc per-bid duodash_keyinput.plist → ts; chỉ xét 0<=now-ts<=**10.0s** (121-124, KHÔNG phải 30s). Giữ bid ts lớn nhất (125-133). Không bid → return (156-174).
- **secure flag boolValue==1 → early return, không seed** (161-174, password bypass).
- 38240("text field focused in a pane")!=0 (181). Copy bid→163CA0, ++163D18, 163D20=80 (budget? HYPOTHESIS tên; giá trị CONFIRMED 183-187,246). Dict 6-entry → 3896C → seed.plist → post seed (188-248).
### 2.3 SB out→in forwarder 3A2E0 (9-87)
- 163CA0 rỗng → return (27). Đọc out.plist via 3815C (29); nil/text sai type → return (31-41,83-86).
- Build {text, ret||0, ts=now} (46-66) → per-bid tmp/duodash_keyinput_in.plist via 31080+3896C (70-71) → post keyinput.apply + --163D20 nếu >=1 (73-78).
### 2.4 UIApp focus 4B90C (9-220, hook becomeFirstResponder-like, callers 461C4/461D0) + publisher 4C000 (9-151)
- 4B90C: --163054 (48-49); 163ED9==0 → passthrough (50-55,67-71); 162F88==0 (keypane off) → clear + passthrough (56-61); knob duodash_ab_nokeypane via 453B8 (1s TTL, 453B8.c:26) → bypass (62-72); đã focus (weak==v5) → passthrough (73-79); cooldown CACurrentMediaTime<164138 → passthrough (81-84); !CNABUIApp.isSplit → passthrough (85-89); session đủ (163F58&&163F5A&&164180&&weak) → post retap + --162F58 (90-98); **secure (45568==0) → 4BF44 restore + orig + return (105-112, password bypass)**; non-secure → store weak 163F30 + class 163F38 (131-132), 164130==1 + responds setInputView: → gán dummy 163F40 chặn native kb (133-149), gọi orig (151), 163F58==1 + weak → snapshot 163F48 + 4C000() + post begin (154-191) + after 1.5s 4C44C + async 4C4FC (193-206, UNKNOWN bodies).
- 4C000(v1): gate 45568 (secure → return, :40). Path = NSTemporaryDirectory()/duodash_keyinput.plist (454F4 17-19; :42-43, rỗng → return). Đọc text/keyboardType/returnKeyType có respondsTo guard (45-63). Dict 8 keys {bid||"", text||"", selLoc=len, selLen=0, kbType, returnKey, **secure=@NO cứng (:93)**, ts} (64-106) → serialize(200)+write 536870913 + chmod off_154400 (114-139). Serialize fail → nuốt.
### 2.5 UIApp apply onApply: (44B1C.c:9-227, đích 4D0AC)
- Gates 163ED9&&163F58 (51). Đọc NSTemporaryDirectory/duodash_keyinput_in.plist (53); nil/không dict → return (56-76). text NSString bắt buộc (77-101), ret bool||0 (84-95). --162F58 (102-103). weak 163F30 nil/không-45568 → return (105-113, bypass lần 2).
- Diff/patch (114-191): current text (default ""), isFirstResponder (131-134); khác + FR + UIKeyInput → prefix chung + deleteBackward/insertText (137-153); else setText: (155-156); UITextField → EditingChanged + UITextFieldTextDidChangeNotification (157-172); UITextView → delegate textViewDidChange: + UITextViewTextDidChangeNotification (174-190). Snapshot 163F48 (193-206). ret==1: UITextField → delegate textFieldShouldReturn: (210-216); else FR → insertText:@"\n" (217-220).
### 2.6 Kb height/dark 38CE8 + overlay 39260
- 38CE8: đọc kb.plist (22), h + ts (23-24); window **600s** 0<=delta<=600 (28-36); h>=4000||h<=1 → 0 else h (39-42).
- 39260(a1=w,a2=h): kb.plist[dark] (68-76), set hidden+frame overlays 163C88/90 left/right, màu dark/light (87-196). Không ghi/post.
### 2.7 Dismiss/fallback/teardown
- 30AC4 dismiss SB (9-40): main → v2=len(163CA0), 30BA0, clear bid, v2 → post dismiss (20-27); +30C2C (27). Background → async 30B98 (UNKNOWN).
- 30960 (9-35): main + (163C78||bid) → ++163CA8 + 30AC4 (18-22, toast OFF cũng teardown); background → async 30ABC (UNKNOWN).
- 37C48 fallback SB (9-26): ++163CA8, purge, clear bid, v2 → post fallback (16-23) + 30C2C (24). Kích hoạt: lost twice / rebuild failed (37A7C 52-62).
- 30C2C teardown card UI (9-127): hop main (39-50); clear 163C78/68/70/88/90 + sizes/flags (64-82); ++163CE8; 30F48(0) card off (84); animate restore hoặc 30FB8 (85-120, UNKNOWN chi tiết).
- 38240 dựng card (9-290): từ chối nếu 163C78 có (return 1, 78-81); nếu 162DDC!=1 hoặc file nokeypane → return 0 (83-92); tạo aux scene com.sensetechlab.duodashkey + containers + overlays + 39260 + after 1.5s 397E0 + 4×12D738 (UNKNOWN) + 30F48(1) card on (262).
- 37A7C rebuild-on-lost (9-70): hop main via 37C40 (24-35); 163C78&&bid → 163D28==163D18 (lost twice) → 37C48 (52-55), else 163D28=163D18 + 37CBC("rebuild — keyboard lost") || 37C48("rebuild failed") (58-62); tôn trọng nokprecover (47-50). Caller 37A18 watchdog ≥3s (11-17).
- UIApp dismiss/cleanup: 4C650 (clear session 22-32; a2!=0 → post end 33-34; cooldown 164138=now+min(30<<v7,480) 35-39; restore inputView=0 + reload + becomeFirstResponder có guard 40-68); 4D068 → 4C650(reason,0) không post end (11-12); 49778 luôn post end + restore (29-36); 449C8 teardown khi tắt switch (15-40).
- UIApp posts: end từ 45180:70 / 49778:36 / 4C650:34; othertap throttled 0.3s từ 48924:136; retap 4B90C:95; begin 4B90C:191.

## 3. END-TO-END
(a) Chạm field trong pane: 4B90C intercept (gates bypass) → store weak + dummy inputView chặn native (131-149) → 4C000 ghi NSTemporaryDirectory/duodash_keyinput.plist (42) → post begin (191) → SB 3A588 poll hostedSlotBids window 10s (117-124) pick bid mới nhất + secure check (161-174) + 38240 dựng card (181) + 163CA0/163D18/163D20=80 (183-187,246) → ghi /var/tmp/seed.plist → post seed (247-248). Đường rebuild SB 37CBC (merge seed/out theo ts) → cùng path + notify (173-174).
(b) KeyApp: HYPOTHESIS (đối chiếu session-001, không verify binary). CẢNH BÁO: dylib chỉ thấy window 10s (3A588:123) và 600s (38CE8:36); **không có hằng 30s** → claim ts<30s là HYPOTHESIS/UNKNOWN. Dylib xác nhận nửa đọc: đăng ký kbshown/kbframe/type (27E20:403-426), đọc kb.plist{h,ts,dark} (38CE8:22, 39260:68-70), đọc out.plist + merge ts (37CBC:92-120).
(c) Apply: SB 3A2E0 đọc out.plist (29) → per-bid in.plist (70-71) → post apply + --163D20 (75-77) → UIApp 4CF3C → async 4D0AC (4CF3C:21) → onApply:0 đọc in.plist (53) → verify → diff/patch + change notifications → ret handling (44B1C).
(d) Dismiss (SB→UIApp): 30AC4/27E20/30960 → post dismiss → 4CFBC→4D0A0→onDismiss: (body UNKNOWN; cleanup tương đương 4C650/49778/449C8 CONFIRMED). kblost (KeyApp→SB): 379F0→hop UNKNOWN; watchdog 37A18 (≥3s) → 37A7C rebuild. Fallback: 37C48 (lost twice/rebuild failed) → post fallback → 4D050→12DCC8 UNKNOWN (ứng viên 4D068→4C650 HYPOTHESIS). end/othertap/retap/begin posts CONFIRMED (45180:70, 48924:136, 4B90C:95, 4B90C:191).

## 4. Password bypass: gate duy nhất isSecureTextEntry via 45568
- Grep secureTextEntry|isSecure|password: chỉ trúng 45568.c:18-19 + B16A0 trampoline. Không password literal (0 hit).
- **45568(a1)** (9-22): nil→NO (fail-closed); !responds→YES (non-secure); isSecure==1→NO (chặn).
- 3 enforces: focus 4B90C:102-112 (native kb); publish 4C000:40 (không ghi); apply 44B1C:107-113 (không patch). SB-side 3A588:161-174 đọc plist["secure"] (dự phòng writer ngoài; dylib luôn ghi NO).
- Secure field không bao giờ vào relay.

## 5. keypane_enabled=0
- Đọc SB 8058 (9-31): value==YES→1 else (keyExists==0) → **thiếu key = ON**; lưu 162DDC (29).
- Push+toast 29400 (9-85): v0==0 → 30960("...switched OFF") → teardown+dismiss nếu có card (30960:18-22); DDz2.active → mỗi bid (29810) push {keypane_enabled, bundleIdentifier} via 8C28(uiapp.keypane) (58-71). Darwin keypane.changed→29400 (27E20:352-359).
- Nhận UIApp: onKeyPaneSwitch: (443FC:9-33, default 1 nếu không NSNumber 26-29) + onState: (4407C:99-105) → 448B4(v,"switch"/"state").
- Áp 448B4 (9-52): hop main (40-50); 162F88!=a1 → update (20-21); ON → clear cooldown (23-27); OFF → 163F58=0, 164130=0 + session → 449C8 (clear+inputView 0+reload+resign, 449C8:15-40) (29-36).
- Hệ quả OFF: focus passthrough native (4B90C:56-61, 45180:24-28, 48924:62-66); knob nokeypane độc lập 1s cache (453B8:26; 4B90C:62-72); SB 38240 từ chối (38240:83-92); session teardown + dismiss (30960→30AC4) + resign (449C8).

## 6. Inventory (paths/schema/globals)
- SB /var/tmp cứng: seed/out/kb plists (30BA0:23-24, 38CE8:22, 37CBC:55,73). Per-bid container 7F014(bid)/tmp/: duodash_keyinput.plist + _in.plist (31080:18-22, 30BA0:16-21, 3A2E0:70). UIApp NSTemporaryDirectory/: cùng 2 tên (454F4:17-19, 4C000:42, 44B1C:53). Chmod off_1543D0 (SB 3896C:40) / off_154400 (UIApp 4C000:129) + write 536870913 atomic (3896C:36, 4C000:125).
- Schema: seed {text||"", selLoc=len, selLen=0, kbType||0, returnKey||0, ts} (37CBC:129-160); per-bid +{bid, secure:@NO} (4C000:64-99); in {text, ret, ts} (3A2E0:46-66; đọc text bắt buộc + ret||0, 44B1C:77-95); kb {h, ts, dark} (38CE8:23-24, 39260:68-70).
- Darwin dylib: keyinput.{begin,type,end,kbframe,kbshown,othertap,kblost,retap,seed,apply,dismiss,card,fallback} + keypane.changed + paneactivity/uiapp.keypane (27E20:352-450, 4CBDC:70-100, 37CBC:174, 3A2E0:75, 30AC4:26, 37C48:23, 4B90C:95,191). type/kbframe/kbshown/begin/end/othertap/retap SB-side chỉ tới hop (UNKNOWN sau hop).
- Globals: 163CA0=current bid, 163CA8=generation (++ fallback/dismiss), 163D18/28=seed gen (lost-twice), 163D20=apply budget init 80 (--/apply), 162EF0=swizzle budget, 162DDC=SB keypane on (def 1), 162F88=UIApp keypane on, 163F58=armed, 163F5A=session, 164130=dummy-inputView, 164180=card-on (4C59C:35), 163F30=weak FR, 163F40=dummy view, 164138=cooldown (4C650:39).

## 7. Giới hạn & UNKNOWN
1. Body 8 block SB (12D7F8…8D8) + 2 block UIApp (12DCA8/12DCC8) không .c → UNKNOWN (thunks 4D064→4C59C, 4D068→4C650: HYPOTHESIS linkage).
2. ts<30s KeyApp không thấy trong dylib (chỉ 10s/600s) → HYPOTHESIS.
3. kb/out writers KeyApp → HYPOTHESIS.
4. 3723C là splash — đã tách.
