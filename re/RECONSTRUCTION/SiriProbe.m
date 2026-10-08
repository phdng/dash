// RECONSTRUCTION/SiriProbe.m — executable voicecmd resolver + APPROXIMATION hook synthesis
// Source: EVIDENCE/siriprobe.md (installer + gates + 7 hooks + voicecmd cache + fakepress/rescan).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên (U-refs).
// Semantics phải giữ: latch + master-enable gates, dlopen fallback, validate-signature,
//   file-gate throttle/cache, swallow-vs-log matrix, rate-limit buckets, notify wiring.

#import "DuoDashShared.h"
#include <string.h>
#include <sys/stat.h>
#include <notify.h>
#import <os/lock.h>
// Records: EVIDENCE/siriprobe.md (session-006, subagent FULL reads).

static os_unfair_lock DDVoiceCmdCacheLock = OS_UNFAIR_LOCK_INIT;
static BOOL DDVoiceCmdCachedEnabled = NO;
static char DDVoiceCmdCachedSelected[97] = {0};
static double DDVoiceCmdCacheTimestamp = 0.0;

BOOL DDResolveVoiceCommandPreferences(NSString **selectedOut) {
    Boolean exists = false;
    Boolean enabledRaw = CFPreferencesGetAppBooleanValue(CFSTR("voicecmd_enabled"),
                                                          CFSTR("com.sensetechlab.duodash.settings"),
                                                          &exists);
    BOOL enabled = enabledRaw && exists;

    char selected[97] = {0};
    CFPropertyListRef raw = CFPreferencesCopyAppValue(CFSTR("voicecmd_selected"),
                                                      CFSTR("com.sensetechlab.duodash.settings"));
    if (raw) {
        if (CFGetTypeID(raw) == CFStringGetTypeID()) {
            CFStringGetCString((CFStringRef)raw,
                               selected,
                               sizeof(selected),
                               kCFStringEncodingUTF8);
        }
        CFRelease(raw);
    }

    if (selected[0]) {
        size_t length = strlen(selected);
        BOOL valid = length > 0 && length <= 96 && selected[0] != '.' && selected[length - 1] != '.';
        BOOL sawDot = NO;
        for (size_t index = 0; valid && index < length; index++) {
            unsigned char ch = (unsigned char)selected[index];
            if (ch == '.') {
                sawDot = YES;
                continue;
            }
            BOOL digit = ch >= '0' && ch <= '9';
            BOOL alpha = (ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z');
            if (ch != '-' && !digit && !alpha)
                valid = NO;
        }
        if (!valid || !sawDot)
            selected[0] = '\0';
    }

    if (selectedOut) {
        NSString *resolved = selected[0] ? [NSString stringWithUTF8String:selected] : @"";
        *selectedOut = resolved ?: @"";
    }
    return enabled;
}

void DDReloadVoiceCommandPreferenceCache(void) {
    CFPreferencesAppSynchronize(CFSTR("com.sensetechlab.duodash.settings"));
    NSString *selected = nil;
    BOOL enabled = DDResolveVoiceCommandPreferences(&selected);
    const char *utf8 = [selected UTF8String] ?: "";
    double now = [[NSProcessInfo processInfo] systemUptime];

    os_unfair_lock_lock(&DDVoiceCmdCacheLock);
    DDVoiceCmdCachedEnabled = enabled;
    strlcpy(DDVoiceCmdCachedSelected, utf8, sizeof(DDVoiceCmdCachedSelected));
    DDVoiceCmdCacheTimestamp = now;
    os_unfair_lock_unlock(&DDVoiceCmdCacheLock);
}

typedef struct {
    double timestamp;
    BOOL exists;
} DDSiriProbeFileGateCache;

static DDSiriProbeFileGateCache DDSiriProbeOffGate = {0};
static DDSiriProbeFileGateCache DDSiriProbeSwallowGate = {0};

static BOOL DDSiriProbeFileExistsCached(const char *path, DDSiriProbeFileGateCache *cache) {
    double now = [[NSProcessInfo processInfo] systemUptime];
    if (now - cache->timestamp >= 0.5) {
        struct stat st;
        cache->exists = stat(path, &st) == 0;
        cache->timestamp = now;
    }
    return cache->exists;
}

BOOL DDVoiceCommandPreferenceCache(NSString **selectedOut) {
    double now = [[NSProcessInfo processInfo] systemUptime];
    char cachedSelected[97] = {0};
    BOOL enabled;
    double age;

    os_unfair_lock_lock(&DDVoiceCmdCacheLock);
    age = now - DDVoiceCmdCacheTimestamp;
    enabled = DDVoiceCmdCachedEnabled;
    if (selectedOut && age < 2.0)
        strlcpy(cachedSelected, DDVoiceCmdCachedSelected, sizeof(cachedSelected));
    os_unfair_lock_unlock(&DDVoiceCmdCacheLock);

    if (age >= 2.0) {
        NSString *selected = nil;
        BOOL refreshedEnabled = DDResolveVoiceCommandPreferences(&selected);
        const char *utf8 = [selected UTF8String] ?: "";

        os_unfair_lock_lock(&DDVoiceCmdCacheLock);
        enabled = refreshedEnabled;
        DDVoiceCmdCachedEnabled = refreshedEnabled;
        strlcpy(DDVoiceCmdCachedSelected, utf8, sizeof(DDVoiceCmdCachedSelected));
        DDVoiceCmdCacheTimestamp = now;
        os_unfair_lock_unlock(&DDVoiceCmdCacheLock);

        if (selectedOut)
            strlcpy(cachedSelected, utf8, sizeof(cachedSelected));
    }

    if (selectedOut) {
        NSString *selected = cachedSelected[0] ? [NSString stringWithUTF8String:cachedSelected] : @"";
        *selectedOut = selected ?: @"";
    }
    return enabled;
}

BOOL DDSiriProbePressEligible(long long buttonIdentifier) {
    if (buttonIdentifier != 6)
        return NO;
    if (DDSiriProbeFileExistsCached("/var/tmp/duodash_siriprobe_off", &DDSiriProbeOffGate))
        return NO;

    NSString *selected = nil;
    BOOL enabled = DDVoiceCommandPreferenceCache(&selected);
    return selected.length > 0 ? enabled : NO;
}

static BOOL DDSiriProbeIdentifierIsValidCString(const char *identifier) {
    if (!identifier || !identifier[0])
        return NO;
    size_t length = strlen(identifier);
    if (length == 0 || length > 96 || identifier[0] == '.' || identifier[length - 1] == '.')
        return NO;

    BOOL sawDot = NO;
    for (size_t index = 0; index < length; index++) {
        unsigned char ch = (unsigned char)identifier[index];
        if (ch == '.') {
            sawDot = YES;
            continue;
        }
        BOOL digit = ch >= '0' && ch <= '9';
        BOOL alpha = (ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z');
        if (ch != '-' && !digit && !alpha)
            return NO;
    }
    return sawDot;
}

BOOL DDSiriProbeShouldSwallow(long long buttonIdentifier) {
    if (DDSiriProbeFileExistsCached("/var/tmp/duodash_siriprobe_off", &DDSiriProbeOffGate))
        return NO;
    if (DDSiriProbePressEligible(buttonIdentifier))
        return YES;
    if (!DDSiriProbeFileExistsCached("/var/tmp/duodash_siriprobe_swallow", &DDSiriProbeSwallowGate))
        return NO;

    NSString *raw = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_siriprobe_swallow_id"
                                              encoding:NSUTF8StringEncoding
                                                 error:nil];
    if (!raw.length)
        return YES;

    NSString *trimmed = [raw stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    return [trimmed longLongValue] == buttonIdentifier;
}

int DDPostVoiceCommandPress(void) {
    NSString *selected = nil;
    (void)DDVoiceCommandPreferenceCache(&selected);
    const char *identifier = [selected UTF8String];
    if (!DDSiriProbeIdentifierIsValidCString(identifier))
        return 0;

    char name[129] = {0};
    size_t length = strlen(identifier);
    if (length + 33 > sizeof(name))
        return 0;

    strlcpy(name, "com.sensetechlab.voicecmd.press.", sizeof(name));
    strlcat(name, identifier, sizeof(name));

    double uptime = [[NSProcessInfo processInfo] systemUptime];
    int token = 0;
    if (notify_register_check(name, &token) == 0) {
        notify_set_state(token, (uint64_t)(uptime * 1000.0));
        notify_cancel(token);
    }
    return notify_post(name);
}

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
