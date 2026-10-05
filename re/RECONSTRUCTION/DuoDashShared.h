// RECONSTRUCTION/DuoDashShared.h — APPROXIMATION skeleton (session-002)
// Mọi hằng số CONFIRMED static; behavior bodies chưa implement.

#pragma once

// Prefs domain chính (F-004)
#define DD_SETTINGS_DOMAIN @"com.sensetechlab.duodash.settings"
// Cache publish bởi sub_74C8 (F-004)
#define DD_APPBRIDGE_CACHE @"/var/tmp/com.sensetechlab.appbridge.plist"
// License base hardcode (F-006; license_endpoint dead — F-016)
#define DD_LICENSE_BASE @"https://license.sensetechlab.com"
#define DD_CLIENT_VERSION @"1.1.5+b1d14e0"

// Notify names (F-005 + sweep session-002 §4; xem API_MAP.md)
#define DD_N_SETTINGS_CHANGED @"com.sensetechlab.settings.changed"
#define DD_N_APPBRIDGE_RESOLVED @"com.sensetechlab.appbridge.resolved"
#define DD_N_APPBRIDGE_LISTCHANGED @"com.sensetechlab.appbridge.listchanged"
#define DD_N_APPBRIDGE_EXIT @"com.sensetechlab.appbridge.exit"
#define DD_N_CPROLEUP @"com.sensetechlab.appbridge.cproleup"
#define DD_N_CPCONNECT @"com.sensetechlab.appbridge.cpconnect"
#define DD_N_CPDISCONNECT @"com.sensetechlab.appbridge.cpdisconnect"
#define DD_N_KEYINPUT_SEED @"com.sensetechlab.keyinput.seed"

// File toggles: fileExists == feature DISABLED (mẫu duodash_cpui_noelemguard — F-011đ)
// Persistent (F-005)
#define DD_LICENSE_BLOB @"/var/mobile/Library/DuoDash/license.blob"
#define DD_REPORTS_OUTGOING @"/var/mobile/Library/DuoDash/reports/outgoing"
// IPC cache (volatile)
#define DD_KEYINPUT_SEED @"/var/tmp/duodash_keyinput_seed.plist"
#define DD_KEYINPUT_OUT @"/var/tmp/duodash_keyinput_out.plist"
#define DD_KEYINPUT_KB @"/var/tmp/duodash_keyinput_kb.plist"

// Init roles (F-012): 1 SpringBoard / 2 Preferences / 3 CarPlay.app /
// 4 mediaserverd / 6 kbd / else 5 appbridge_uiapp. Master enable byte_168D19
// set bởi AC7A4 qua dispatch_once(165508/146AB8) — F-011.
typedef NS_ENUM(int, DDRole) {
    DDRoleBridge = 1, DDRolePrefsRefresh = 2, DDRoleAppBridgeCP = 3,
    DDRoleCarPlay = 4, DDRoleUIApp = 5, DDRoleKbdPoc = 6,
};

// License verify codes (F-006/B-09): 0 OK,1 empty,2 format,3 no-pubkey,
// 4 kid,5 device-mismatch,6 expired,7 clock-skew,8 v!=1,10 product-mismatch (9 vắng).
