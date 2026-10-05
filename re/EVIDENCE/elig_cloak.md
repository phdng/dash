# EVIDENCE/elig_cloak.md — P2-3 CarPlay eligibility cloak + dock/focus/statusbar (session-005)
_Nguồn: subagent general đọc decompile. Mỗi claim có file:line + nhãn._

## 0. Installer + helpers
- Elig group cài tại 163EC.c:181-295, guard getenv(DUODASH_AB_ELIG_HOOKED). Orig-slots: 163858=effectivePolicyForAppDeclaration: (192-199); 163860=declarationForAppProxy: (200-207); 163868=_newApplicationLibrary (209-216); 163870=carPlayDeclaration (218-225); 163878=icon:imageWithInfo: obj-variant (229-236); 163880=struct-variant (261-268); 163888/163890=displayName/displayNameForLocation: (272-283).
- dword_162E08 = capability probe DBApplicationController (sharedInstance/appLibrary/applicationWithBundleIdentifier:/_didAdd:/_didRemove: + DBApplicationInfo tồn tại, 285-295); ==1 mới cho nhánh patch policy.
- Dock/focus/statusbar cài tại 18A7C.c:17-66, guard DUODASH_AB_DOCK_HOOKED, fallback DB→CAR: 1638D0=_dockButtonPressed: (35-42); 1638D8=takeWithPriority: 8-arg (44-52); 1638E0=homeButtonUp: (53-58). Env chỉ set khi cả 3 origs non-nil (59-62).
- Icon-tap cài tại 189D0.c:9-42 trên SBHIconManager: 163790=iconTapped:, 1638C8=iconTapped:modifierFlags:; class nil → không hook.
- **1CAF8** (9-20 FULL): chỉ `length>0 && =="com.sensetechlab.duodash"` else nil/0. First-party hardcoded; không list/plist/CFPrefs/substring.
- **114B4 "bridged check"** (9-47 FULL): trả 1 iff AND + 2 exclusion: (1) byte_163770==1 (appbridge_enabled từ plist, 17410:118-130); (2) bid.length>0 && 163450 contains bid (bridgedApps, 17410:131-150); (3) nếu 116D4() true thì loại bid==navprovider_selected (24-33; 7044 đọc key); 116D4 (9-63) = navprovider_autostart bool cache 2s, bypass nếu file nodashkeep hoặc 163470/163478 non-empty → 0 (cache 60s) — literal CONFIRMED, semantic HYPOTHESIS; (4) loại CarPlay-UI: (!len(163470)||bid!=163470) && (!count(163478)||!contains) (34-37); nguồn 163470/163478 load 17410:169-182 — literal CONFIRMED, UX HYPOTHESIS.
- **1CA4C "split-member check"** (9-24): length && (1CAF8 || ==1634B8 || ==1634C0 || ==1634C8). Dùng dock/split/focus, không dùng elig/icon.
- **1E770 roster gate** cache 1s: byte_162E28 = !fileExists(/var/tmp/duodash_ab_noroster). Tồn tại ⇒ roster OFF.
- **1C3C8 master kill-switch**: return !fileExists(/var/tmp/duodash_ab_hosting_off). Tồn tại ⇒ mọi intercept dock/focus/home/icon skip → call-through (1BB20:81,110,125; 1BF1C:113; 1C29C:22; 1D1D4:24,43,51).
- **F83C int-probe** (9-22): trả objc_msgSend(obj,sel) nếu responds else -1 (0xFFFFFFFF).

## A. Eligibility cloak
### A1. 17EC4 effectivePolicyForAppDeclaration: (KHÔNG fake số)
- Luôn gọi orig trước: v7=off_163858(...) (:34). Cache bridged khi 163770==1 && bid∈163450 (:41,47): 163488[bid]=origPolicy, 163490[bid]=@(launchUsingTemplateUI) (:59-61), chỉ khi F83C không âm (:51,55); F83C==-1 → không cache.
- Nhánh patch v18 (:70-85): cần v7 && 162E08==1 && (114B4||1CAF8) && 1E770() (:71-73). 3 probes (isCarPlaySupported/canDisplayOnCarScreen/isCarPlayCapable/launchUsingTemplateUI) via F83C nhưng bỏ kết quả (:75-78, HYPOTHESIS probe/log). v18=1 không kèm literal policy number.
- Ép launchUsingTemplateUI=0 (:86-90): độc lập v18/1E770/162E08, chỉ cần (114B4||1CAF8) && responds setLaunchUsingTemplateUI:. Roster OFF vẫn neuter.
- Ép CarPlay-capable (:91-123): chỉ khi v18==1. Add bid vào 163898 (once 1638A0/12D228, :95-100); runtime-add setCarPlaySupported:/setCanDisplayOnCarScreen: ("B", 9BDE4, :108-110) nếu chưa patch (cache 1638A8/1638B0); set cả hai =1 (:117-119). Fake = 1/1, không phải policy enum.
- Error: v7 nil → skip patch+class-patch, trả nil (:71,91,127). off_163858 nil mà bị gọi → crash (HYPOTHESIS, không nil-guard).
- Luôn trả v7 (orig object mutate tại chỗ), không object synth (:127).
### A2. 18318 +declarationForAppProxy:
- Orig trước (:18); non-nil → giữ, không override (:20-23). Orig nil mới xét synth (:25-39): applicationIdentifier nếu responds (:26-29) else nil; 114B4||1CAF8 → 1DB14(bid) (:30-32) else nil (:38).
- **1DB14** (9-30 FULL): getClass CRCarPlayAppDeclaration; nil → nil (:17,27); có → alloc_init + setBundleIdentifier:bid + setSupportsMaps:1 (guarded responds, :20-23). Fake = {bundle=bid, SupportsMaps=1}.
- Error: orig nil + không bridged/duodash → nil; class nil → nil (:38; 1DB14:25-28); bid nil/empty → nil (114B4(nil)=0, 1CAF8(nil)=0).
### A3. 1842C +_newApplicationLibrary (không điều kiện bid)
- v0=off_163868() → store 163480 → 1DBE8(v0) → return v0 (:13-16). Luôn call-through. Orig nil → lưu nil, 1DBE8(nil) return sớm (:92), trả nil.
- **1DBE8** (91-440) injector: build bridgedApps + "com.sensetechlab.duodash" (1CAF8(CFSTR) luôn true → DuoDash luôn add, :94-104); mỗi bid chưa có applicationInfoForBundleIdentifier: → LSApplicationProxy + addApplicationProxy: + nhét ivar _carPlayDeclaration=1DB14(bid) (:129-163); nhánh phụ icon-add via /var/tmp/duodash_ab_iconadd + notify _notifyDidAddApplications: (:167-179,435-436, HYPOTHESIS thứ tự/kích hoạt).
### A4. 18490 -carPlayDeclaration
- v2=off_163870() (:19); v4=1D9BC(self) trích bid duyệt selector-list off_1540D0 (string non-empty đầu, 1D9BC:30-61, :20).
- Orig non-nil → thắng (:23-25), kể cả DuoDash. Orig nil + !114B4 && !1CAF8 → nil (:28-33). Orig nil + bridged/duodash → once (1638C0/12D248) add bid vào set 1638B8 (:34-37) → trả 1DB14(v4) (:38). Error: class nil → nil; v4 nil → nil (:28).
### A5. 185C8 icon:imageWithInfo: variant 1 (object-info)
- Orig trước (:29). v11=1D36C(a3) trích bid duyệt off_154118 (:30; 1D36C:29-56). Chỉ xét fake khi **1CAF8** (:31-32); **không hỏi 114B4** → bridged third-party giữ icon orig.
- Synth 1D4F8 (:49): size=max(orig.size,60) else 120.0; scale=orig.scale else 2.0 (:39-48). Nguồn "/Library/Application Support/DuoDash/DualAppsIcon.png" + UIGraphicsImageRenderer (1D4F8:28-60); load fail → fallback block 1D6D4 (:52-60, glyph UNKNOWN). v20 non-nil → synth else orig (:52-60).
### A6. 1875C icon:imageWithInfo: variant 2 (struct-info, CAR)
- Check 1CAF8(1D36C(a3)) trước (:15-24); cài chỉ khi signature arg#3 khớp struct (163EC:242-270). Fake-first: 1D4F8(1, size=max(a4,8)→else 120, scale=(a6>=1?a6:2.0)) (:25-32; mapping arg 1D4F8 UNKNOWN, clamp 8/120/1/2 CONFIRMED). Non-nil → synth không gọi orig (:33-35); nil → fallback orig (:40). Không DuoDash → orig (:38-41).
### A7/A8. 18888 displayName / 18918 displayNameForLocation: → fake "DuoDash"
- 1D36C(self) + 1CAF8 → CFSTR("DuoDash") không gọi orig (18888:20-21), else orig (18888:23). 18918 giống, bỏ qua location arg (18918:19-25).

## B. Dock/focus/statusbar/icon-tap (chung: 1C3C8 false → skip intercept → forward orig)
### B1. 1BB20 _dockButtonPressed: (nuốt tap, chuyển/host app)
- Trích bid: duyệt off_154130 trên sender (41-64), fallback 14A9C(sender) via .icon + off_1540B8 (65; 14A9C:27-75). Khối 162E40-- + đọc bundleIdentifier/applicationBundleIdentifier rồi release bỏ (68-80, no-op, UNKNOWN mục đích).
- Nhánh 1 DuoDash (1C3C8&&1CAF8, :81): 1635F0==0 (không split) → debounce 1.5s vs 163620 (:85-89); 163610==1 → clear 1634B0/163618 + 19330(0,0) (:91-99); **nuốt** (LABEL_36, không gọi 1638D0) (:102,106-108). Trong 1.5s nuốt không reassert (:89-90 rỗng).
- Nhánh 2 split-member (1635F0==1 && 1CA4C, :104): **nuốt**.
- Nhánh 3 bridged (1C3C8&&114B4, :110): đang split → 1CB48() clear split (:112-113; 1CB48:15-26 zero 1635F0/1634B8/1634C0/1634C8/163628 + log); !1CBA0 (chưa phải single đang host: 163610==1 && bid==1634B0, 1CBA0:17-18) + quá 1.5s → 1CC04(bid) host (:114-121; 1CC04:32-43: 8DF8(bid,1), 163610=1, 1634B0=copy, stamp 163618; đọc duodash_ab_mapcoexist 1CC04:22-30, tác dụng HYPOTHESIS); **nuốt**.
- Nhánh 4 app khác (:125-131): 1CCF4(bid,"dock-tap-other-app") teardown nếu >0.5s và không noswitchteardown (1CCF4:22-53) + 1CE54 warm/prefetch (1CE54:25-68) + **forward** off_1638D0 nếu non-nil (:129-130). off nil → nuốt lặng.
- Call-through **chỉ nhánh 4** (hoặc hosting_off).
### B2. 1BF1C takeWithPriority:... (đè focus, KHÔNG nuốt — luôn forward cuối nếu non-nil, :137-139)
- Parse (58-106): v40=(a3 NSString=="notification") (58-62); focusedPid probe bỏ kq (71-72, HYPOTHESIS vô tác dụng); v36=target bid từ a5 (74-78); v37=đang host (==1634B0) hoặc (split && 1CA4C) (81-92); v38==(TemplateUIHost) (95); v43=exists aggressive_focusteardown (107-112). Gate 1C3C8 (113).
- Single-active (163610==1, 116-124): skip teardown khi (elapsed<0.5 ? 1 : v40) | v37 (118-123) — bảo vệ 0.5s/notification/đúng-app (literal CONFIRMED; "giữ focus" HYPOTHESIS).
- Single không active (125-128): skip khi v37|v40|!split|(elapsed<0.5).
- Teardown (129-135): `if (v43 | !v38)` mới teardown — aggressive-file → teardown cả TemplateUIHost; không file → tha TemplateUIHost (literal CONFIRMED; ý đồ HYPOTHESIS). Teardown = split?1C414():1C670() (131-134; 1C414 chạy khi 1635F0==1, 1C670 khi 163610==1).
### B3. 1C29C homeButtonUp: (luôn forward orig nếu non-nil :43-44, home không bị nuốt)
- Gate 1C3C8 && (163610==1 || 1635F0==1) (:22). Knob /var/tmp/duodash_ab_nohomedismiss tồn tại → giữ home, không teardown (:24-26). Debounce qword_163850: chỉ teardown khi uptime>=163850 (:29-34; writer UNKNOWN). Teardown split?1C414():1C670() (:36-39).
### B4. 1D0E4 + 1D158 iconTapped[:modifierFlags:] (SB side, shared 1D1D4; wrapper: !1D1D4&&off → off(...), 1=xử lý/nuốt)
- 1D1D4 (19-60): lưu weak self 163508 (:20); bid=14A9C(icon) (:22); 162E3C-- no-op (:23-24, UNKNOWN).
- DuoDash (1C3C8&&1CAF8, :24): non-split → clear single + 19330(0,0); return 1 nuốt (:26-41). Không debounce (khác dock).
- Bridged (1C3C8&&114B4, :43): split → 1CB48(); !1CBA0 → 1CC04 host; return 1 (:45-49). Không debounce.
- App khác: 1CCF4(bid,"icon-tap-other-app") + 1CE54 + return 0 → caller forward (:51-55). Lưu ý 1D1D4:53-54 gọi 1CE54(v5) sau objc_release(v5) — use-after-release theo mặt chữ (HYPOTHESIS artifact retain/autorelease, cần verify asm).
- Call-through chỉ khi không DuoDash/bridged (hoặc hosting_off) và off non-nil; off nil + 1D1D4==0 → tap rơi (HYPOTHESIS).

## C. Trả lời trực tiếp
1. Fake/synth: policy object mutate tại chỗ (launchUsingTemplateUI=0, CarPlaySupported=1, CanDisplayOnCarScreen=1 — 17EC4:86-90,117-119); declaration synth {bundle=bid, SupportsMaps=1} khi orig nil + bridged/DuoDash (18318/18490/1DB14); icon synth DualAppsIcon.png chỉ bid==DuoDash (185C8/1875C); displayName literal "DuoDash" (18888/18918).
2. Dock nuốt DuoDash/bridged/split-member, forward app lạ; focus không nuốt (teardown trước forward, bảo vệ 0.5s/notification, aggressive-file); home luôn forward + knob nohomedismiss; icon-tap mirror dock không debounce. DUODASH_AB_DOCK_HOOKED = env guard installer (18A7C:17,62), knobs runtime = files /var/tmp/duodash_ab_*.
3. 1CAF8 = bid=="com.sensetechlab.duodash" duy nhất; bridged list = 114B4 (163450 bridgedApps + enabled − navprovider_selected − split_carplay_ui).
