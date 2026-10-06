// RECONSTRUCTION/Migration.m — APPROXIMATION synthesis (session-035)
// Sources: F-019/F-020 (session-003), EVIDENCE/4C34_import_defaults.md
//   (§1-§7, từ 4C34.c 1465 dòng + helpers 84F74/85028/84FD8/8509C/85664/85748/
//   85800/8597C/85B14/85C5C/85D30/A3558/A4450/A4558/A50CC).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: once-only guards, thứ tự import→defaults, wipe-then-migrate,
//   4 nhánh license, navapps merge rules, seed-false-only, log formats exact.

#import "DuoDashShared.h"
// License branch bodies: cross-ref RECONSTRUCTION/License.m §DDMigrateLicense
//   (không duplicate ở đây; chi tiết dòng xem EVIDENCE §4).
// CarSleeper/SiriProbe/SBApplication tails 4C34.c:1121-1457: cross-ref
//   RECONSTRUCTION/CarSleeper.m + SiriProbe.m (ngoài scope file này).

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

// ---- §6 Defaults bootstrap (4C34.c:908-1119; F-020) ----
static void DDBootstrapDefaults(void) {
    // Guard stat(defaults.done)!=0 mới chạy (912).
    // existing = (airplay marker || settings keys) ? 1 : (import.done existed) (914-944).
    // existing==1: với 3 keys 85C5C (pane_unload_close_enabled, appbridge_autostart,
    //   disconnect_close_enabled), keys nào CopyValue(AnyHost) nil → seed
    //   CFPreferencesSetValue(key,kCFBooleanFalse,...,CurrentUser,AnyHost) —
    //   LUÔN false (949-1032). sync ok/failed (1040-1048).
    // existing==0 (fresh): không seed (946,1052).
    // Ghi defaults.done: existing → "at=<ms> v=1 result=existing why=<import/airplay/keys:N> "
    //   "pinned=<join missing> kept=<join kept> sync=<ok/failed>"; new → "at=<ms> v=1 result=new";
    //   append "\n" UTF-8 (1054-1114).
}

// ---- §7 TrueDash = rename/fork kế nhiệm một chiều (HYPOTHESIS mạnh, F-019) ----
// 1. Import một chiều True→Duo duy nhất (85800.c). 2. Xóa nguồn sau migrate
//   (SetMultiple nil truedash.settings; xóa blob cũ; xóa off_154238). 3. Layout song sinh
//   đổi prefix (dirs TrueDash vs DuoDash; domains truedash.settings/rescuer vs duodash).
// 4. Rename map + compat keys (hiddenByTrueDash đọc → hiddenByDuoDash ghi;
//   truedash_language dư). 5. License verify chéo product "duodash" cho blob cũ +
//   3 prefix key cùng tồn tại. 6. import.done once-only; defaults coi import.done
//   là tín hiệu existing. Bundle-id TrueDash.app riêng: UNKNOWN.
