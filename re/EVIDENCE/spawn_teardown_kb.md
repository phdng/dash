# EVIDENCE/spawn_teardown_kb.md — Q-11B spawn/teardown + KB observers + poll helpers (session-007)
_Nguồn: subagent general đọc FULL 17+7 files. Mỗi claim có file:line + nhãn._

## A. 17 callees của onHostState: (9D64)
Context caller: hostRefused==1 → refuse branch (744-769); else sbPid→1635EC, activated→v131, bid→v128, cpuiBid/Gen/Killed/Rect/More (205-246); !activated/bid rỗng/spike → B8F8 + LABEL_20; 1635F0==1 → async B768; LABEL_20 cpuiKilled → 163570; LABEL_66 cpuiMore (205-246,248-727 CONFIRMED).

### 1. B768(a1) — notify SB active bid + refresh dock (B768.c)
Input a1 block, bid tại a1+32 (:44). Lấy sub_15F40() (:21); responds appHistory → _bundleIdentifierDidBecomeVisible:previous:@"com.sensetechlab.duodash",0 (:25-36). Chọn bid: a1+32 nếu length>0 else 1634B8/1634C0 (:44-55); có length + responds → setActiveBundleIdentifier:animated:bid,1 (:57-58); responds _refreshAppDock → gọi (:59-61). Không post/global trong file; object ngoài HYPOTHESIS SB/HomeScreen (class 15F40() UNKNOWN). 15F40 nil → chỉ release (:23,65); thiếu selector → lặng lẽ skip.
### 2. BBF8(key,gen) — evict có điều kiện generation (BBF8.c)
key rỗng → no-op (:18). Lock unk_163648, lookup 163510[key] (:20-24). a2==0 → xóa luôn; !=0 → chỉ xóa khi 163518[key]==a2 (:25-40); xóa cả 163510/163518 (:38-42). Chỉ ghi dicts, không post/986C. Callers 9D64/B9A8/D154.
### 3. BCDC() — cancel timer/source 163558 (BCDC.c:9)
!=0 → dispatch_source_cancel + =0 + release (:13-18); nil → idempotent no-op. Chỉ clear global. Gọi từ B9A8 nhánh 163550 + 9D64:391.
### 4. BD18(key,w,h) — register size + bump generation (BD18.c:9)
Guards length==0 / w<1||h<1 → return (:18,20). Dưới lock: 159FC() ensure (:23); 163510[key]=CGSize value (:28-29); ++163718 (:31); 163518[key]=NSNumber ULL (:32-33, đối số decompiler nuốt — UNKNOWN giá trị gen). Không post.
### 5. BE34(str) — predicate "is base app?" (BE34.c:9)
Rỗng → nil (:35-37). base = 155D8() (bỏ  FAF0, :19-20); base rỗng → nil (:22-31); isEqual → 1 else containsString ([base contains:query], :24-27). Không side-effect. "base" HYPOTHESIS tên, hướng chứa CONFIRMED.
### 6. BEE4(outFlag*,x,y) — kiểm tra/move view (BEE4.c:9)
*out=0 nếu non-nil (:24-25). View = 12988() (bỏ FAF0, :26-27); nil → return nil (:57-60). superview nil → return (:31-35). Có superview: convertPoint:fromView:0 (:36-38); lệch<=0.5 cả 2 → đúng vị trí, return 1, *out=0 (:41-47); else setFrame:v11,v13 → return 1, *out=1 (:50-53). setFrame size có giữ UNKNOWN. Không global/post.
### 7. BFF4(bid,gen,retry,rect) — dispatcher confine/retry/timeout (BFF4.c:9)
Gate: 163528.length>0 && 1636E8==a2 else return (:41-45, khớp 9D64:394-400). !BE34: retry<=0 → B9A8(0)+986C(gen,bid,0,"launch_timeout") (:49-53); còn retry → after 100ms 15238 (:55-67). BE34: a3<1 → bỏ qua (:71-74); else FAF0+13220, 13220 nil + 163720<=9 → ++ + after 100ms 14C80 (:77-101); có env → 14CA0(rect) test confine (:104): true → 163538=FAF0 + 14E74(bid,gen,30,rect) (:105-111); false → B9A8(1)+986C "confine_failed" (:115-116). Ghi 163538, post 986C, schedule retry.
### 8. C2A4(bid) — lookup killed-list + knob deathwait (C2A4.c)
Rỗng → nil (:17-20); else 163570[bid] (:18). Trả array iff NSArray + count>0 + byte_163748==1 + file nodeathwait VẮNG + 14080(bid,array)==0 (:22-26); else nil (:30-32). Pure predicate. D4C4 + 9D64:451-452 dùng chọn CB08 vs C37C.
### 9. C37C(bid,gen,rect) — event-launch DB/CAR rồi BFF4 (324 dòng, 3 tầng)
Base fast-path: BE34 → BFF4(...,0) (:61,321). Cached validator: F654 + 1439C, 145F8(env,bid) true → 163530=copy + BFF4(...,30) (:63-72). Heavy event, gate file noeventlaunch vắng (:79): introspect DBApplicationLaunchInfo/DBEvent vs CARApplicationLaunchInfo/CAREvent, ivar _application/_activationSettings, mode 0..3, validate signatures, build F4B0/F9B8+14744/14820 → launchInfo → event(4) → handleEvent: (:81-271). v25==1 → 163530 + BFF4(...,30) (:305-311); fail → B9A8(0)+986C "no_launch_route" + reason chi tiết (unknown_launch_info/shape/no_environment/handleEvent_shape/no_launch_info/no_event/no_app_info/not_this_os/knob) (:144-299,313-317). Class OS cụ thể HYPOTHESIS, flow CONFIRMED.
### 10. CB08(bid,array,retries,check,done,startT) — waiter retry 50ms (CB08.c:9)
check()[2]() ==0 → return (:31). 14080(bid,array)!=0 → done ngay (:33-35). Hết retry → lock 1423C, đọc 163560[bid] (bỏ), done (:39-47); còn → after 50ms 1427C retained (:51-66). Không post trực tiếp; D4C4 gọi 20 retries (D4C4:63); 9D64:473 retry-count UNKNOWN (decompiler cắt args).
### 11. CCEC() — lazy-init 7 containers (CCEC.c:9)
163578 Dict, 163580 Array, 163588 Dict, 163590 Set, 163598 Set, 1635A0 Set, 1635A8 Dict — nil thì tạo (:26-74). Idempotent. Gọi từ D4C4/CE5C/9D64.
### 12. D01C(bid,gen,retry,rect) — gate base rồi D4C4 hoặc retry (D01C.c)
Gate 1637A0==a2 else no-op (:25). BE34==1: retry<=0 → 986C "is_base_app" (:29-31); còn → after 100ms 14060 (:35-48). Không base → D4C4 ngay (:53). Caller 9D64:621 non-base, 9D64:614 base-fail.
### 13. D154(bid,a2) — teardown một bid (D154.c:9)
VC=163578[bid], xóa 163588[bid], probe 13AB8 (:39-42). VC + EEF0 + responds backgroundSceneWithCompletion: → copy bid, gọi block 13F90(a2^1, v5&(a2^1)), schedule after 15s 14040 nếu (v5 & ~a2) + after 15s 1404C nếu ~a2, v14=1 (:45-91); else v14=0 (:94-96). Detach vô điều kiện nếu VC: 10188, willMoveToParent:nil, viewIfLoaded.hidden=0, removeFromSuperview, removeFromParent (:97-105). a2==1 → 163590 add (giữ tombstone, :107-109); else xóa 163590, F150(vc,v14), xóa 163578[bid], v14==0 && !(v5^1) && !a2 → BBF8(bid,v28) (:111-118). Cuối: 163588.count==0 → 127B4() (:121-122). Không post trực tiếp.
### 14. D4C4(bid,gen,rect) — router spawn: fast D684 hay CB08 (D4C4.c)
CCEC() (:29); 163588[bid] && 163578[bid] → D684 fast re-layout (:30-38). Else v15=C2A4(bid) (:42): non-nil → CACurrentMediaTime + CB08(copy,killed,20,E7C4-check,E7DC-done) (:45-63); nil → D684 (:69). Không notify.
### 15. CE5C() — teardown toàn cục (CE5C.c:9)
CCEC() rồi copy allKeys 163588 → D154(key,0) từng key (:33-60); copy 163590 → D154 từng object (:66-86); removeAllObjects 163590 + 1635A8, return xóa 1635A8 (:88-89). Gọi từ 9D64:727 khi !activated.
### 16. B9A8(keep) — abort/reset bid hiện tại (B9A8.c:9)
Nhánh 1 (163528 non-empty): giữ bid, ++1636E0, clear 163540/15278/163528/rect/1636E8/163538/1636F0, v7=BE34 (:30-49). a1 && 163530==bid && v7 → 13AB8+15CBC, copy, after 3s 15DA4 (:50-68, grace delayed-evict HYPOTHESIS); else BBF8(bid,0) + v7→15A94 (:72-74); clear 163530 + 1636D8=0 (:76-80). Nhánh 2 (163550 non-empty): clear + BCDC + BBF8 + BE34→15A94 (:82-96); cả hai rỗng → no-op. Không post trực tiếp.
### 17. B144(label) — dock-hide ticker + timer 1s (B144.c)
Non-main → async 16398 return (:74-82). LoadWeak 1635D8 window, nil → 161F8() tạo + storeWeak (:84-92). 1635F0!=1 || !window → cancel timer 1635E0 + restore hidden theo 1637D0/1637D1 (:93-95,214-235). Hide chỉ khi file nodockhide VẮNG + 1635EC>=1 + kill(pid,0)==0||EPERM; else LABEL_33 không hide (:96-97, điều kiện đảo). Chọn bid: 163528 nếu rect ∩ window.bounds (via 163A0), else quét 163588[*]["rect"] rồi 1635A8[*] (:105-196); nil nếu không khớp. Timer 1635E0 1s (1s, 0x3B9ACA00, 0xEE6B280) + handler 12D0A8 nếu chưa có (:205-244); bookkeeping 1637D0/1637D1/1637D8 + setHidden:1 nếu visible (:246-261, hide-semantics HYPOTHESIS).
- Ack chung: 986C(gen,bid,ok,why) → 8D78 cpui.status (986C:23-54); why: launch_timeout/confine_failed (BFF4:52,116), already (9D64:422), no_launch_route (C37C:316), is_base_app (D01C:31, 9D64:611).

## B. CNABKeyProbeObserver: onKbShow/onKbHide/onDismiss/onEndEditing
Đăng ký 4CBDC (guard DUODASH_AB_UIAPP_IPC_HOOKED, 27-29): Darwin apply→4CF3C/dismiss→4CFBC/card→4D03C/fallback→4D050 (68-100); NSNotification onKbShow:WillShow/onKbHide:WillHide/onEndEditing:TextField+TextViewDidEndEditing (102-129).
### 1. onKbShow: (44AE8.c:9-11) — stub rỗng, body `;`, callers/callees none. No-op dù đã đăng ký.
### 2. onKbHide: (44AEC.c:9-11) — stub rỗng tương tự. No-op.
### 3. onDismiss: (44AF0.c:11-15) — `if(163ED9==1){ 162F58>=1 → --; 449C8(); }`. Header callees-none stale (thực tế gọi 449C8). Không đọc plist/post.
- 449C8 (9-40): 163F5A=0,163F59=0,++163F60, clear 163F48 + weak 163F30 + 163F38, 164148=0; weak responder tồn tại → 164150=1, setInputView:nil+reload (nếu responds), resignFirstResponder (nếu responds), 164150=0. Đk: 163ED9 + responder tồn tại.
### 4. onEndEditing: (45180.c FULL) — teardown có điều kiện + post end
Gate 163ED9 (22). 162F88==0 → 163F58=0,164130=0, return (24-28). v4=453B8("nokeypane", TTL 1s cache 453B8:26) (30); 163F58=164130=v4^1 (31-32); v4==1 (knob tồn tại) → return, không teardown (33-85, logic đảo). Knob vắng: notification.object vs weak 163F30 — nil/khác → v8=0; bằng + 163F59!=1 → v8=1; bằng + 163F59==1 → 163F59=0, --162F58, v8=0 (35-84). Chung: 162F58>=1 → -- (46-47); v8==1 → clear setInputView+reload (nếu responds), clear weak, 163F5A=0, ++163F60, và chỉ khi 163F58==1 → post keyinput.end + --162F58 lần nữa (50-73).
- Bonus đối chiếu onApply: 44B1C (không yêu cầu nhưng đã đọc): in.plist via 454F4 (53; path NSTemporaryDirectory+name 454F4:16-20), keys text/ret (77,84), guard 163ED9&&163F58 (51) + 45568 reject secure (45568:17-19), diff deleteBackward/insertText hoặc setText + post TextDidChange, ret==1 → textFieldShouldReturn hoặc insertText "\n" (137-220).

## C. Poll retry + UI flush (365D4/371AC/370F8, gọi từ 22AD0)
Caller 22AD0: connected→1652B0 + uptime 1652B8 (:26-30); 162E74!=1 && v3==0 → disconnect "poll" (:32-40); v3==1 && 162E74!=1 → 163A68=5 + post cpconnect (:44-47); labels poll.retry/connect/bringup "%@#%d" 6-163A68 (:50-64); 163A68 = 365D4(label,1) ? 0 : -1 (:65-70); 163C40>0 → 371AC (main) else async (:78-92); v3==1 → 370F8 (main) else async (:95-100); chốt 162E74=v3 + after 3s 22D5C (:102-109).
### 1. 365D4(label,force) — probe resolution + persist + notify ble.status.changed (365D4.c:9)
Display 34250() nil → 0 (:40-42,96-97). FBSDisplayConfiguration initWithCADisplay (pixelSize/scale, fallback bounds/frame, :43-93); w<1||h<1 → 0 (:94). Clamp xmmword_163AA8>=40 (:101-118); lưu 163AC0=w/h, 163AD0=scale (:119-121); format "%.0f × %.0f", bucket 480p/720p/1080p (:122-138). force || !equal(163AD8/AE0) → storeStrong + SetAppValue(headunit_resolution/video_quality) + Sync + Post ble.status.changed (:140-159); return h>0 (:129,170). Side-effect duy nhất prefs+notify. Class FBSDisplayConfiguration CONFIRMED theo string.
### 2. 371AC(_) — flush dropOverdueNotice (371AC.c:9)
[DDz1 shared] → dropOverdueNotice (:13-14). Không plist/post/điều kiện/knob. Gọi tại 22AD0:86-92.
### 3. 370F8(_) — flush nudgePresent:"tick" có knob (370F8.c:9)
[DDz1 shared]; visible==0 → return; livePresentRunning==1 → return (:16-18). fileExists nonudgetick → return, vắng → nudgePresent:"tick" (:20-24). Post trong nudgePresent nếu có = UNKNOWN từ file này.
