// RECONSTRUCTION/SiriProbe.m — APPROXIMATION synthesis (session-027)
// Source: EVIDENCE/siriprobe.md (installer + gates + 7 hooks + voicecmd cache + fakepress/rescan).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên (U-refs).
// Semantics phải giữ: latch + master-enable gates, dlopen fallback, validate-signature,
//   file-gate throttle/cache, swallow-vs-log matrix, rate-limit buckets, notify wiring.

#import "DuoDashShared.h"
// Records: EVIDENCE/siriprobe.md (session-006, subagent FULL reads).

// ---- Installer (EVIDENCE §0; 4C34.c:1279-1390) ----
static void DDInstallSiriProbe(void) {
    // Gate: latch siriprobe off (9C530==0) + master enable (byte_168D19==1).
    // Target SiriActivationService; chưa load → dlopen framework (mode 17 → fallback mode 1).
    // 7 hooks via 88A80 (validate return-type + argc + arg-types trước MSHookMessageEx;
    //   orig → off_164A08/10/18/20/28/30/38):
    //   889D0=activationRequestFromButtonIdentifier:context: (118/"q@");
    //   88BC8=buttonDownFromButtonIdentifier:timestamp:context: (118/"qd@");
    //   88C98=buttonUpFromButtonIdentifier:deviceIdentifier:timestamp:context: (118/"q@d@");
    //   88D7C=buttonLongPressFromButtonIdentifier:context: (118/"q@");
    //   88E2C=prewarmFromButtonIdentifier: (118/"q");
    //   88EA0=handleActivationRequest: (66/"@");
    //   88F48=activationRequestFromVoiceTriggerWithContext: (118/"@").
    // Sau hook: 88FD0 reload prefs-cache; 3 notify blocks (settings.changed/voicecmd.changed/
    //   fakepress — bodies opaque, U02); 890A0 warm-cache.
    // Counters init 0xA cho 16 buckets 164A40 + 2 buckets 164A80/84 (guard 164A00).
}

// ---- Gate helper 894F0 (EVIDENCE §1) ----
static int DDProbeGate(const char *path /*siriprobe_off, chung cache*/) {
    // Chỉ stat lại nếu uptime-last>=0.5s; cache stat==0 (tồn tại); return cached&1.
    // = kiểm tra tồn tại file, throttle 0.5s/process. Mọi hook + swallow dùng chung
    //   cache &163228/&164A88; swallow thêm cặp riêng &163230/164A89 + path .../swallow.
    // Writers siriprobe_* files: 0 hit decompile — controller ngoài (UNKNOWN U04).
    return 0; // APPROXIMATION returns
}

// ---- Logger 89590 (EVIDENCE §2; sink UNKNOWN) ----
static void DDProbeLog(const char *name, long long bid) {
    // Rate-limit: bucket 164A40[bid] (0<=bid<0x10) else 164A80/84; atomic decrement;
    //   chỉ build string khi counter>=0 (~11 lần đầu mỗi bucket rồi im, không reset — HYPOTHESIS).
    // Nội dung: "[backtrace %@ bid=%lld thread=%@]" + main/background; backtrace 40 bỏ frame 0;
    //   mỗi frame dladdr → basename+offset+symbol hoặc unresolved.
    // SINK UNKNOWN (build rồi release — không NSLog/fopen/notify). Tác dụng duy nhất: tiêu counter.
    // Callers bỏ return (comma-operator) → không ảnh hưởng control-flow.
}

// ---- Swallow gate 89764 + press-eligible 89880 (EVIDENCE §3) ----
static int DDPressEligible(long long bid) {
    // 89880: off → 0; bid!=6 → 0 (6 HYPOTHESIS side-button); qua → 890A0 đọc
    //   voicecmd_selected (rỗng → 0) else return voicecmd_enabled.
    // ⟺ bid==6 && !off && enabled && selected hợp lệ.
    return 0; // APPROXIMATION returns
}
static int DDShouldSwallow(long long bid) {
    // 89764 (return 1 = nuốt): (1) off → 0; (2) 89880!=0 → 1 (không cần file swallow);
    //   (3) file swallow vắng → 0; (4) swallow_id trim, longLongValue==bid → 1 else 0;
    //   (5) id rỗng/absent → 1 = swallow mọi bid (wildcard — HYPOTHESIS ý đồ).
    // File swallow = master-switch theo-bid; cả hai vô hiệu khi off tồn tại.
    return 0; // APPROXIMATION returns
}

// ---- 7 hook bodies (EVIDENCE §4; ma trận swallow-vs-log) ----
static void DDHookActivationRequest(long long bid /*, ...args forward nguyên */) {
    // 889D0: off → orig luôn, không log. On → log (...) rồi orig iff !swallow.
    // Không file/post/đếm thêm.
}
static void DDHookButtonDown(long long bid /*, ...*/) {
    // 88BC8 (duy nhất có side-effect thêm): off → orig. On → luôn log;
    //   nếu eligible → post voicecmd.press.<bid> (89338 — KỂ CẢ khi sắp bị swallow).
    //   Cuối: orig iff !swallow.
}
static void DDHookButtonUp(long long bid /*, ...*/) { /* 88C98: như hook 1 (orig 164A18). */ }
static void DDHookLongPress(long long bid /*, ...*/) { /* 88D7C: như hook 1/3 (orig 164A20). */ }
static void DDHookPrewarm(long long bid) {
    // 88E2C passthrough thuần: gọi gate chỉ refresh cache; luôn orig; không log/swallow.
}
static id DDHookHandleRequest(id req) {
    // 88EA0 log-only: !off → log (bid giả -1 → bucket 164A84); luôn orig + return giá trị.
    // Không bao giờ swallow.
    return nil; // APPROXIMATION returns
}
static void DDHookVoiceTrigger(/* ... */) {
    // 88F48 passthrough thuần (như prewarm).
}
// Ma trận: swallow CHỈ 4 hooks nút khi off-vắng + swallow==1; không swallow → log 1 lần + forward.

// ---- Voicecmd prefs-cache (EVIDENCE §5) ----
static void DDVoiceCmdReload(void) {
    // 88FD0: Synchronize + 891F0 + cache byte_164A90/unk_164A91 + ts (lock 164A8C).
    // 891F0: enabled chỉ true khi key tồn tại VÀ true (thiếu = disabled);
    //   selected copy; validate reverse-DNS (1..0x60 chars, [0-9A-Za-z.-],
    //   không leading/trailing dot, bắt buộc ≥1 dot, else xóa trắng).
    // 890A0: cached read (<2s trả cache, >=2s re-read; return enabled).
    // Thunks 894E8/894EC (callers:none) → 88FD0.
}

// ---- fakepress + rescan (EVIDENCE §6-7; handlers opaque) ----
static void DDFakePressTest(void) {
    // Poster duy nhất: prefs-UI didSelectRow section==2 → post fakepress + alert testsent.
    // Handler block opaque (ứng viên 89334→89338 HYPOTHESIS): đọc selected (rỗng/disabled →
    //   silent no-op); validate BID; build "com.sensetechlab.voicecmd.press.<bid>";
    //   register_check + set_state(now_ms) + post. = transform của press thật.
}
static void DDVoiceCmdRescan(void) {
    // Posters rescan (viewWillAppear + tap) → observer 7F14C → 7FD94 → async queue 1647C0
    //   (block opaque) → worker 81CE4: quét VoiceHandlers/*.plist (DuoDash + TrueDash),
    //   v==2, handler==filename, handlerName cắt 48, check installed (LSApplicationProxy),
    //   ghi voicecmd_seen, migrate wheelbutton keys + voicecmd_migrated,
    //   purge stale selected rồi LUÔN post listchanged. Linkage rescan→worker HYPOTHESIS.
    // Consumer voicecmd.press.<bid>: 0 hit decompile (tweak ngoài via plist + register).
}
// Posters voicecmd.changed: 9332C (prefs-UI set+sync+post) + 81CE4:530 (purge-selected).
// Handlers: block opaque; thunks →88FD0 (mapping HYPOTHESIS, effect reload-cache CONFIRMED nếu gọi).
