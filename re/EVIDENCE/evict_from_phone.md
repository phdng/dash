# EVIDENCE/evict_from_phone.md — evictFromPhone/Then: mảnh skipEvict cuối (session-010)
_Nguồn: subagent general đọc FULL 3AE48 (12 dòng) + 3AE50 (187 dòng) + helpers + grep callers. Mỗi claim có file:line + nhãn._

## 1. 3AE48 wrapper (3AE48.c:9-11)
Sig `void evictFromPhone(self,a2)`. Body 1 dòng: `evictFromPhoneThen:0` (nil completion, fire-and-forget). Không kill/unhost/notify/prefs/globals/files. Headers callers/callees:none stale (mâu thuẫn code + grep).

## 2. 3AE50 evictFromPhoneThen: (3AE50.c:9, void (self,a2,a3=completion nullable))
- a3 retain → v3/v35 (:57); return void. Mọi đường đều gọi v4 đúng 1 lần qua guard (3F088:15-27: exactly-once, main-thread?call:async; chống double-call completion SB vs watchdog 2s — cơ chế CONFIRMED, ý đồ HYPOTHESIS).
- **Bước 0**: __block BOOL done=0 (:48-51); block wrapper v34 (v36=v37, v35=v3) (:52-58); v4=retainBlock (:59); mọi LABEL_2/fallback gọi v4 (:73,168,173,179).
- **Bước 1**: fileExists `duodash_ab_noevict` (:60-61) → tồn tại → LABEL_2 gọi v4 ngay, không evict (:63-64).
- **Bước 2**: file `evict_skipfrontmost` (:66); vắng → tiếp tục (:77-80); tồn tại → v8=3EDFC(163D30[0]) (:68; 163D30[0] = bid slot0 từ hostBundleId: 3B2D8:68-71); 3EDFC = bid có phải frontmost phone (SpringBoard _accessibilityFrontMostApplication vs 3EFD4 getter, rỗng→nil — 3EDFC:20-37; 3EFD4 HYPOTHESIS frontmost-getter); frontmost → LABEL_2 (:70-75), else tiếp tục.
- **Bước 3**: getClass SBMainWorkspace + SBHomeScreenEntity (:81-82); nil → LABEL_2 (:83-87); sharedInstance (:88); phải responds createRequestWithOptions: VÀ executeTransitionRequest: else LABEL_2 (:90-92,177-180).
- **Bước 4**: createRequestWithOptions:0 (:94; nil → v4 :95,171-174); entity nếu responds (:97-99); modifyApplicationContext: + block 3F100 capture entity (:100-109); **3F100 chỉ setActivatingEntity:entity** (3F100:14-15). Không entity → nullptr, vẫn tiếp tục (:112-115).
- **Bước 5** (chỉ khi a3!=nil): chọn selector theo CF<1946.102 ? setCompletionBlock:/addCompletionHandler: (đảo, :119-128); thử cả 2 via respondsToSelector vòng while(1) (:128-140); cả 2 thiếu → v20=0 (:134-139). Gắn được: 3F164 wrap v4 (:141-148; forward 3F164:11); watchdog dispatch_time 2s + after main 3F170 cùng v21/v37 (:149-157; forward 3F170:11; guard 1-lần). v20=1 (:158). Wrapper evictFromPhone (a3=0) luôn v20=0 → không gắn block SB.
- **Bước 6**: executeTransitionRequest: (:166) — **hành động evict duy nhất: yêu cầu SpringBoard về Home** (diễn giải từ entity+setActivatingEntity, HYPOTHESIS tên). v20==0 → v4 ngay (:167-168; path wrapper: v4 rỗng, 3F088 chỉ set flag :19). Dọn release + Block_dispose (:169,175,181,183-186).
- **KHÔNG có**: kill/pid/signal/proc_pidpath; gọi DDz khác/spike/cnab/dismiss/removeFromSuperview/resign/unhost; notify_post; CFPrefs/NSUserDefaults; ghi prefs/globals/files (chỉ đọc 2 flags); unlink/write/open/close.

## 3. Callers (grep evictFromPhone = 14 matches, 3 file code + 2 trampoline)
- 3AE50:2,9 (định nghĩa), 3AE48:2,9,11 (định nghĩa + self-call), **3CC44:312** (`!a6 && exists(split_evict)`; sau đó scheduleGeometryPushes :313-314), **3B2D8:189** (evict-rồi-host: frontmost-check + !skipfrontmost + !noevict + placeholderView đen :153-176; completion 3EF20 check gen/163DC8/163D88/bid → cnabBuildSceneHostForBid + setFrame/mask/addSubview + handshake :13-30), **3B2D8:211** (fire-and-forget sau cnabBuildSceneHost thành công, trước handshake :202-212, nhánh host-trực-tiếp). B0820/B0840 trampolines objc_msgSend. Không caller kill/unhost/dismiss nào khác.

## 4. Verdict trực tiếp
- **Không kill process.** Chỉ SB transition về Home (createRequest + setActivatingEntity:Home + execute). App phone-side background gián tiếp, không SIGKILL.
- **Không remove views/resign/dismiss trực tiếp** (view work ở caller/completion: 3B2D8 placeholder + 3EF20 addSubview, hoặc 3B2D8 trực tiếp).
- **Đối lập 7792C** (reaper: pane_unload gate 7792C:115-123 + 85CDC :124 + noreap/sleeping :128-133 → 76E08 list :295 → 77098/7711C map :306-308 → proc_pidpath+strcmp+kill(9) :319-321; không chia sẻ bước nào).
- **Khác 85B8** (prefs-only: đọc ui via 7044 :22 + list via 70FC :30 → mutableCopy/removeObject/84D8 save :39-41; không transition/kill/views).
- 1 dòng: wrapper nil-completion → Then: (Home-transition + guards noevict/skipfrontmost + watchdog 2s), không kill/prefs/view-op; kill thuộc 7792C, prefs thuộc 85B8.
