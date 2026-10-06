// RECONSTRUCTION/KeyboardHooks.m — APPROXIMATION synthesis (session-029)
// Source: HOOKS.md (UIApp/keyboard/orientation table + swizzle + kbd PoC + AZ section),
//   EVIDENCE/keyinput_relay.md (focus intercept, swizzle bodies, AZ bodies — KHÔNG duplicate,
//   cross-ref KeyinputRelay.m), F-017 (AZ spoof), F-013 (BKS display).
// KHÔNG compile ở đây (không toolchain iOS).
// QUAN TRỌNG: hook mapping (class→selector→hook-fn→orig→guard) là CONFIRMED (HOOKS.md);
//   hook-fn BODIES (bên trong làm gì) là UNKNOWN — chưa đọc (ngoại trừ focus/swizzle/AZ đã có bodies).
//   File này là ledge mapping + guards, KHÔNG phải behavioral bodies. Không nâng cấp nhãn.

// ---- Ctor + guards (HOOKS.md §0 + F-011) ----
// 455D0 (UIApp ctor, once DUODASH_AB_UIAPP_HOOKED): cài toàn bộ hooks dưới khi
//   vào process role5-unlisted (appbridge_uiapp). Bundle-conditional sub-branches
//   (Maps/Waze/duodashkey/RCT checks — xem HOOKS session-002 detail, không duplicate).
// 4C858 (kbd PoC ctor): LẶP LẠI keyboard hooks bên dưới IFF file
//   /var/tmp/duodash_kbpoc_kbd tồn tại (gated file — HOOKS.md kbd PoC).

// ---- Focus hooks (bodies ĐÃ CÓ trong KeyinputRelay.m — cross-ref, không duplicate) ----
// UITextField/TextView becomeFirstResponder → 4B90C intercept (gates + dummy inputView +
//   secure-bypass + seed publish + post begin). resignFirstResponder hooks (đối xứng).
// → Xem KeyinputRelay.m §focus.

// ---- Orientation / geometry spoof hooks (mapping CONFIRMED, bodies UNKNOWN) ----
// Mỗi dòng: Target.selector → hook-fn (orig-slot) [guard]:
//   UIScreen.bounds → 461F4 (off_163F90) [chỉ khi !RCT — INFERRED từ HOOKS note]
//   UIScreen.nativeBounds → 47C3C (off_163FD8) [UNKNOWN body]
//   UIScreen._referenceBounds → 47FE4 (off_164010) [UNKNOWN body]
//   UIWindow.setFrame: → 46340 (off_16398) [UNKNOWN body]
//   UIWindow._setRotatableViewOrientation:duration:force: → 47760 (off_163FB0) [UNKNOWN]
//   UIWindow._rotateWindowToOrientation:... → 4784C (off_163FB8) [UNKNOWN]
//   CPWindow.layoutSubviews → 474E4 (off_163FA0) [CarPlay window]
//   CPTemplateApplicationScene._performActionsForUIScene:... → 4752C (off_163FA8) [UNKNOWN]
//   UIViewController.supportedInterfaceOrientations → 4793C (off_163FC0) [UNKNOWN]
//   UIViewController.__supportedInterfaceOrientations → 47A20 (off_163FC8) [UNKNOWN]
//   UIViewController.presentViewController:animated:completion: → 47B04 (off_163FD0) [!RCT]
//   UIViewController.dismissViewControllerAnimated:completion: → 47E40 (off_163FE0) [!RCT]
//   UIApplication.statusBarOrientation → 47E60 (off_163FE8) [!RCT]
//   UIWindowScene.interfaceOrientation → 47EBC (off_163FF0) [!RCT]
//   UIWindowSceneGeometry.interfaceOrientation → 47F18 (off_163FF8) [!RCT; return ghi byte_164000]
//   UIDevice.orientation → 47F74 (off_164008) [!RCT]
// (Hook-fn addresses từ session-002 subagent mapping — HOOKS.md tóm tắt; bodies chưa đọc → UNKNOWN.
//  RCT = React-Native app (RCTRootView/RCTBridge tồn tại) → hook tối thiểu — cross-ref session-002.)

// ---- Keyboard size hooks (mapping CONFIRMED, bodies UNKNOWN) ----
//   +UIKeyboardImpl.defaultSizeForInterfaceOrientation: → 480F8 (off_164018) [via 9C0F0 class-method]
//   +UIKeyboardImpl.keyboardSizeForInterfaceOrientation: → 481BC (off_164020) [via 9C0F0]
//   +UIKeyboardImpl.sizeForInterfaceOrientation: → 48280 (off_164028) [via 9C0F0]
//   +UIKeyboardImpl.keyboardWidthForScreen:withOrientation: → 48344 (off_164030) [via 9C0F0]
//   -UIKeyboardImpl.defaultSizeForInterfaceOrientation: → 48428 (off_164038) [via 9C044 instance]
//   UIPeripheralHost.getWidthForOrientation: → 484EC (off_164040) [UNKNOWN body]
//   UIKBScreenTraits.keyboardWidth → 485AC (off_164048) [UNKNOWN]
//   UIKBScreenTraits.bounds → 48654 (off_164050) [UNKNOWN]
//   UIKBScreenTraits.keyboardScreenReferenceSize → 486E4 (off_164058) [UNKNOWN]
//   UIKBScreenTraits.setKeyboardWidth: → 4875C (off_164060) [CHỈ khi duodashkey]
//   UIKBScreenTraits.setBounds: → 487BC (off_164068) [CHỈ khi duodashkey]
//   UIKBScreenTraits.setKeyboardScreenReferenceSize: → 4883C (off_164070) [CHỈ khi duodashkey]
//   UIView.didMoveToWindow → 488A4 (off_164078) [log "font normalization" — cross-ref session-002]
//   + 7 hooks động off_12DB98 → ĐÃ RESOLVE F-017 (AZ* spoof, KHÔNG phải keyboard — xem dưới)
//   UIApplication.sendEvent: → 48924 (off_164390) [pane-activity probe + othertap throttle —
//     xem KeyinputRelay.m §dismiss (48924 othertap 0.3s)]
//   +AVExternalDevice.currentCarPlayExternalDevice → 48E70 (off_164398, via 9C0F0)
//     [log "cloak ..." — CarPlay-external-device spoof? body UNKNOWN]
//   NSBundle.localizedStringForKey:value:table: → 48EB8 (off_164408)
//     [CHỈ khi file /tmp/duodash_ab_cptrip tồn tại — body UNKNOWN]

// ---- AZ* spoof (bodies ĐÃ CÓ — F-017, không duplicate) ----
// 12DB98 loop 7 hooks (AZCPConnectionState/AZCPNavigationCoordinator/AZCarPlayManager):
//   body `++counter; if (byte_163ED8&1) return 0 else orig()` — xem KeyinputRelay.m? KHÔNG —
//   xem HOOKS.md AZ section + F-017. (Ghi chú để khỏi nhầm với keyboard hooks.)

// ---- Keyboard-layer swizzle (bodies ĐÃ CÓ trong KeyinputRelay.m — cross-ref) ----
// _UIKeyboardLayerHostView setCenter:/setFrame:/didMoveToWindow (372CC installer + 37398/374C4/375B8)
//   — native-kb suppressor màn ngoài (376DC 3 điều kiện). PSTableCell
//   refreshCellContentsWithSpecifier:→94E9C (prefs UI, 4A80.c:34-39 via 9C190) —
//   body UNKNOWN (ngoài keyinput relay; ghi nhận mapping).

// ---- BKS display hooks (bodies ĐÃ CÓ — F-013, không duplicate) ----
// BKSDisplayServicesSetScreenBlanked → 4DF94 (keepawake) + backlight reader (<0.2 + display_held).
// (Ghi chú để hoàn chỉnh keyboard/display surface.)
