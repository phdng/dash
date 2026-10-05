# FUNCTION: -[CNABSpringBoardObserver onHostRequest:] (0x1FB5C)
_Status: INFERRED (static only, chưa runtime VERIFIED). Session-018, session budget: 1 function._
_Evidence: đọc trực tiếp FULL `decompile/1FB5C.c` (214 dòng, 1 pass) session-018 + cross-ref `EVIDENCE/cnab_observers.md` §1._

## ROLE
NSNotification handler cho `com.sensetechlab.appbridge.host.request` (đăng ký 27E20.c:287 — cross-ref). Single-app host: deactivate→hide+ack(0); spike→showSpike+ack; fast re-present (active && !split && hosted==bid); full-host (dismiss→prepare→frame→hostBundleId→showWithHostView); mọi exit ack via 9424 (gen 0, ZeroRect) trừ LABEL_22 success (log + 7B6D8). Không kill/prefs/file/notify_post/dispatch trực tiếp.

## CALLERS
- NSDistributedNotificationCenter delivery (registration 27E20.c — cross-ref). Header 1FB5C.c:5 `callers: none` (static BL). [INFERRED linkage]

## CALLEES (header 1FB5C.c:6 + body)
- C: `27670` (frame decode :81), `27B08` (frame intersect :122/:155), `369E8` (panel geometry :128/:161), `89D8` (uiapp.state :133), `9424` (acks ×4: :98/:134/:167/:182), `4D0F4` (log :208), `7B6D8` (:200/:205) + runtime + string/rect.
- ObjC: `DDz2.shared` (:86), `DDz1.shared` (:87), DDz2 (active :113/:151, isSplitHosting :115, hostedBundleId :117, hostedOrientation :133, renderSize ×2 :130-132, hostBundleId:renderSize: :163, dismiss :152), DDz1 (hide :91, showSpike :96, prepareShell :153, setAppContentFrame: :126/:159, carPlayUsableBounds :127/:160, present :129, carPlayDisplaySize :162, showWithHostView: :180).
- KHÔNG gọi: `notify_post`, `CFPreferences*`, `kill`, file IO, `dispatch_*`, `spike*`, `218D8/202D0`, `986C/B144`. [OBSERVED bằng vắng mặt]

## THREAD/QUEUE
- Delivery thread, toàn đồng bộ. Không async/dispatch/lock. [OBSERVED]

## INPUTS
- `self`, `a2`, `a3` = NSNotification (retain :65).
- userInfo (:66), nil→empty (:68-69). `bundleIdentifier` (:72, nil→"?" :74-76). `activate` bool (:78-80). Frame via 27670 → v12/v14/v16/v18 doubles (:81-84, mapping exact xem 27670 — UNKNOWN ở body này).
- KHÔNG đọc: bundleIdL/R/C, skipEvict, envOnly, layout, cpui*, carWin*, gen. [OBSERVED vắng mặt]

## OUTPUT
- `void`. Kết quả: globals (gen++), DDz actions, 9424 acks, 7B6D8, 4D0F4 + releases (:209-213). [OBSERVED]

## GLOBAL STATE READS
- `off_162E68` (mode string → 369E8, :128/:161). Không đọc gen/prefs/knobs khác. [OBSERVED]

## GLOBAL STATE WRITES
- `++qword_163980` unconditional mọi request (:85, kể cả deactivate). Không ghi gì khác. [OBSERVED]

## OBJECT STATE READS
- DDz2: active/isSplitHosting/hostedBundleId/hostedOrientation/renderSize. DDz1: (actions, không getters đọc state). [OBSERVED]

## OBJECT STATE WRITES
- Không mutate DDz objects trực tiếp trong body (chỉ actions hide/showSpike/prepareShell/dismiss/showWithHostView/present/setAppContentFrame). [OBSERVED]

## BRANCHES
### B01 — activate (:89-92)
- condition: `activate & 1`.
- false → `[DDz1 hide]` (:91) → LABEL_10 (:92).
- true → tiếp B02.
- evidence: :89-93. Status: OBSERVED.

### B02 — spike (:94-112)
- condition: `bid == "__spike__"`.
- true → `showSpike` → v23 (:96-97); `9424(v23, bid, nil×3, 0, ZeroRect)` (:98-108); `!v23` → LABEL_11 (:109-110) else LABEL_22 (:111).
- false → tiếp B03.
- evidence: :94-112. Status: OBSERVED.

### B03 — fast re-present gate (:113-121, 3-AND)
- condition: `DDz2.active && !isSplitHosting && hostedBundleId==bid`.
- true → fast path (:122-148, xem B04).
- false → fallthrough (:151+).
- evidence: :113-121. Status: OBSERVED.

### B04 — fast path (:122-148)
- `27B08(DDz1, frame)` (:122-125); `setAppContentFrame:` (:126); `carPlayUsableBounds` (:127); `369E8(off_162E68, ...)` (:128); `present` → v37 (:129); `renderSize` ×2 (v39/v40; call thứ hai discard — :130-132); `89D8(bid, 1, hostedOrientation, 0, w, h)` (:133, 6 args exact); `9424(v37, bid, nil×3, 0, ZeroRect)` (:134-144); `!v37` → LABEL_11 (:145-146) else LABEL_22 (:147).
- evidence: :122-148. Status: OBSERVED calls/args; renderSize-double-call intent UNKNOWN.

### B05 — dismiss (:151-152)
- (fallthrough, unconditional): `if (DDz2.active) dismiss`.
- evidence: :151-152. Status: OBSERVED.

### B06 — prepareShell (:153-154)
- condition: `![DDz1 prepareShell]` → LABEL_10.
- evidence: :153-154. Status: OBSERVED.

### B07 — hostBundle nil (:162-165)
- `carPlayDisplaySize` (discard :162); `hostBundleId:renderSize:(bid)` → v52 (:163); `!v52` → LABEL_10 (:164-165).
- evidence: :155-165 (incl. 27B08/setFrame/bounds/369E8 pattern lặp B04). Status: OBSERVED.

### B08 — show result (:180-194)
- `showWithHostView:(v52)` → v53 (:180); release v52 (:181); `9424(v53, bid, nil×3, 0, ZeroRect)` (:182-192); `!v53` → LABEL_11 (:193-194) else fallthrough LABEL_22.
- evidence: :180-194. Status: OBSERVED.

### B09 — LABEL_22 bid length (:196-206)
- condition: `length(bid)`.
- true → v55=bid; v54=[bid] array (:198-199); `7B6D8()` argless (:200); release (:201). (Array built nhưng call argless — arg elision? UNKNOWN, cùng lớp U 2565C/CB08.)
- false → `7B6D8()` (:205).
- evidence: :195-206. Status: OBSERVED code; arg-passing UNKNOWN.

### B10 — LABEL_10 ack-zero (:166-178)
- `9424(0, bid, nil×3, 0, ZeroRect)` — activated=0, gen 0, zero rect. Từ B01/B06/B07. → LABEL_11.
- evidence: :166-178. Status: OBSERVED.

### B11 — LABEL_11 common exit (:207-213)
- `4D0F4("host.request")` (:208) + releases v21/v19/v9/v6/v3. Mọi route (trừ LABEL_22 cũng qua đây? — LABEL_22 :195-206 fallthrough vào LABEL_11 :207. Vâng: cả success cũng log + release. INFERRED flow.)
- evidence: :195-213. Status: OBSERVED.

## CALL TRACE (exact, theo thứ tự)
01. retain a3; userInfo (nil→empty); bid (nil→"?"); activate bool; frame 27670 (:65-84)
02. ++163980 (:85)
03. DDz2.shared + DDz1.shared (:86-87)
04. B01: !activate → hide → LABEL_10 (ack 0) → LABEL_11
05. B02: spike → showSpike → 9424(result) → LABEL_11/22
06. B03: gate 3-AND → B04 fast path (:122-148: 27B08/setFrame/bounds/369E8/present/renderSize×2/89D8/9424 → LABEL_11/22)
07. B05 dismiss (conditional) (:151-152)
08. B06 prepareShell? No → LABEL_10 (ack 0)
09. 27B08/setFrame/bounds/369E8 (lần 2) (:155-161)
10. carPlayDisplaySize (discard) + hostBundleId:renderSize: (:162-163)
11. B07 nil? → LABEL_10 (ack 0)
12. showWithHostView: → 9424(result) → B08 (:180-194)
13. LABEL_22: bid-length? → [bid] array + 7B6D8() (:195-206)
14. LABEL_11: 4D0F4 + releases (:207-213)

## SIDE EFFECTS (records SE-1FB5C-* ở SIDE_EFFECTS.md)
- Globals: 163980++ (luôn).
- DDz actions: hide/showSpike/prepareShell/dismiss/showWithHostView/present/setAppContentFrame (+bounds/displaySize getters).
- IPC: 89D8 uiapp.state (fast path, 6 args); 9424 acks ×4 sites (tất cả gen 0 + ZeroRect + nil cpui).
- Log: 4D0F4 (mọi exit incl. success). 7B6D8 (success, arg UNKNOWN).
- Không CFPrefs/file/kill/dispatch/notify_post.

## ASYNC
- Không dispatch/delay/retry trong body. [OBSERVED]

## TIMING
- Không timing trong body. Thứ tự: parse → gen++ → singletons → branches → ack/log. [OBSERVED]

## FAILURE PATHS
- !activate → hide + ack(0) (không phải lỗi, là deactivate).
- bid rỗng (không spike): rơi qua B02 (必 false? — rỗng != "__spike__" → tiếp B03: active? hosted==rỗng? — INFERRED có thể fast-path nếu hosted rỗng(!), rồi 27B08/setFrame... — behavior rỗng-bid full-path INFERRED cần trace, ghi UNKNOWN chi tiết).
- spike/show/present/host/show false → LABEL_11 (log, không ack thêm — ack đã phát trước check).
- prepareShell/hostBundle false → LABEL_10 (ack 0).
- Mọi fail graceful, không throw/retry.

## REENTRANCY
- Reentrant: gen++ mỗi request; không lock/guard trong body. DDz calls tuần tự. INFERRED.

## STALE-GUARD
- Không có. [OBSERVED vắng mặt]

## NIL/EMPTY CASE
- userInfo nil → empty → bid "?", activate 0 → B01 hide path. Frame 27670(empty-dict) → defaults UNKNOWN (record 27670 nếu cần).
- bid nil → "?" (không phải rỗng!) → B02 false ("?" != spike) → B03 (hosted=="?"? INFERRED hầu như false) → full path với bid "?". INFERRED consequence đáng chú ý: nil-bid KHÁC empty-bid.
- DDz2.shared/DDz1.shared nil? — singleton luôn non-nil (INFERRED pattern; không guard trong body).
- hostedBundleId nil → isEqual:(nil)? — INFERRED false → tiếp fallthrough.

## UNKNOWN (đóng)
- U01: 27670 field mapping + defaults với empty-dict.
- U02: 27B08/369E8 semantics + off_162E68 values.
- U03: 7B6D8 argless-call vs built array (elided? global-state? — cùng lớp CB08/CE5C/D4C4).
- U04: 89D8 6-arg semantics (arg#1=1? arg#3=0? — cross-ref EVIDENCE/cnab_observers.md §8.6 có schema 8 keys, khớp 1 phần).
- U05: renderSize double-call (kết quả 2 bỏ — redundant hay side-effect?).
- U06: bid-rỗng full-path (có fast-path với hosted rỗng?).
- U07: v37 present / v53 show / v23 spike return semantics (0/1 meaning).

## CONFIDENCE
- Parse/branches/calls/order/args: OBSERVED (đọc FULL trực tiếp 214 dòng).
- Nil-consequences/intents/return-semantics: INFERRED/HYPOTHESIS.
- Runtime: UNVERIFIED. Không có gì VERIFIED.

## EVIDENCE
- `Library/.../decompile/1FB5C.c` (214 dòng, đọc FULL trực tiếp session-018).
- Cross-ref: `re/EVIDENCE/cnab_observers.md` §1 (khớp 4 nhánh + acks), `re/EVIDENCE/spawn_teardown_kb.md` (89D8 schema 8 keys — khớp 1 phần với 6 args đây).
