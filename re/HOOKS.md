# HOOKS.md — Hook Mapping (Phase 3, static)

## §0 Init chain (CONFIRMED session-002, thay H-001/H-002)
dyld `__init_offsets` (slice0) = {44C0, 7F010, 842EC, 9460C}. 44C0 dispatch theo role (AC5FC suffixes F-012) qua blocks (memory invoke table): role1→4C34, role2→4A80 (+4760), role3→49A8→4A08→once→163EC, role4→48FC, role5-listed→4838→4888→once→455D0+4CBDC, role6→47C4→once→4C858. Mọi role ctor mở đầu `dispatch_once(165508/146AB8)` = AC7A4 (role-name + `byte_168D19` master + latch memcpy). Lồng tiếp: 4C34:1278→27E20; 27E20:282→4DEB4 (BKS blank hook); 4760→4D0B8 stub.

## Direct MSHook (CONFIRMED, 17 grep hits)
| ID | Site | API | Class | Selector | Hook fn | Orig | Guard |
|---|---|---|---|---|---|---|---|
| H1 | 4A80.c:27 | MSHookMessageEx | PSListController | tableView:didSelectRowAtIndexPath: | sub_94610 | off_164AF8 | byte_164AF2+168D19+NSClassFromString |
| H2 | 4A80.c:28 | MSHookMessageEx | PSListController | viewWillAppear: | sub_948C0 | off_164B00 | như trên |
| H3 | 4A80.c:29 | MSHookMessageEx | PSListController | viewWillDisappear: | sub_94DC4 | off_164B08 | như trên |
| H4 | 4A80.c:31 | MSHookMessageEx | PSListController | dealloc | sub_94E38 | off_164B10 | sel_registerName |
| H5 | 4C34.c:1451 | MSHookMessageEx | SBApplication | _processDidLaunch: | sub_84318 | off_164830 | 168D19+InstanceMethod+RunLoopSource |
| H6 | 4C34.c:1452 | MSHookMessageEx | SBApplication | _noteProcess:didChangeToState: | sub_845B8 | off_164838 | như trên |
| H7 | 27E20.c:262 | MSHookFunction | (RTLD_DEFAULT) | objc_exception_throw | sub_4001C | off_163E30 | !getenv HOST_HOOKED |
| H8 | 4DEB4.c:27 | MSHookFunction | off_164450 UNKNOWN | ? | sub_4DF94 | off_164458 | stat display_held + threshold 0.2 + keepawake_off |
| H9 | 88A80.c:63 | wrapper | SiriActivationService (via 4C34) | 7 selectors (bảng dưới) | 889D0/88BC8/88C98/88D7C/88E2C/88EA0/88F48 | off_164A08-38 | signature check q@ / qd@ / q@d@ / q / @ |
| H10 | 9C044.c:39 | wrapper | generic instance | — | a5 | a6 | class_getInstanceMethod+9BE28, log hook:%s |
| H11 | 9C0F0.c:41 | wrapper | generic class | — | a5 | a6 | class_getClassMethod+9BE28, log hook:+%s |

## SiriActivationService (via H9, CONFIRMED)
activationRequestFromButtonIdentifier:context:→889D0; buttonDown...:timestamp:...→88BC8; buttonUp...:deviceIdentifier:...→88C98; buttonLongPress...→88D7C; prewarmFromButtonIdentifier:→88E2C; handleActivationRequest:→88EA0; activationRequestFromVoiceTriggerWithContext:→88F48. Fallback dlopen SiriActivation.framework.

## SpringBoard scene/host (via sub_4049C — BLOCKED ON ARTIFACTS session-002)
Class+selector CONFIRMED (27E20.c:263-274, 10 entries), hook-fn/orig/types UNKNOWN: decompiler strip X2-X5, call-graph không chứa IMP, export chỉ có 2 asm không gồm 27E20. Cần raw ARM64 disasm 10× `BL sub_4049C`. Chi tiết F-018.

## CarPlay cloak (via 163EC, CONFIRMED)
- CRCarPlayAppPolicyEvaluator effectivePolicyForAppDeclaration:→17EC4 (off_163858)
- CRCarPlayAppDeclaration +declarationForAppProxy:→18318 (off_163860)
- DashBoard +_newApplicationLibrary→1842C; DBApplicationInfo carPlayDeclaration→18490; DB/CARLeafIconDataSource icon:imageWithInfo:→185C8/1875C; DB/SBLeafIcon displayName/displayNameForLocation:→18888/18918
- UIApplication sendEvent:→17204 (pane-touch wake)
- Dock/focus/statusbar (189D0/18A7C): SBHIconManager iconTapped×2; DB/CARAppDock _dockButtonPressed; DB/CARFocus take...; DB/CARRootStatusBar homeButtonUp + workspace:stateDidChange...
- Scene/layout (18C2C): DBSceneUpdate _frame/_safeAreaInsets HOẶC CARDashboard sceneFrame/safeArea HOẶC DBDashboardLayoutEngine
- Publisher (18F48): FBSDisplayLayoutPublisher addElement:→1AFF8 (skip nếu duodash_cpui_noelemguard)
- Monitor (19014): DBProcessMonitor _handleDeath...→1AB8C; DBDashboard processMonitor:didHandle...→1AD44

## UIApp/keyboard/orientation (via 455D0, CONFIRMED)
UITextField/TextView become/resignFirstResponder; UIScreen bounds/nativeBounds/_referenceBounds; UIWindow setFrame:/_setRotatable.../_rotate...; CPWindow layoutSubviews; CPTemplateApplicationScene _performActions...; UIViewController supportedInterfaceOrientations/__supported...; present/dismissViewController; statusBarOrientation/interfaceOrientation (WindowScene/Geometry)/orientation; UIKeyboardImpl ×4 + instance; UIPeripheralHost; UIKBScreenTraits width/bounds/refSize (+setters nếu duodashkey); UIView didMoveToWindow; +7 UNKNOWN loop off_12DB98; UIApplication sendEvent:→48924; AVExternalDevice +currentCarPlayExternalDevice→48E70; NSBundle localizedString... (nếu cptrip flag).

## Prefs + keyboard-layer swizzle (via 9C190)
PSTableCell refreshCellContentsWithSpecifier:→94E9C (4A80.c:34-39); _UIKeyboardLayerHostView setCenter:/setFrame:/didMoveToWindow (372CC.c:20-38).

## kbd PoC (4C858, gated file)
Lặp lại keyboard hooks nếu /var/tmp/duodash_kbpoc_kbd tồn tại.

## AZ* CarPlay-state spoof (via 455D0 loop 12DB98 — CONFIRMED session-002)
AZCPConnectionState carPlayConnected→49870 / carPlayActive→498A0; AZCPNavigationCoordinator isCarPlayConnected→498D0; AZCarPlayManager isCarPlayConnected→49900 / isCarPlaySceneActive→49930 / evaluateIsCarPlayConnected→49960 / evaluateIsCarPlaySceneActive→49990 (origs off_164358-88). Body: `if (byte_163ED8&1) return 0 else orig()`.

## BackBoard display hooks (via 4DEB4 — CONFIRMED session-002)
`BKSDisplayServicesSetScreenBlanked` (dlsym 4DDC0.c:19) → MSHook→4DF94 (gated `keepawake_off` absent); reader `BKSHIDServicesGetBacklightFactor` (4DDC0.c:20) cho threshold 0.2 + `display_held` one-shot `SetScreenBlanked(1)`.

## Prefs-native controllers (dylib-side — CONFIRMED session-002)
`CNLicenseActivationController` (~20 methods: observe/viewDidLoad/cnLicense*) + `CNTweakManagementController` (~12 methods: cnRebuildHeader/cnApplyStrings/cnDone) — đích của `openLicenseActivation:/openTweakManagement:`, push từ PSListController hooks H1-H4.
