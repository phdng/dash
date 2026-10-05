# EVIDENCE/spike_hostslots.md — spikeHostSlots: nội bộ + skipEvict (session-009)
_Nguồn: subagent general đọc FULL 3CC44 (347 lines, 2 passes) + 3BBF0 (226) + 3C1F0 (59) + 3D4FC (83). Mỗi claim có file:line + nhãn._

## 0. Trả lời trực tiếp: skipEvict=1 khác 0 ở điểm nào?
- **Duy nhất 1 use** trong cả chain 4 file: `3CC44.c:311` — `if (!a6 && v49==1) -[DDz2 evictFromPhone]` (v49 = exists /var/tmp/duodash_ab_split_evict, :308-309).
- skipEvict=1 → ức chế nguyên vẹn `evictFromPhone`, kể cả khi file-flag tồn tại. skipEvict=0 → vẫn không evict nếu file-flag vắng.
- Ngoài điểm đó: không kill/unhost/dismiss/giữ-xóa view/degrade/geometry/slot/DDz1/notify nào khác (không còn use a6 trong 3CC44:9-347; 3 file còn lại không có tham số skipEvict: 3BBF0:10, 3C1F0:9, 3D4FC:9).
- Nội bộ evictFromPhone (kill? unhost? replacePane? remove view?) — UNKNOWN (ngoài 4 file).

## 1. 3CC44 spikeHostSlots:natives:carPlayUI:skipEvict: (3CC44.c:9)
Sig `(self,a2,a3=bids,a4=natives,a5=carPlayUI,a6=skipEvict)`: a3 NSArray<NSString> (:71,81), a4 NSArray<NSValue CGSize> (:72-76,292-293,326-327), a5 NSArray<NSNumber bool> (:73,107-115). Return NSMutableArray* UIView slots autoreleased (:289,305,333,346; HYPOTHESIS caller 2565C kiểm tra count).
- Grep a6: chỉ 2 hit (decl :9 + check :311). Gating :308-312 (defaultManager :308, exists split_evict :309, `!a6 && v49==1` → evictFromPhone :311-312).
- Slots tạo/xóa: v14=min(counts) (:74-80); guard v14 in 0..3 (v14>=4 → return nil, không tạo/dismiss/notify, :82,339-342); loop k=0..v14-1: v45=bids[k] (sanitized 3DD4C :292), v46=natives[k]+CGSizeValue (:293-294), v47=spikeCreateSlot:index:native: (:295), addObject (:305). Không xóa slot trực tiếp (không removeFromSuperview/invalidate/nil ivar); xóa gián tiếp duy nhất evictFromPhone; dismiss chỉ ở error-path spikeCreateSlot==nil (:298-304: dismiss + post cpdisconnect + nil).
- DDz1 calls: KHÔNG có trực tiếp trong body (không objc_msgSend tới DDz1/present/replacePane/views/shared). DDz1 shared + carPlayDisplaySize chỉ ở 3BBF0:65-67.
- Notify duy nhất: post cpdisconnect (:301) ở nhánh nil. Không notify/CFPrefs/xpc khác. IPC-FS: đọc lscape/.tripped/.inflight + stat respring_planned/inflight + mtime (:128,134,142,151-153), unlink .inflight (:155,173), write .tripped (:166-172), open/write/close .inflight pid (:263-271), 372CC() (:272); check split_evict (:309).
- Globals ghi: ++163DC8 (:102), 163DC0=1 (:103), 163D48=v14 (:104), word_163D50[0..2]=carPlayUI bools (:105-119), reset 163D58=0/163E80=0/163D60=0/163D68=0 (:120-124) rồi có thể ghi đè từ AB-file (:259-262), 162F08=v43 (:285-288).

## 2. 3BBF0 spikeCreateSlot:index:native: (3BBF0.c:10)
Sig `(self,a2,a3=bid,a4=index 0..2,a5=native CGSize)`. Return UIView* (SBAppViewController.view / placeholder 36E98 / plain UIView tag 7020 / nil).
- Ghi sổ ngay: 163D88=1 (:51). Guard index (unsigned)<=2 else nil → caller dismiss+notify (:52,220-223).
- Ghi bid→163D30[index] (:54-57), size→163D90[index] (:58-60).
- Nhánh CarPlayUI (163D50[index]==1, :61): width<2||height<2 → fallback carPlayDisplaySize (DDz1 shared :65-67), vẫn <2 → Zero else *2 (:63-79); tạo UIView frame + tag 7020 + clearColor + opaque 0 + interaction 0 + autoresizing 18 (:81-94, empty pane).
- Nhánh SpringBoard (163D50!=1 && bid non-empty, :96): getClass SBApplicationController/SBDeviceApplicationSceneEntity/SBAppViewController (:98-100); class nil → nil (:101-113, không degrade/placeholder); sharedInstance + applicationWithBundleIdentifier: (:109-110); app nil → clear 163D30 + placeholder 36E98 (:204-207); reset evict-state nếu 163E90==163DC8 (clear 163E98[index], 163E88=0, 162F1C=max(4,.) — :113-123, HYPOTHESIS "đánh dấu re-host"); initWithApplicationForMainDisplay: (:125) fail → degradeSlot "its scene entity could not be made" (:190-198); NSUUID + initWithIdentifier:andApplicationSceneEntity: (:128-131) fail → degradeSlot "its SBAppViewController could not be made" (:175-184); lưu VC ivar self+8/24/32 (:134-139); setIgnoresOcclusions:0 + setAutomatesLifecycle:0 (:140-143); view (:145) nil → degradeSlot "its view is nil" (:159-167); setRequestedMode:2 (:148-149), homeGrabberDisplayMode:1 (:150-153); success return retain(view) (:155,169-170).
- Nhánh bid rỗng → placeholder 36E98 (:216-218).
- DDz1: chỉ 3BBF0:65-67. Không notify/xpc. Globals: 163D88, 163D30[], 163D90[], 163E98/163E88/162F1C, ivars. Error → placeholder degraded (trừ 2 nil cases).

## 3. 3C1F0 degradeSlot:bid:native:why: (3C1F0.c:9)
Sig thực `(self,a2,a3=slot int,a4=bid,a5=native CGSize,a6=why)` (:9-12,26-27 — `why` cuối). Callers duy nhất 3BBF0 (:160,176,191). Return placeholder 36E98 (:54,58).
- skipEvict: không có (soát 1-59). Slots: ivar offset 32/24/8 theo slot (:28-34, khớp 3BBF0:134-139); VC cũ tồn tại (:37) → viewIfLoaded (:39-42) → removeFromSuperview (:43, xóa khỏi hierarchy) → invalidate nếu responds (:44-45, unhost/invalidate, không kill — HYPOTHESIS nghĩa, CONFIRMED call); ivar=nil+release (:48-50); clear 163D30[a3]=@"" (:51-53); placeholder 36E98 (:54).
- Không DDz1/notify/IPC. Chỉ ghi ivar + 163D30[a3]. Không error-nil (luôn placeholder, giả định 36E98 thành công — HYPOTHESIS).

## 4. 3D4FC scheduleGeometryPushesForSlot: (3D4FC.c:9)
Sig `(self,a2,a3=slot)`, void. Caller 3CC44 (:313-314, header :5).
- skipEvict: không có (soát 9-83). Slots: không tạo/xóa. Guard a3<=2 (:33); bid 163D30[a3] rỗng → return (:35-36,80-81); CPUI flag (163D50[a3]&1) → return (:38-39,79).
- Enumerate off_154160 delays NSNumber (:40-47), mỗi cái dispatch_time + dispatch_after(main, block 3DC38) captures generation=163DC8, nativeSize=163D90[a3], orientation=162F08, bid copy (:59-70).
- Không DDz1 trực tiếp (downstream 3DC38 UNKNOWN). Không notify_post. Chỉ đọc globals, không ghi (ngoài retain/capture). Early-returns duy nhất.

## 5. Tổng hợp chain + debug
Chain: spikeHostSlots: (3CC44) → loop spikeCreateSlot: (3BBF0) → (fail) degradeSlot: (3C1F0) + sau loop scheduleGeometryPushesForSlot: (3D4FC) mỗi slot + dismiss chỉ khi nil.
skipEvict KHÔNG forward vào hàm con (không param để forward) — giữ tại 3CC44, check 1 lần rồi bỏ (sửa giả thiết cũ "forward nguyên vẹn").
skipEvict=1 giữ view y hệt =0 (success→SB view, degraded→placeholder, CPUI→tag-7020); không suppress dismiss/degrade/geometry. Điểm debug duy nhất: breakpoint 3CC44:311 + quan sát a6 + exists split_evict.
