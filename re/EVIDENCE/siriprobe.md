# EVIDENCE/siriprobe.md — P3-4 SiriProbe end-to-end (session-006)
_Nguồn: subagent general đọc decompile. Mỗi claim có file:line + nhãn._

## 0. Installer (4C34.c)
- Chỉ cài khi latch `siriprobe` off (`9C530==0`, :1294) + master enable (1295). Target `SiriActivationService`, dlopen fallback mode 17→1 (:1297-1306).
- 7 hooks qua 88A80 (validate return-type+argc+arg-types trước MSHookMessageEx, 88A80:29-64; orig → off_164A08/10/18/20/28/30/38, 4C34:1308-1363):

| # | Replacement | Selector | Check | Orig |
|---|---|---|---|---|
|1|889D0|activationRequestFromButtonIdentifier:context:|118/"q@"|164A08 (1308-1315)|
|2|88BC8|buttonDownFromButtonIdentifier:timestamp:context:|118/"qd@"|164A10 (1316-1323)|
|3|88C98|buttonUpFromButtonIdentifier:deviceIdentifier:timestamp:context:|118/"q@d@"|164A18 (1324-1331)|
|4|88D7C|buttonLongPressFromButtonIdentifier:context:|118/"q@"|164A20 (1332-1339)|
|5|88E2C|prewarmFromButtonIdentifier:|118/"q"|164A28 (1340-1347)|
|6|88EA0|handleActivationRequest:|66/"@"|164A30 (1348-1355)|
|7|88F48|activationRequestFromVoiceTriggerWithContext:|118/"@"|164A38 (1356-1363)|
- Sau hook: 88FD0 reload prefs-cache (:1364); 3 notify blocks 130618 (settings.changed) / 130638 (voicecmd.changed) / 130658 (fakepress) (:1365-1383, opaque); 890A0 warm-cache (:1388-1390).
- Rate-limit counters init 0xA cho 16 buckets 164A40 + 2 buckets 164A80/84, guard 164A00 (:1279-1291).

## 1. Gate helper 894F0 (894F0.c:9)
`sub_894F0(path, lastCheck*, cached*)`: chỉ stat lại nếu uptime-last>=0.5s (:17-30); cache stat==0 (tồn tại) (:22-25); return cached&1 (:31). = kiểm tra tồn tại file, throttle 0.5s/process.
- Mọi hook truyền `/var/tmp/duodash_siriprobe_off` + cùng cache &163228/&164A88 (889D0:16, 88BC8:16, 88C98:18, 88D7C:16, 88E2C:14, 88EA0:17, 88F48:16, 89764:17, 89880:16). Swallow thêm cặp riêng &163230/164A89 + path `.../swallow` (89764:21).
- Writer của siriprobe_* files: 0 hit toàn decompile (chỉ readers) — controller ngoài, UNKNOWN.

## 2. Logger 89590 (89590.c:9, callers 889D0/88BC8/88C98/88D7C/88EA0)
- Rate-limit: bucket &164A40[bid] (0<=bid<0x10) else &164A80/84; atomic decrement (36-47); chỉ build string khi counter>=0 (~11 lần đầu mỗi bucket rồi im, không reset) (48, HYPOTHESIS con số/mục đích).
- Nội dung: `"    [backtrace %@ bid=%lld thread=%@]\n"` + main/background (50-62); backtrace 40 bỏ frame 0 (50,63-65); mỗi frame dladdr → basename+offset+symbol hoặc unresolved (67-101).
- **Sink UNKNOWN**: build rồi release, không NSLog/fopen/notify (103). Tác dụng duy nhất: tiêu 1 counter. Callers bỏ return (comma-operator) → không ảnh hưởng control-flow (889D0:17, 88C98:19, 88D7C:17).

## 3. Swallow gate 89764 + press-eligible 89880
- **89880(bid)** (89880.c): off → 0; bid!=6 → 0 (18; 6 HYPOTHESIS side-button). Qua → 890A0(buf) đọc voicecmd_selected (22); buf rỗng → 0 (23-26); else return voicecmd_enabled (22-24). ⟺ bid==6 && !off && enabled && selected hợp lệ.
- **89764(bid)** (89764.c:9, return 1 = nuốt): (1) off → 0 (17-18); (2) 89880!=0 → 1, không cần file swallow (19-20); (3) file swallow vắng → 0 (21-22); (4) đọc swallow_id trim (23-36), longLongValue==bid → 1 else 0 (37-40); (5) id rỗng/absent → 1 = swallow mọi bid, wildcard (30,42-45, HYPOTHESIS ý đồ).
- swallow (tồn tại) = master-switch theo-bid; vắng → chỉ press voicecmd hợp lệ bị swallow. swallow_id = filter số. Cả hai vô hiệu khi off tồn tại.

## 4. Từng hook body
- **889D0** (activationRequest): off → orig luôn, không log (16-19). On → 89590(...) rồi orig iff !swallow (17). Forward nguyên args (14-19). Không file/post/đếm thêm.
- **88BC8** (buttonDown, duy nhất có side-effect thêm): off → LABEL_5 orig (16-17,22-23). On → luôn 89590 (18); nếu 89880 → 89338() post voicecmd.press.<bid> (19-20, **kể cả khi sắp bị swallow**). Cuối: orig iff !swallow (21-23).
- **88C98** (buttonUp): như hook 1 (18-22, orig 164A18).
- **88D7C** (longPress): như hook 1/3 (16-20, orig 164A20).
- **88E2C** (prewarm): passthrough thuần — gọi 894F0 chỉ refresh cache (14), luôn orig 164A28 (14-15). Không log/swallow.
- **88EA0** (handleActivationRequest): log-only — !off → 89590(..., -1 → bucket 164A84) (17-18 + 89590:39-40); luôn orig 164A30, return giá trị (19-22). Không swallow.
- **88F48** (voiceTrigger): passthrough thuần (16-17).
- Ma trận: **swallow chỉ 4 hooks nút** (889D0/88BC8/88C98/88D7C) khi off-vắng + 89764==1. 4 hooks khi không swallow: log 1 lần + forward. 88EA0 log + luôn forward. 88E2C/88F48 forward thuần. off tồn tại: forward không log (4 nút + 88EA0).

## 5. Prefs-cache voicecmd (88FD0/890A0/891F0)
- **891F0(outEnabled, outBid97)**: voicecmd_enabled chỉ true khi key tồn tại VÀ true (thiếu = disabled) (24-36); voicecmd_selected copy (38-48); validate reverse-DNS (1..0x60 chars, [0-9A-Za-z.-], không leading/trailing dot, bắt buộc ≥1 dot, else xóa trắng) (49-80).
- **88FD0()**: full reload (Synchronize + 891F0 + cache byte_164A90/unk_164A91 + ts 163238 dưới lock 164A8C, 16-26). Gọi tại install (4C34:1364) + thunks 894E8/894EC (callers:none).
- **890A0()**: cached read (<2s trả cache, >=2s re-read + update, 19-42); return enabled (42).

## 6. fakepress: poster duy nhất + handler opaque
- Poster duy nhất: CNVoiceCmdSettingsController didSelectRow section==2 → CFNotificationCenterPost(fakepress) + alert testsent (92DFC:59-67, post :64; label sendtest 92934:83 HYPOTHESIS).
- Handler block 130658 (4C34:1378-1383) opaque, UNKNOWN. Ứng viên 89334 (thunk → 89338, callers:none, 89334:9-12) vì 89338 là poster duy nhất voicecmd.press.* (grep 1 hit, 89338:67) — HYPOTHESIS mapping.
- Nếu đúng: đọc selected via 890A0 (89338:35); rỗng/disabled → silent no-op (36); validate BID (38-65, len+33<=0x81); build "com.sensetechlab.voicecmd.press.<bid>" (67-68); register_check + set_state(now_ms) + post (73-79). = transform của 88BC8 press thật (88BC8:19-20).

## 7. voicecmd.changed posters/handlers + rescan
- Posters: 9332C (set pref + sync + post Darwin, 9332C:13-26, post :21-26; gọi từ 92BD0:14 enabled, 93310:13 selected); 81CE4:530 (selected trỏ handler đã gỡ → reset rỗng + 82830 post).
- Handlers: block 130638 (4C34:1371-1376, opaque UNKNOWN); thunks 894E8/894EC → 88FD0 (HYPOTHESIS mapping; effect reload-cache CONFIRMED nếu gọi). Prefs-UI 920C0 chỉ observe language + listchanged (không voicecmd.changed).
- Rescan: posters rescan từ viewWillAppear 91EE0:24-30 + tap section-0 92DFC:136-138; observer 7F14C:89-95 → 7FD94 → async queue 1647C0 12FBD0 (11-13, opaque). Worker 81CE4 quét VoiceHandlers/*.plist (DuoDash + TrueDash, 111-116), v==2 (194), handler==filename (239-242), handlerName cắt 48 (255-260), check installed LSApplicationProxy (270-313), ghi voicecmd_seen (392-398), migrate wheelbutton_gm_voice + voicecmd_migrated (402-490), purge stale selected rồi luôn post listchanged (535). Linkage rescan→81CE4 via 8290C/81CC4 (HYPOTHESIS).
- Consumer voicecmd.press.<bid>: 0 hit decompile (tweak ngoài via plist + CNVoiceCommandRegister; hướng dẫn 92DFC:113-119) — CONFIRMED vắng mặt / HYPOTHESIS ngoài.

## 8. UNKNOWN giữ lại
1. Sink log-string 89590. 2. Bodies 130618/130638/130658 + mapping 894E8/894EC, 89334↔fakepress. 3. Bodies 12FAB0/12FAD0/12FBD0. 4. Writer siriprobe_* files. 5. bid==6 label, encoding 4.
