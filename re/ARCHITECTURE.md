# ARCHITECTURE.md — Inventory (Phase 1)

## 1. Binaries
| Binary | Size | ID / Version | Arch evidence |
|---|---|---|---|
| `Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib` | 3087248 | DuoDash-STL-1.0, client 1.1.5+b1d14e0 | arm64 (decompile 4016 files/4018 funcs, __TEXT/__DATA_CONST/__DATA/__LINKEDIT) |
| `Applications/DuoDash.app/DuoDash` | 167408 | com.sensetechlab.duodash 1.0/1.0, iOS14+, iPhone, hidden, Portrait, location-bg, 17 locales | 25 funcs, main 0x100004154 |
| `Applications/DuoDashKey.app/DuoDashKey` | 238960 | com.sensetechlab.duodashkey 1.0/1.0, hidden, LandscapeRight, no bg | 255 funcs, main 0x100007C24 |
| `Library/PreferenceBundles/DuoDashPrefs.bundle/DuoDashPrefs` | 169840 | com.sensetechlab.duodash.prefs 1.0.0, Principal DuoDashRootListController | 2 classes (RootList, AppPicker) |

## 2. Injection / Dependencies
- Filter: Bundles springboard/Preferences/CarPlayApp/UIKit (Any) + Executables mediaserverd/kbd. Evidence: DuoDash.plist.
- Linked: libobjc, Foundation, CoreFoundation, UIKit, CoreGraphics, CoreBluetooth, IOKit, CoreTelephony, Security, CydiaSubstrate, libz, libc++, libSystem, QuartzCore. Evidence: strings 0xc48-0x1170.
- Imports key: MSHookFunction/MessageEx, CFPreferences*/CFNotification*, notify_*, objc_*, NS* (FileManager/Bundle/NotificationCenter/PropertyList/JSON/URLSession), CBCentralManager/CBUUID, CTTelephonyNetworkInfo, SecKey*, IOPS/IOService, CoreGraphics/CG*, dispatch_*, dlopen/dlsym.

## 3. Resources / Config
- Prefs spec full: `Library/PreferenceLoader/Preferences/DuoDashPrefs.plist` (30 items, defaults com.sensetechlab.duodash.settings). Subset: `DuoDashPrefs.bundle/Root.plist` (11 items).
- App Support: `Library/Application Support/DuoDash/{DualAppsIcon.png,DualAppsSplash.png,Splash1-3.jpg,navbubble_beep.caf,VoiceHandlers/<bundle>.plist}` (strings).
- Icons: `icon@2x/3x.png`, brightness_min/max, AppIcon60x60.

## 4. Processes / Roles
Role (sub_AC7A4): 1=bridge, 2=prefsrefresh, 3=appbridge_cp, 4=carplay, 5=appbridge_uiapp (default), 6=kbdpoc. Dispatcher sub_44C0. Guards DUODASH_AB_*_HOOKED.

## 5. Component map
```
SpringBoard (27E20 host ctor + 4C34 mega-ctor + 163EC carplay ctor)
 ├─ AppBridge panes (split left/right/third, layout 0-8, ratio/frac, autostart)
 ├─ CarPlay cloak (elig/dock/focus/statusbar/scene/publisher/monitor)
 ├─ Keyboard relay (455D0 UIApp hooks <-> DuoDashKey.app via seed/kb/out plists)
 ├─ SiriProbe (7 SiriActivationService hooks)
 ├─ CarSleeper daemon (bt/cell/airplane notifies + IOPS)
 ├─ License (ECDSA + activate/info/env/healthz)
 └─ Prefs UI (DuoDashPrefs.bundle -> CFPreferences -> Darwin/notify -> hot reload)
DuoDash.app: black launcher (giữ process + location bg)
DuoDashKey.app: transparent 1x1 field keyboard holder
```

## 6. Compatibility
- MinimumOS 14.0, iOS version check via SystemVersion.plist ProductVersion %d.%d.%d (4008.c availability_version_check wrapper).
- `hw.machine` sanitized cho license model. `availability_version_check` import.
- 17 locales (en + zh-Hans/Hant/es/ja/ko/de/fr/pt-BR/ru/ar/it/tr/vi/pl/id/th).
