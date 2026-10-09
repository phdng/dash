// RECONSTRUCTION/Migration.m — executable defaults-bootstrap slice + synthesis notes
// Original synthesis: session-035. Exact Foundation/CoreFoundation defaults phase promoted session-196.
// Import/license/file-migration phases retain unresolved tables/private contracts and are compile-excluded.

#import "DuoDashShared.h"
#import <sys/stat.h>
// License branch bodies: cross-ref RECONSTRUCTION/License.m §DDMigrateLicense
//   (không duplicate ở đây; chi tiết dòng xem EVIDENCE §4).
// CarSleeper/SiriProbe/SBApplication tails 4C34.c:1121-1457: cross-ref
//   RECONSTRUCTION/CarSleeper.m + SiriProbe.m (ngoài scope file này).

#if 0 // Import/license/file-migration synthesis remains non-executable pending unresolved static tables/contracts.
// ---- §1 Guards: import.done / import.running (4C34.c:275-293) ----
static BOOL DDMigrationShouldRun(void) {
    // import.done tồn tại → goto LABEL_162 (4C34.c:908), skip toàn bộ import.
    // mkdir("/var/mobile/Library/DuoDash", 0x1ED=493=rwxr-xr-x).
    // import.running tồn tại → ghi import.done="at=<ms> result=aborted\n";
    //   write-ok → remove import.running; rồi goto LABEL_162.
    //   Write-fail → giữ lock, vẫn goto (lần sau abort tiếp).
    // Helpers: 84FD8()=ms-now, 85028()=write "…\n" UTF-8, 84F74()=exists.
    return YES; // APPROXIMATION returns
}

// ---- §2 Pre-check (4C34.c:295-321) ----
static BOOL DDMigrationPrecheck(void) {
    // Inputs: TrueDash/license.blob (295), TrueDash/license.key (302-306),
    //   8509C(truedash.settings), 8509C(truedash.rescuer) (296-312).
    // Skip nếu blob absent AND key absent AND settings==0 AND rescuer==0 (310-314).
    // Ngược lại viết import.running="at=<ms>"; fail → goto LABEL_162 (317-321).
    return YES; // APPROXIMATION returns
}

// ---- §3 Wipe-then-migrate prefs, 2 hosts (4C34.c:322-385) ----
static void DDMigratePrefs(void) {
    // 85148(srcDomain,dstDomain,counters*) — semantics 4 counters
    //   [copy,renamed,dropped,removed]; mapping arg tại call-site HYPOTHESIS.
    // Rename map qword_164860 (off_154718) + denylist qword_164868 (off_154250),
    //   init 85928 — NỘI DUNG cả hai UNKNOWN (cần raw ARM64/__objc_dictobj decode).
    // Filter: chỉ copy trực tiếp nếu rangeOfString:"truedash" options:1==NSNotFound
    //   (85148.c:132-133). "truedash_language" (strings 1418) giữ lại kiểu này.
    // Sub-loop mỗi host (AnyHost rồi CurrentHost): intersect TrueDash dict với
    //   off_154268 → CFPreferencesSetMultiple(nil, array, "...truedash.settings",
    //   CurrentUser, host)+Synchronize = XÓA keys đã migrate khỏi source (341-379).
    //   Nội dung off_154268 UNKNOWN (__objc_arrayobj 55044).
    // Sanitize helpers: 8597C (giữ NSString length>0), 85B14/85BCC (giữ cặp Str:Str).
}

// ---- §4 License branch (4C34.c:386-906) — cross-ref ----
static void DDMigrateLicenseBranch(void) {
    // Full bodies trong License.m §DDMigrateLicense; tóm contract ở đây:
    // v19-v24 exists flags + old_key present/absent (387-403).
    // deviceId=A3558() rỗng → licence no-device-id/none, goto LABEL_91 (404-415).
    // TrueDash blob → A397C(blob,deviceId,"duodash") valid iff v31==0 (731-764);
    //   pubkey off_1542E0 HYPOTHESIS. Key 3-valued unreadable/absent/readable (766-782).
    // DuoDash blob verify A4450; so iat TrueDash vs DuoDash via 85748;
    //   ưu tiên v46=(DuoDash invalid && TrueDash iat < DuoDash iat) (784-793).
    // A Import (TrueDash valid && !v46): A4558 → imported/failed; key rỗng → none/kept
    //   else A50CC → resealed/failed; licence imported; xóa loạt off_154238 (794-846,
    //   nội dung off_154238 UNKNOWN). B1/B2/C: deleted/none/reseal/kept (850-899).
    // Product 3 thế hệ cùng tồn tại; blob cũ verify dưới product "duodash" (754).
}

// ---- §5 airplay/iconstate/navapps + flags + chốt log (4C34.c:417-727) ----
static void DDMigrateFiles(void) {
    // airplay_backup.plist/airplay_absent: skip nếu Duo đã có; else 85800 copy
    //   True→Duo, một cái ok → undo+="airplay" (419-443).
    // iconstate_backup: copy nếu Duo absent + True present → undo+="iconstate" (445-480).
    // navapps.plist merge (482-685): cả hai phải NSDictionary; hidden union
    //   hiddenByDuoDash ∪ hiddenByTrueDash (fallback hiddenByCarNav), dedup
    //   NSMutableOrderedSet (527-580); hiddenClasses Duo đè True (581-605);
    //   ghi hiddenByDuoDash, remove hiddenByCarNav (606-615);
    //   dashboardModeLastSeen NSNumber: remove nếu cả hai nil/0 else True-ưu-tiên
    //   (616-657); write atomically → undo+="navapps" (671-682).
    // Flags: airplay_msrv_pending→"msrv", airplay_uninstalling→"standdown" via 85800
    //   (686-689); undo=join(",") or "none" (85D30 format-only, 690-693).
    // Chốt log → import.done:
    //   "at=%lld result=ok settings=%lu renamed=%lu dropped=%lu removed=%lu "
    //   "rescuer=%lu licence=%s blob=%s key=%s old_key=%s undo=%@" (698-727);
    //   ok → remove import.running.
}

#endif

BOOL DDMigrateTrueDashFileNamed(NSString *name) {
    NSFileManager *fm = [NSFileManager defaultManager];
    NSString *source = [@"/var/mobile/Library/TrueDash" stringByAppendingPathComponent:name];
    if (![fm fileExistsAtPath:source])
        return NO;

    NSString *destination = [@"/var/mobile/Library/DuoDash" stringByAppendingPathComponent:name];
    [fm removeItemAtPath:destination error:nil];
    return [fm copyItemAtPath:source toPath:destination error:nil];
}

NSArray<NSString *> *DDMigrationUniqueNonemptyStrings(id candidate) {
    if (![candidate isKindOfClass:[NSArray class]])
        return nil;

    NSMutableOrderedSet<NSString *> *ordered = [NSMutableOrderedSet orderedSet];
    for (id item in (NSArray *)candidate) {
        if ([item isKindOfClass:[NSString class]] && [(NSString *)item length])
            [ordered addObject:item];
    }
    return ordered.array;
}

NSDictionary<NSString *, NSString *> *DDMigrationStringDictionary(id candidate) {
    if (![candidate isKindOfClass:[NSDictionary class]])
        return nil;

    NSMutableDictionary<NSString *, NSString *> *result = [NSMutableDictionary dictionary];
    [(NSDictionary *)candidate enumerateKeysAndObjectsUsingBlock:^(id key, id value, BOOL *stop) {
        (void)stop;
        if ([key isKindOfClass:[NSString class]] && [value isKindOfClass:[NSString class]])
            result[key] = value;
    }];
    return result;
}

NSString *DDMigrationJoinOrNone(NSArray<NSString *> *values) {
    return values.count ? [values componentsJoinedByString:@","] : @"none";
}

NSDictionary<NSString *, NSString *> *DDMigrationRenameMap(void) {
    return @{ @"truedash_language": @"duodash_language" };
}

NSSet<NSString *> *DDMigrationDeniedPreferenceKeys(void) {
    return [NSSet setWithArray:@[
        @"license_pending_key",
        @"license_pending_email",
        @"license_endpoint",
        @"duodash_reenable_tweaks",
    ]];
}

NSArray<NSString *> *DDMigrationSourceCleanupKeys(void) {
    return @[
        @"license_pending_key",
        @"license_pending_email",
    ];
}

NSString *DDMigrationDestinationKeyForSourceKey(id sourceKey) {
    if (![sourceKey isKindOfClass:[NSString class]] || ![(NSString *)sourceKey length])
        return nil;

    NSString *key = sourceKey;
    NSString *renamed = DDMigrationRenameMap()[key];
    if (renamed)
        return renamed;
    if ([DDMigrationDeniedPreferenceKeys() containsObject:key])
        return nil;
    if ([key rangeOfString:@"truedash" options:NSCaseInsensitiveSearch].location != NSNotFound)
        return nil;
    return key;
}

static NSDictionary *DDMigrationCopyDomainSnapshot(NSString *domain, CFStringRef host) {
    CFPreferencesSynchronize((__bridge CFStringRef)domain,
                             kCFPreferencesCurrentUser,
                             host);
    CFArrayRef keys = CFPreferencesCopyKeyList((__bridge CFStringRef)domain,
                                               kCFPreferencesCurrentUser,
                                               host);
    if (!keys)
        return @{};

    CFDictionaryRef values = NULL;
    if (CFArrayGetCount(keys)) {
        values = CFPreferencesCopyMultiple(keys,
                                           (__bridge CFStringRef)domain,
                                           kCFPreferencesCurrentUser,
                                           host);
    }
    CFRelease(keys);

    id bridged = CFBridgingRelease(values);
    return [bridged isKindOfClass:[NSDictionary class]] ? bridged : @{};
}

BOOL DDMigratePreferenceDomain(NSString *sourceDomain,
                               NSString *destinationDomain,
                               NSUInteger counters[4] _Nonnull) {
    CFStringRef hosts[] = { kCFPreferencesAnyHost, kCFPreferencesCurrentHost };
    NSDictionary *sourceSnapshots[] = {
        DDMigrationCopyDomainSnapshot(sourceDomain, hosts[0]),
        DDMigrationCopyDomainSnapshot(sourceDomain, hosts[1]),
    };

    NSUInteger totalSourceCount = sourceSnapshots[0].count + sourceSnapshots[1].count;
    if (!totalSourceCount)
        return NO;

    for (NSUInteger hostIndex = 0; hostIndex < 2; hostIndex++) {
        NSDictionary *source = sourceSnapshots[hostIndex];
        NSMutableDictionary *desired = [NSMutableDictionary dictionary];

        for (id rawKey in source) {
            if (![rawKey isKindOfClass:[NSString class]] || ![(NSString *)rawKey length]) {
                counters[2] += 1;
                continue;
            }

            NSString *key = rawKey;
            NSString *renamed = DDMigrationRenameMap()[key];
            if (renamed) {
                desired[renamed] = source[key];
                counters[1] += 1;
                continue;
            }
            if ([DDMigrationDeniedPreferenceKeys() containsObject:key] ||
                [key rangeOfString:@"truedash" options:NSCaseInsensitiveSearch].location != NSNotFound) {
                counters[2] += 1;
                continue;
            }

            desired[key] = source[key];
            counters[0] += 1;
        }

        NSDictionary *destination = DDMigrationCopyDomainSnapshot(destinationDomain, hosts[hostIndex]);
        NSMutableArray *removeKeys = [NSMutableArray array];
        for (id key in destination) {
            if (!desired[key])
                [removeKeys addObject:key];
        }
        counters[3] += removeKeys.count;

        CFPreferencesSetMultiple((__bridge CFDictionaryRef)desired,
                                 (__bridge CFArrayRef)removeKeys,
                                 (__bridge CFStringRef)destinationDomain,
                                 kCFPreferencesCurrentUser,
                                 hosts[hostIndex]);
        CFPreferencesSynchronize((__bridge CFStringRef)destinationDomain,
                                 kCFPreferencesCurrentUser,
                                 hosts[hostIndex]);
    }
    return YES;
}

static BOOL DDMigrationPathExists(NSString *path) {
    return [[NSFileManager defaultManager] fileExistsAtPath:path];
}

static long long DDMigrationNowMilliseconds(void) {
    return (long long)([[NSDate date] timeIntervalSince1970] * 1000.0);
}

static BOOL DDMigrationWriteRecord(NSString *path, NSString *record) {
    NSString *line = [record stringByAppendingString:@"\n"];
    return [line writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:nil];
}

static NSUInteger DDMigrationPreferenceKeyCount(NSString *domain) {
    NSUInteger total = 0;
    CFStringRef hosts[] = { kCFPreferencesAnyHost, kCFPreferencesCurrentHost };
    for (NSUInteger index = 0; index < 2; index++) {
        CFArrayRef keys = CFPreferencesCopyKeyList((__bridge CFStringRef)domain,
                                                   kCFPreferencesCurrentUser,
                                                   hosts[index]);
        if (keys) {
            total += (NSUInteger)CFArrayGetCount(keys);
            CFRelease(keys);
        }
    }
    return total;
}

BOOL DDPrepareTrueDashImportIfNeeded(void) {
    NSString *root = @"/var/mobile/Library/DuoDash";
    NSString *done = [root stringByAppendingPathComponent:@"import.done"];
    NSString *running = [root stringByAppendingPathComponent:@"import.running"];
    NSFileManager *fm = [NSFileManager defaultManager];

    if (DDMigrationPathExists(done))
        return NO;

    mkdir([root fileSystemRepresentation], 0755);

    if (DDMigrationPathExists(running)) {
        NSString *record = [NSString stringWithFormat:@"at=%lld result=aborted",
                            DDMigrationNowMilliseconds()];
        if (DDMigrationWriteRecord(done, record))
            [fm removeItemAtPath:running error:nil];
        return NO;
    }

    BOOL hasLicenseArtifact =
        DDMigrationPathExists(@"/var/mobile/Library/TrueDash/license.blob") ||
        DDMigrationPathExists(@"/var/mobile/Library/TrueDash/license.key");
    if (!hasLicenseArtifact &&
        DDMigrationPreferenceKeyCount(@"com.sensetechlab.truedash.settings") == 0 &&
        DDMigrationPreferenceKeyCount(@"com.sensetechlab.truedash.rescuer") == 0) {
        return NO;
    }

    NSString *record = [NSString stringWithFormat:@"at=%lld", DDMigrationNowMilliseconds()];
    return DDMigrationWriteRecord(running, record);
}

long long DDMigrationIssuedAtIfValid(NSInteger validationStatus, NSDictionary *payload) {
    if (validationStatus != 0)
        return 0;
    id issuedAt = payload[@"iat"];
    if (![issuedAt isKindOfClass:[NSNumber class]])
        return 0;
    return [issuedAt longLongValue];
}

BOOL DDFinalizeTrueDashImportRecord(const NSUInteger settingsCounters[4] _Nonnull,
                                     BOOL settingsMigrated,
                                     const NSUInteger rescuerCounters[4] _Nonnull,
                                     BOOL rescuerMigrated,
                                     NSString *licenceStatus,
                                     NSString *blobStatus,
                                     NSString *keyStatus,
                                     NSString *oldKeyStatus,
                                     NSString *undoStatus) {
    NSUInteger settingsCopied = settingsMigrated ? settingsCounters[0] : 0;
    NSUInteger rescuerCopiedOrRenamed =
        rescuerMigrated ? (rescuerCounters[0] + rescuerCounters[1]) : 0;
    NSString *record = [NSString stringWithFormat:
        @"at=%lld result=ok settings=%lu renamed=%lu dropped=%lu removed=%lu rescuer=%lu licence=%@ blob=%@ key=%@ old_key=%@ undo=%@",
        DDMigrationNowMilliseconds(),
        (unsigned long)settingsCopied,
        (unsigned long)settingsCounters[1],
        (unsigned long)settingsCounters[2],
        (unsigned long)settingsCounters[3],
        (unsigned long)rescuerCopiedOrRenamed,
        licenceStatus,
        blobStatus,
        keyStatus,
        oldKeyStatus,
        undoStatus];

    NSString *done = @"/var/mobile/Library/DuoDash/import.done";
    if (!DDMigrationWriteRecord(done, record))
        return NO;

    [[NSFileManager defaultManager]
        removeItemAtPath:@"/var/mobile/Library/DuoDash/import.running"
                   error:nil];
    return YES;
}

BOOL DDMigrateTrueDashPreferenceDomains(NSUInteger settingsCounters[4] _Nonnull,
                                        NSUInteger rescuerCounters[4] _Nonnull) {
    BOOL migratedSettings = DDMigratePreferenceDomain(@"com.sensetechlab.truedash.settings",
                                                       @"com.sensetechlab.duodash.settings",
                                                       settingsCounters);
    BOOL migratedRescuer = DDMigratePreferenceDomain(@"com.sensetechlab.truedash.rescuer",
                                                      @"com.sensetechlab.duodash.rescuer",
                                                      rescuerCounters);

    CFStringRef hosts[] = { kCFPreferencesAnyHost, kCFPreferencesCurrentHost };
    for (NSUInteger hostIndex = 0; hostIndex < 2; hostIndex++) {
        NSDictionary *source = DDMigrationCopyDomainSnapshot(@"com.sensetechlab.truedash.settings",
                                                              hosts[hostIndex]);
        NSMutableArray<NSString *> *removeKeys = [NSMutableArray array];
        for (NSString *key in DDMigrationSourceCleanupKeys()) {
            if (source[key])
                [removeKeys addObject:key];
        }
        if (removeKeys.count) {
            CFPreferencesSetMultiple(NULL,
                                     (__bridge CFArrayRef)removeKeys,
                                     CFSTR("com.sensetechlab.truedash.settings"),
                                     kCFPreferencesCurrentUser,
                                     hosts[hostIndex]);
            CFPreferencesSynchronize(CFSTR("com.sensetechlab.truedash.settings"),
                                     kCFPreferencesCurrentUser,
                                     hosts[hostIndex]);
        }
    }
    return migratedSettings || migratedRescuer;
}

BOOL DDRunDefaultsBootstrapIfNeeded(void) {
    struct stat st;
    if (stat("/var/mobile/Library/DuoDash/defaults.done", &st) == 0)
        return NO;

    BOOL importExists = (stat("/var/mobile/Library/DuoDash/import.done", &st) == 0);
    BOOL airplayExists = (stat("/var/mobile/Library/DuoDash/airplay_backup.plist", &st) == 0) ||
                         (stat("/var/mobile/Library/DuoDash/airplay_absent", &st) == 0);

    CFIndex keyCount = 0;
    CFStringRef hosts[] = { kCFPreferencesAnyHost, kCFPreferencesCurrentHost };
    for (NSUInteger index = 0; index < 2; index++) {
        CFPreferencesSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                 kCFPreferencesCurrentUser,
                                 hosts[index]);
        CFArrayRef keys = CFPreferencesCopyKeyList((__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                   kCFPreferencesCurrentUser,
                                                   hosts[index]);
        if (keys) {
            keyCount += CFArrayGetCount(keys);
            CFRelease(keys);
        }
    }

    BOOL existing = airplayExists || keyCount > 0 || importExists;
    NSArray<NSString *> *safetyKeys = @[
        @"pane_unload_close_enabled",
        @"appbridge_autostart",
        @"disconnect_close_enabled",
    ];
    NSMutableArray<NSString *> *kept = [NSMutableArray array];
    NSMutableArray<NSString *> *pinned = [NSMutableArray array];
    NSString *syncResult = @"ok";

    if (existing) {
        for (NSString *key in safetyKeys) {
            CFPropertyListRef raw = CFPreferencesCopyValue((__bridge CFStringRef)key,
                                                           (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                           kCFPreferencesCurrentUser,
                                                           kCFPreferencesAnyHost);
            if (raw) {
                [kept addObject:key];
                CFRelease(raw);
            } else {
                [pinned addObject:key];
            }
        }
        for (NSString *key in pinned) {
            CFPreferencesSetValue((__bridge CFStringRef)key,
                                  kCFBooleanFalse,
                                  (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                  kCFPreferencesCurrentUser,
                                  kCFPreferencesAnyHost);
        }
        syncResult = CFPreferencesSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                              kCFPreferencesCurrentUser,
                                              kCFPreferencesAnyHost) ? @"ok" : @"failed";
    }

    mkdir("/var/mobile/Library/DuoDash", 0755);
    long long nowMs = (long long)([[NSDate date] timeIntervalSince1970] * 1000.0);
    NSString *record;
    if (existing) {
        NSMutableArray<NSString *> *reasons = [NSMutableArray array];
        if (importExists)
            [reasons addObject:@"import"];
        if (airplayExists)
            [reasons addObject:@"airplay"];
        if (keyCount)
            [reasons addObject:[NSString stringWithFormat:@"keys:%lu", (unsigned long)keyCount]];
        NSString *why = DDMigrationJoinOrNone(reasons);
        record = [NSString stringWithFormat:
                  @"at=%lld v=1 result=existing why=%@ pinned=%@ kept=%@ sync=%@",
                  nowMs, why, DDMigrationJoinOrNone(pinned), DDMigrationJoinOrNone(kept), syncResult];
    } else {
        record = [NSString stringWithFormat:@"at=%lld v=1 result=new", nowMs];
    }

    NSString *line = [record stringByAppendingString:@"\n"];
    return [line writeToFile:@"/var/mobile/Library/DuoDash/defaults.done"
                  atomically:YES
                    encoding:NSUTF8StringEncoding
                       error:nil];
}

// ---- §7 TrueDash = rename/fork kế nhiệm một chiều (HYPOTHESIS mạnh, F-019) ----
// 1. Import một chiều True→Duo duy nhất (85800.c). 2. Xóa nguồn sau migrate
//   (SetMultiple nil truedash.settings; xóa blob cũ; xóa off_154238). 3. Layout song sinh
//   đổi prefix (dirs TrueDash vs DuoDash; domains truedash.settings/rescuer vs duodash).
// 4. Rename map + compat keys (hiddenByTrueDash đọc → hiddenByDuoDash ghi;
//   truedash_language dư). 5. License verify chéo product "duodash" cho blob cũ +
//   3 prefix key cùng tồn tại. 6. import.done once-only; defaults coi import.done
//   là tín hiệu existing. Bundle-id TrueDash.app riêng: UNKNOWN.
