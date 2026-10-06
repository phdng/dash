// RECONSTRUCTION/SpikeHosting.m — APPROXIMATION synthesis (session-037)
// Source: EVIDENCE/spike_hostslots.md (F-035; subagent đọc FULL 3CC44 347 dòng +
//   3BBF0 226 + 3C1F0 59 + 3D4FC 83, mỗi claim có file:line).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: skipEvict check đúng 1 lần, slot-count guard 0..3,
//   CPUI/SB/empty 3 nhánh, degrade = unhost-không-kill + placeholder,
//   geometry-push early-returns, dismiss+notify chỉ ở error-path nil.

#import "DuoDashShared.h"
// Caller: 2565C present-commit (pass-through skipEvict — cross-ref
//   RECONSTRUCTION/PresentCommitAck.m + functions/2565C.md).
// Sửa giả thiết cũ "forward nguyên vẹn": skipEvict KHÔNG forward vào hàm con
//   (3BBF0/3C1F0/3D4FC không có param skipEvict) — giữ tại 3CC44, check 1 lần.
// hostSplit/switchInPlace + spawn/teardown callees: KHÔNG ở đây
//   (EVIDENCE/hosting_engine.md + spawn_teardown_kb.md — scope R-025).

// ---- 3CC44 spikeHostSlots:natives:carPlayUI:skipEvict: (3CC44.c:9) ----
static NSArray *DDSpikeHostSlots(NSArray<NSString *> *bids, NSArray *natives,
                                 NSArray<NSNumber *> *carPlayUI, BOOL skipEvict) {
    // Sig: a3 bids NSArray<NSString>, a4 natives NSArray<NSValue CGSize>,
    //   a5 carPlayUI NSArray<NSNumber bool>. Return NSMutableArray* UIView slots
    //   autoreleased (HYPOTHESIS caller 2565C kiểm tra count).
    // skipEvict — DUY NHẤT 1 use cả chain (3CC44.c:311):
    //   `if (!a6 && exists("/var/tmp/duodash_ab_split_evict")) → [DDz2 evictFromPhone]`.
    //   =1 → ức chế nguyên vẹn evictFromPhone kể cả khi flag tồn tại;
    //   =0 → vẫn không evict nếu flag vắng. Ngoài điểm đó không kill/unhost/dismiss/
    //   giữ-xóa view/degrade/geometry/slot/DDz1/notify nào khác.
    //   (Nội bộ evictFromPhone: kill? unhost? replacePane? remove view? — UNKNOWN.)
    // Slots: v14=min(counts); guard v14 in 0..3 (v14>=4 → return nil, không
    //   tạo/dismiss/notify); loop k: bid sanitized 3DD4C + native CGSizeValue →
    //   spikeCreateSlot:index:native: → addObject. Không xóa slot trực tiếp
    //   (không removeFromSuperview/invalidate/nil ivar); xóa gián tiếp duy nhất
    //   evictFromPhone; dismiss + post cpdisconnect + return nil chỉ ở error-path
    //   spikeCreateSlot==nil (:298-304).
    // DDz1 calls: KHÔNG có trực tiếp (không objc_msgSend tới DDz1/present/replacePane/
    //   views/shared). Notify duy nhất: post cpdisconnect ở nhánh nil.
    // IPC-FS: đọc lscape/.tripped/.inflight + stat respring_planned/inflight + mtime,
    //   unlink .inflight, write .tripped, open/write/close .inflight pid, 372CC().
    // Globals ghi: ++163DC8, 163DC0=1, 163D48=v14, word_163D50[0..2]=carPlayUI bools,
    //   reset 163D58/163E80/163D60/163D68=0 (rồi có thể ghi đè từ AB-file),
    //   162F08=v43 (orientation? — cross-ref evidence).
    // Sau loop: scheduleGeometryPushesForSlot: mỗi slot (:313-314).
    return nil; // APPROXIMATION returns
}

// ---- 3BBF0 spikeCreateSlot:index:native: (3BBF0.c:10) ----
static UIView *DDSpikeCreateSlot(NSString *bid, NSUInteger index, CGSize native) {
    // Return: SBAppViewController.view / placeholder 36E98 / plain UIView tag 7020 / nil.
    // Ghi sổ ngay 163D88=1; guard index (unsigned)<=2 else nil → caller dismiss+notify;
    //   ghi bid→163D30[index], size→163D90[index].
    // Nhánh CarPlayUI (163D50[index]==1): w<2||h<2 → fallback carPlayDisplaySize
    //   (DDz1 shared — DDz1-use duy nhất cả chain), vẫn <2 → Zero else *2; tạo UIView
    //   frame + tag 7020 + clearColor + opaque 0 + interaction 0 + autoresizing 18.
    // Nhánh SpringBoard (bid non-empty): SBApplicationController/
    //   SBDeviceApplicationSceneEntity/SBAppViewController getClass (nil → return nil,
    //   không degrade/placeholder); sharedInstance + applicationWithBundleIdentifier:
    //   (app nil → clear 163D30 + placeholder 36E98); reset evict-state nếu
    //   163E90==163DC8 (HYPOTHESIS "đánh dấu re-host"); initWithApplicationForMainDisplay:
    //   fail → degradeSlot "its scene entity could not be made"; NSUUID +
    //   initWithIdentifier:andApplicationSceneEntity: fail → degradeSlot
    //   "its SBAppViewController could not be made"; lưu VC ivar self+8/24/32;
    //   setIgnoresOcclusions:0 + setAutomatesLifecycle:0; view nil → degradeSlot
    //   "its view is nil"; setRequestedMode:2, homeGrabberDisplayMode:1; success return view.
    // Nhánh bid rỗng → placeholder 36E98. Error → placeholder degraded (trừ 2 nil cases).
    return nil; // APPROXIMATION returns
}

// ---- 3C1F0 degradeSlot:bid:native:why: (3C1F0.c:9) ----
static UIView *DDDegradeSlot(int slot, NSString *bid, CGSize native, NSString *why) {
    // Callers duy nhất 3BBF0 (3 degrade reasons trên). Return placeholder 36E98.
    // VC cũ (ivar offset 32/24/8 theo slot) tồn tại → viewIfLoaded →
    //   removeFromSuperview (xóa khỏi hierarchy) → invalidate nếu responds
    //   (unhost/invalidate, KHÔNG kill — HYPOTHESIS nghĩa, CONFIRMED call);
    //   ivar=nil+release; clear 163D30[slot]=@""; return placeholder 36E98.
    // Không DDz1/notify/IPC. Chỉ ghi ivar + 163D30[slot]. Luôn placeholder
    //   (giả định 36E98 thành công — HYPOTHESIS).
    return nil; // APPROXIMATION returns
}

// ---- 3D4FC scheduleGeometryPushesForSlot: (3D4FC.c:9) ----
static void DDScheduleGeometryPushes(NSUInteger slot) {
    // void; caller 3CC44 (:313-314). Không tạo/xóa slot.
    // Guard slot<=2; bid 163D30[slot] rỗng → return; CPUI flag (163D50[slot]&1) → return.
    // Enumerate off_154160 delays NSNumber (NỘI DUNG delays UNKNOWN), mỗi cái
    //   dispatch_time + dispatch_after(main, block 3DC38) captures
    //   generation=163DC8, nativeSize=163D90[slot], orientation=162F08, bid copy.
    // Không DDz1 trực tiếp (downstream 3DC38 UNKNOWN). Không notify_post.
    // Chỉ đọc globals, không ghi (ngoài retain/capture).
}

// ---- Debug note (EVIDENCE §5) ----
// skipEvict=1 giữ view y hệt =0 (success→SB view, degraded→placeholder, CPUI→tag-7020);
//   không suppress dismiss/degrade/geometry. Điểm debug duy nhất:
//   breakpoint 3CC44:311 + quan sát a6 + exists split_evict.
