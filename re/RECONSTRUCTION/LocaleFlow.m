// RECONSTRUCTION/LocaleFlow.m — APPROXIMATION synthesis (session-053)
// Source: EVIDENCE/version_device_ainfo.md §A (F-030/B-20/P3-5; 4008/A3558/ACF1C +
//   greps + language flow L1-L14). §B (Q-10 info-schema) ngoài scope — cross-ref License.m.
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: fail-soft mọi nơi (không branch loại OS/device),
//   write→post, read 4-tầng + whitelist + cache, clear-fan-out, dead keys giữ nguyên.

#import "DuoDashShared.h"
// Q-10 info-schema bodies: License.m §DDInfo (cross-ref, không duplicate).
// CF<1946.102 selector branch: Evict.m §3AE50-Bước 5 (branch version duy nhất).
// device_hash (A3558): License.m (UDID-hash đính chính — không duplicate).
// Prefs infra: PrefsResolver.m (SetAppValue/Sync/74C8).

// ---- Version/device: hầu hết NEGATIVE (không branch, fail-soft) ----
static void DDVersionDeviceNotes(void) {
    // 4008(a1..a4) generic "OS>=X.Y.Z?": đường nhanh _availability_version_check khi
    //   đã init (163430!=0); fallback so thủ công với 163410/414/418 (parse từ
    //   SystemVersion.plist ProductVersion qua 4198). Caller duy nhất 46340 (threshold UNKNOWN).
    // iOS floor khai báo 14.0 (external Info.plist). Runtime weak-link + plist fallback.
    // operatingSystemVersion chỉ telemetry (A574C/ios_version, 9EE88/os_version). Không if.
    // hw.machine: sysctl → sanitize [A-Za-z0-9,_-] len<=0x20 → dict model; fail → bỏ key.
    // device_hash rỗng → fail-soft no_device_id/no_blob. bootsessionuuid fail → bỏ boot_id
    //   (CarSleeper state.plist). UIDevice.name rỗng → bỏ qua (BLE packet).
    // ACF1C: announce "role=%s pid=%d stage=installed armed_wall=%.0f boot=%s" khi
    //   168D18&&168D19&&164C88 (callers 4A08/4A80/4C34). Không branch version/device/locale.
    // MinimumOS/systemVersion/AppleLanguages: 0 hit decompile (không đọc).
}

// ---- Language write (L1: 6A4E4:21-24, duy nhất) ----
static void DDWriteLanguage(void /* NSString lang */) {
    // Guard 9B284 whitelist (:19) → SetAppValue(duodash_language) → Sync →
    //   9B314 (clear cache) → post language.changed.
}

// ---- Language read 4-tầng + cache (L2-L4: 9AFB0/9B284/9B314) ----
static NSString *DDReadLanguage(void) {
    // (1) /var/tmp/duodash_lang_force trim (:34-59); (2) prefs duodash_language (:62);
    // (3) legacy carnav_language migrate → ghi lại (:67-86); (4) default en (:90).
    // Validate 9B284 mỗi bước: strcmp off_130E88 step 2 đến 32 → 17 entries
    //   (NỘI DUNG 16 strings còn lại UNKNOWN, chỉ lộ "en").
    // Cache 164C38 + lock 164C58 (:26-33,105-115). 9B314 clear 164C38/40 dưới unfair_lock.
    // Không AppleLanguages. truedash_language: 0 hit decompile — dead/legacy giữ nguyên.
    return @"en"; // APPROXIMATION returns
}

// ---- Observers + fan-out (L5-L11: 6 observers, clear + main-reload) ----
static void DDLanguageObservers(void) {
    // Toàn cục 9B848 → 9B87C()=9B314 (chỉ clear). Settings 948C0:96220 (9B314 + async main 96D70).
    // License 8C41C, NavBubble 8EFE4→91DCC (9B314 + async 91E58), VoiceCmd 920C0→933FC,
    //   TweakMgmt 93A3C→93B3C (9B314 + async 93BC8) — mẫu clear+reload (bodies CN* UNKNOWN).
    // 9B314 fan-out callers: 6A4E4,8EE04,91DCC,91EE0,933FC,9394C,93B3C,948C0,96220,9B87C.
    // 9EE88 dùng NSLocale en_US_POSIX chỉ cho NSDateFormatter — không branch locale user.
}
