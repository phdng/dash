// RECONSTRUCTION/CrashReporting.m — executable guard/config seam + synthesis notes
// Original synthesis: session-034. Foundation/CoreFoundation-safe slice promoted session-179.
// Exact evidence: 9DE28 preference getter + 9E014 early collection gates/dry-run branch.
// Network packaging/upload, queue mutation, status globals, and notify-trigger execution remain excluded.

#import "DuoDashShared.h"
#import <CommonCrypto/CommonDigest.h>

static NSString * const DDCrashOffPath = @"/var/tmp/duodash_cr_off";
static NSString * const DDCrashCollectingPath = @"/var/mobile/Library/DuoDash/crashreport_collecting";
static NSString * const DDCrashDryRunPath = @"/var/tmp/duodash_cr_dryrun";
static BOOL gDDCrashReportingAdapterReady;

NSString *DDCrashSHA256Hex(NSData *data, NSUInteger prefixLength) {
    unsigned char digest[CC_SHA256_DIGEST_LENGTH];
    CC_SHA256(data.bytes, (CC_LONG)data.length, digest);

    NSMutableString *hex = [NSMutableString stringWithCapacity:CC_SHA256_DIGEST_LENGTH * 2];
    for (NSUInteger index = 0; index < CC_SHA256_DIGEST_LENGTH; index++)
        [hex appendFormat:@"%02x", digest[index]];

    if (prefixLength && hex.length > prefixLength)
        return [hex substringToIndex:prefixLength];
    return hex;
}

NSComparisonResult DDCrashStringLengthDescendingComparator(NSString *left, NSString *right) {
    if (left.length == right.length)
        return [left compare:right];
    return left.length > right.length ? NSOrderedAscending : NSOrderedDescending;
}

NSComparisonResult DDCrashDictionaryDateDescendingComparator(NSDictionary *left, NSDictionary *right) {
    id rightDate = right[@"date"];
    id leftDate = left[@"date"];
    return [rightDate compare:leftDate];
}

NSString *DDCrashNormalizeIdentifier(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *normalized = [[value stringByTrimmingCharactersInSet:whitespace] lowercaseString];
    if (normalized.length < 16 || normalized.length > 64)
        return nil;

    NSCharacterSet *allowed = [NSCharacterSet characterSetWithCharactersInString:@"0123456789abcdef-"];
    if ([normalized rangeOfCharacterFromSet:allowed.invertedSet].location != NSNotFound)
        return nil;
    return normalized;
}

static NSString *DDCrashPreferenceString(NSString *key) {
    CFPreferencesSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                             kCFPreferencesCurrentUser,
                             kCFPreferencesAnyHost);
    CFPropertyListRef raw = CFPreferencesCopyValue((__bridge CFStringRef)key,
                                                   (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                   kCFPreferencesCurrentUser,
                                                   kCFPreferencesAnyHost);
    id value = CFBridgingRelease(raw);
    return [value isKindOfClass:[NSString class]] ? value : nil;
}

void DDCrashReportingAdapterStart(void) {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        gDDCrashReportingAdapterReady = YES;
    });
}

BOOL DDCrashReportingAdapterReady(void) {
    DDCrashReportingAdapterStart();
    return gDDCrashReportingAdapterReady;
}

BOOL DDCrashReportingMayCollect(void) {
    if (!DDCrashReportingAdapterReady())
        return NO;
    NSFileManager *fm = [NSFileManager defaultManager];
    return ![fm fileExistsAtPath:DDCrashOffPath] &&
           ![fm fileExistsAtPath:DDCrashCollectingPath];
}

BOOL DDCrashReportingDryRunEnabled(void) {
    if (!DDCrashReportingAdapterReady())
        return NO;
    return [[NSFileManager defaultManager] fileExistsAtPath:DDCrashDryRunPath];
}

NSString *DDCrashReportingEndpoint(void) {
    if (!DDCrashReportingAdapterReady())
        return nil;
    return DDCrashPreferenceString(@"crashreport_endpoint");
}

NSString *DDCrashReportingToken(void) {
    if (!DDCrashReportingAdapterReady())
        return nil;
    return DDCrashPreferenceString(@"crashreport_token");
}

BOOL DDCrashReportingShouldPrepareUpload(void) {
    // 9E014 checks dry-run before endpoint length. Both prevent request preparation.
    if (!DDCrashReportingAdapterReady() || DDCrashReportingDryRunEnabled())
        return NO;
    return DDCrashReportingEndpoint().length > 0;
}

NSString *DDCrashReportingReportsURLString(void) {
    NSString *endpoint = DDCrashReportingEndpoint();
    if (!endpoint.length)
        return nil;

    // Exact 9E014 normalization: trim only '/' from both ends, then append /v1/reports.
    NSCharacterSet *slashes = [NSCharacterSet characterSetWithCharactersInString:@"/"];
    NSString *trimmed = [endpoint stringByTrimmingCharactersInSet:slashes];
    return [trimmed stringByAppendingString:@"/v1/reports"];
}

NSString *DDCrashReportingAuthorizationValue(void) {
    NSString *token = DDCrashReportingToken();
    if (!token.length)
        return nil;
    return [@"Bearer " stringByAppendingString:token];
}

NSString *DDCrashReportingRecoveryStatusSuggestion(void) {
    if (!DDCrashReportingAdapterReady())
        return nil;

    NSFileManager *fm = [NSFileManager defaultManager];
    if ([fm fileExistsAtPath:DDCrashCollectingPath])
        return @"Disabled — last report crashed";

    NSString *status = DDCrashPreferenceString(@"crashreport_status");
    if ([status hasPrefix:@"Uploading"] ||
        [status isEqualToString:@"Collecting…"] ||
        [status isEqualToString:@"Packaging…"] ||
        [status isEqualToString:@"Already sending"]) {
        return @"Idle";
    }
    return nil;
}

NSUInteger DDCrashReportingPruneOutgoingQueue(void) {
    if (!DDCrashReportingAdapterReady())
        return 0;

    NSFileManager *fm = [NSFileManager defaultManager];
    NSArray<NSString *> *names = [fm contentsOfDirectoryAtPath:DD_REPORTS_OUTGOING error:nil];
    if (names.count < 4)
        return 0;

    NSMutableArray<NSDictionary *> *entries = [NSMutableArray arrayWithCapacity:names.count];
    for (NSString *name in names) {
        NSString *path = [DD_REPORTS_OUTGOING stringByAppendingPathComponent:name];
        NSDictionary *attrs = [fm attributesOfItemAtPath:path error:nil];
        NSDate *date = attrs.fileModificationDate ?: [NSDate distantPast];
        [entries addObject:@{ @"p": path, @"d": date }];
    }

    // Exact A1CAC comparator: compare a3[@"d"] against a2[@"d"], newest first.
    [entries sortUsingComparator:^NSComparisonResult(NSDictionary *a, NSDictionary *b) {
        return [b[@"d"] compare:a[@"d"]];
    }];

    NSUInteger removed = 0;
    for (NSUInteger index = 3; index < entries.count; index++) {
        NSString *path = entries[index][@"p"];
        if ([fm removeItemAtPath:path error:nil])
            removed++;
    }
    return removed;
}
// Records: F-016 (session-002), B-08. Prefs UI: group/row/button/status (strings
//   0xc7c4c/0xc7cf7/0xc5dcc/cr_collecting/cr_disabled). Manual trigger:
//   prefs button → Darwin com.sensetechlab.crashreport.send (poster 948C0? —
//   INFERRED từ notify_matrix poster column; exact poster file UNKNOWN — dùng notify name).

// ---- Trigger + re-entrancy (notify_matrix: 7F14C.c:136-142) ----
static void DDCrashReportSend(void) {
    // 80C04 (DeliverImmediately): spinlock byte_1650B0 — busy → 9DEEC("Already sending"),
    //   return (không queue thêm).
    //   free → async queue 9DFD4 (block 146158) → collect+upload dưới (9E014).
    // (Spinlock type/op exact UNKNOWN — cross-ref notify_matrix row.)
}

// ---- Guards: collecting + kill-switch (B-08, F-016) ----
static BOOL DDCrashMayCollect(void) {
    // Guard 1 — re-entrancy file: /var/mobile/Library/DuoDash/crashreport_collecting
    //   tồn tại → 9DEEC("Disabled - last report crashed") + return NO.
    //   (Tạo file khi bắt đầu collect, unlink khi xong/fail — INFERRED lifecycle.)
    // Guard 2 — kill-switch file: /var/tmp/duodash_cr_off tồn tại → disabled + return NO.
    // latch.reset pipeline unlink collecting + 9DEEC(Idle) + Post(respring.request)
    //   (notify_matrix latch.reset row — cross-ref F-023).
    return YES; // APPROXIMATION returns
}

// ---- Collect: 9EE88 → bundle.tar.gz + meta.json (B-08) ----
static void DDCollectCrashReport(void) {
    // 9DEEC("Collecting…") status (strings 0xc80d7; prefs row crashreport_status).
    // 9EE88(...): thu thập artifacts → bundle.tar.gz + meta.json vào
    //   /var/mobile/Library/DuoDash/reports/outgoing (+ timestamped subdir? — UNKNOWN layout exact).
    // Queue cap: giữ tối đa 3 (xóa từ index 3, sort mtime — F-016).
    // (9EE88 fields/meta schema: chưa tách record — cross-ref B-08 "meta.json"; UNKNOWN chi tiết.)
}

// ---- Endpoint resolve: 9DE28 getter (F-016: 9DE28.c:18-35) ----
static NSString *DDCrashEndpoint(void) {
    // Compile-safe wrapper over the exact 9DE28-compatible getter above.
    return DDCrashReportingEndpoint();
}

// ---- Upload: multipart POST (F-016: 9E014.c:228-231+) ----
static void DDUploadCrashReport(void) {
    NSString *ep = DDCrashEndpoint();
    if (!ep.length) {
        // 9DEEC("Saved on device (no server configured)") — KHÔNG network. (F-016)
        return;
    }
    // dryrun: /var/tmp/duodash_cr_dryrun tồn tại → local-only (không upload).
    // POST <endpoint.trim('/')/v1/reports>, multipart/form-data
    //   (meta.json + bundle.tar.gz), timeout 60s,
    //   headers: X-DuoDash-Protocol / Idempotency-Key / optional Bearer token.
    // Semaphore 300s chờ completion (300000000000ns — INFERRED từ F-016 "semaphore 300s").
    // Progress/timer/cleanup bodies: UNKNOWN (chưa đọc 9E014 FULL — chỉ F-016 summary).
}

// ---- Statuses (strings — UI mapping, bodies UNKNOWN) ----
// "Collecting…" (0xc80d7), "Saved on device" (0xc4286),
// "Saved on device (no server configured)" (0xc42ac),
// "Disabled - last report crashed" (0xc80f2), cr_collecting/cr_disabled keys,
// "Disabled after repeated crashes: %@" (0xc8c51, latch-disabled context — F-023 cross-ref).
// Prefs rows hiển thị state qua 9DEEC(...) — call sites rải rác (chưa liệt kê hết — UNKNOWN).
