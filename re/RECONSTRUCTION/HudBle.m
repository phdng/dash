// RECONSTRUCTION/HudBle.m — APPROXIMATION synthesis (session-031)
// Sources: F-024 (pairing flow), notify_matrix (ble.action/ble.status.changed),
//   strings (scan machinery, HUD keys, speed prefs, BKS brightness), F-008 (app location bg).
// KHÔNG compile ở đây (không toolchain iOS).
// QUAN TRỌNG: pairing/scan BODIES chưa đọc (chỉ mapping + strings) → UNKNOWN;
//   chỉ flows đã có evidence (F-024/notify rows) là CONFIRMED wiring. Không nâng cấp nhãn.

// ---- Pairing flow (CONFIRMED wiring — F-024 + notify_matrix) ----
// Prefs UI toggle `hud_paired` → Post `com.sensetechlab.ble.action`.
// 80468 (7F14C:114-120): Sync prefs; `hud_paired ? BLEManager.shared pair : unpair`
//   (guard 1647C8).
// 96174 (948C0:148-154): `ble.status.changed` → Sync prefs + async main 96DC8 (BLE→UI refresh).
// Server health + firmware rows hiển thị state (prefs UI: server_health, hud_firmware_version).
static void DDHudPairingChanged(void) {
    // Bodies pair/unpair trong BLEManager chưa đọc → UNKNOWN (ngoài strings scan machinery dưới).
}

// ---- Scan machinery (mapping từ strings — bodies UNKNOWN) ----
static void DDHudScan(void) {
    // Selectors thấy trong strings (puesta, bodies chưa đọc):
    //   _beginScan (0x11cb08), _armScanTimeout (0x11cddf), _cancelScanTimeout (0x11cc69),
    //   _scanTimeoutSource (0x11e660, dispatch source — INFERRED timeout timer),
    //   _isScanning (0x11e014), _peripheral (0x11e4c7),
    //   peripheral:didDiscoverServices: (0x11c806, CBPeripheralDelegate).
    // UI strings: "Scanning for HUD." (0xc80c3 + 17 locales, vd es 0xfa03b),
    //   prefs.status.scanning (0xc3ea0), hud_pairing_status (0xc5df2).
    // Timeout durations + scan parameters + service UUIDs: UNKNOWN (không có trong strings hits).
}

// ---- HUD prefs keys (strings + prefs UI — CONFIRMED tồn tại, consumers UNKNOWN) ----
static void DDHudPrefs(void) {
    // Keys: hud_paired (0xc1fdd), hud_paired_uuid (0xc6289),
    //   hud_paired_uuid_sha256 (0x10faa5), hud_firmware_version (0xc62b8),
    //   hud_orientation (0xc635d), hud_brightness (0xc636d),
    //   hud_pairing_status (0xc5df2), prefs.row.firmware (0xc65e5).
    // SHA256 của UUID gợi ý privacy (không broadcast UUID thô) — HYPOTHESIS intent.
    // Orientation/brightness consumers: UNKNOWN bodies (brightness hooks dưới).
}

// ---- HUD brightness (BKS display hooks — mapping từ strings, bodies UNKNOWN) ----
static void DDHudBrightness(void) {
    // BKSDisplayBrightnessGetCurrent (0xc2df4) + BKSDisplayBrightnessSetCurrent (0xc2e13)
    //   (imports — cross-ref F-013 BKS family: SetScreenBlanked/BacklightFactor đã map).
    // Ai gọi get/set, khi nào (theo hud_brightness? theo ambient?): UNKNOWN.
    // Prefs bundle có brightness_min/max assets (icon brightness) — cross-ref bundle resources.
}

// ---- Speed pipeline: sources + correction + display (strings + F-022/F-008) ----
static void DDSpeedSource(void) {
    // Sources (prefs UI rows): incar.title/row/note.speed_source (0xbfb8d/0xbfc9e/0xbfba6),
    //   prefs.navbubble.row.speed_source (0xc3a90), navbubble_speed_source key (0xc0214),
    //   incar.value.obd2 (0xbfb59) — GPS (phone location) vs OBD2 dongle (car speed over BLE).
    //   DuoDash.app location background mode (F-008) nuôi GPS branch.
    // Correction: incar.title/row/note.speed_correction (0xbfc4e/0xbfc9e/0xbfc6b),
    //   speed_correction key (0xc036c), prefs.navbubble.row.speed_correction (0xc3ab1).
    //   Công thức correction: UNKNOWN (không có trong strings hits).
    // Override/debug: /var/tmp/duodash_ab_simspeed (0xc0049, file VALUE — cross-ref toggle_matrix pattern).
}
static void DDSpeedPublish(void) {
    // NavProvider spec keys (doc string 0xc448b): speedLimit int km/h (omit=none),
    //   currentSpeed int km/h (omit=unknown, present=authoritative, 0=stopped).
    // Notifies: duodash.speedLimit (0xc1820) / truedash.speedLimit (0xc188d) /
    //   speedLimit.relayed (0xc1ba8) / alertSpeedLimit (0xc1c21) / speed=%@ format (0xc1ca8).
    // File: /var/tmp/com.sensetechlab.speed.plist (0xc16f5) — write ở 7F974 submitSpeed (F-022/DataRouter.m).
    // Navbubble display: prefs.navbubble.sec.speed (0xc38e0), status none_selected/producing/
    //   silent/not_found (0xc7502/0xc752e/0xc7569/0xc74c8).
    // Camera alerts dùng speedLimit (cameraType/Distance/Limit trong navprovider spec).
}
