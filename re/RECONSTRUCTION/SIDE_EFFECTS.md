# SIDE_EFFECTS.md — Side-effect ledger (starter session-012: 2410C; session-013: +2565C)
_Quy ước: mỗi record có ID/FUNCTION/CONDITION/EFFECT/TARGET/DATA/TIMING/THREAD/ORDER/FAILURE/EVIDENCE._
_Trạng thái observation: OBSERVED (static) — chưa VERIFIED (chưa runtime test)._

## SE-2410C-001 — mkdir DuoDash
- FUNCTION: 2410C (refused path, 2410C.c:332)
- CONDITION: nhánh refused (!a2||a3), unconditional trong nhánh
- EFFECT: mkdir
- TARGET: `/var/mobile/Library/DuoDash`
- DATA: mode 0x1ED (493 = rwxr-xr-x, INFERRED decode)
- TIMING: đồng bộ, trước write notice.state
- THREAD: queue 165118 (background; hoặc sync fallback)
- ORDER: trước SE-2410C-002
- FAILURE: mkdir fail → tiếp tục write (không check return — INFERRED từ absence of check; cần re-read :332-358 để chốt)
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.2

## SE-2410C-002 — write notice.state
- FUNCTION: 2410C (refused path, 2410C.c:358-367)
- CONDITION: unconditional trong refused path (sau verdict build :333-356)
- EFFECT: file write (atomically, encoding:4=UTF-8)
- TARGET: `/var/mobile/Library/DuoDash/notice.state`
- DATA: `at=<…> source=host verdict=<…> licence=<…> text=<…>` (format exact từ :333-356 — INFERRED tóm tắt, cần verbatim)
- TIMING: đồng bộ sau mkdir
- THREAD: queue 165118
- ORDER: sau SE-2410C-001, trước SE-2410C-003
- FAILURE: write fail → tiếp tục (không abort — INFERRED)
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.2

## SE-2410C-003 — chmod notice.state
- FUNCTION: 2410C (refused path, 2410C.c:358-367)
- CONDITION: sau write (có thể unconditional)
- EFFECT: chmod
- TARGET: `/var/mobile/Library/DuoDash/notice.state`
- DATA: mode 0x1A4 (420 = rw-r--r--, INFERRED decode)
- TIMING: đồng bộ sau write
- THREAD: queue 165118
- ORDER: sau SE-2410C-002
- FAILURE: UNKNOWN
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.2

## SE-2410C-004 — refused IPC ack
- FUNCTION: 2410C → 97A0 → 8D78 (refused path; 97A0.c:33)
- CONDITION: nhánh refused (mọi sub-branch: geo/license/notice đều qua 97A0 — INFERRED từ :205-215 + :277 + :871)
- EFFECT: NSDistributedNotification post (deliverImmediately)
- TARGET: `com.sensetechlab.appbridge.host.state`, dict {hostRefused:1, refuseReason:<string>}
- DATA: refuseReason ∈ {verdict strings, "no-display", "no-display-postanswer", ...} (liệt kê đầy đủ UNKNOWN)
- TIMING: đồng bộ trong 2410C
- THREAD: queue 165118
- ORDER: sau notice flow (refused-notice path) hoặc ngay (geo path)
- FAILURE: UNKNOWN
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.2/§1.7; EVIDENCE/cnab_observers.md §8.3

## SE-2410C-005 — sync kill evicted bids
- FUNCTION: 2410C → 763E0(v81, "cpui switch (R3)", 0) (2410C.c:806-808; 763E0.c:244-264)
- CONDITION: nhánh evict-delay (v81.count truthy); a3=0 cho phép kill
- EFFECT: process kill (SIGKILL) per pid resolve từ 77244
- TARGET: pids trong v81 (trừ protected/frontmost/unresolvable — 763E0.c:124-208; skip nếu noreap — :92)
- DATA: reason string "cpui switch (R3)" (log)
- TIMING: đồng bộ trong 2410C (evict-delay branch)
- THREAD: queue 165118
- ORDER: sau resolve 77244 (:758-761), trước tombstone/schedule (:809-834)
- FAILURE: resolve null → urgency flag, không abort; kill fail per-pid → tiếp tục (INFERRED)
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.4; EVIDENCE/evict_helpers.md §4 (kill không từ 85B8/7764C)

## SE-2410C-006 — tombstone write
- FUNCTION: 2410C (2410C.c:815-818)
- CONDITION: nhánh evict-delay (sau 2595C map)
- EFFECT: global mutation (Dictionary copy)
- TARGET: `qword_163970` = copy v103 (pid/path/bid dicts cho IPC/kill)
- DATA: merge v103 + dicts cũ có bid∈v59 (trước ghi)
- TIMING: đồng bộ
- THREAD: queue 165118
- ORDER: sau SE-2410C-005, trước schedule 25EDC
- FAILURE: UNKNOWN
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.4
- NOTE: xóa ở 25C4C.c:38-40 (file khác, cross-ref)

## SE-2410C-007 — host.state ack (via 2565C→9424→8D78)
- FUNCTION: 2410C → (direct :850 hoặc continuation) 2565C → 9424 → 8D78 (2565C.c:126-128; 9424.c:90-102)
- CONDITION: 2565C chạy (cả success v11=1 và fail v11=0 đều ack)
- EFFECT: NSDistributedNotification post
- TARGET: `com.sensetechlab.appbridge.host.state`, dict {activated=v11, bundleIdentifier, sbPid, cpuiBid/cpuiRectX/Y/W/H (cond), cpuiMore (cond), cpuiGen (cond), cpuiKilled (cond)}
- DATA: v11 = success flag; gen = 162E60++ (cpuiGen lifecycle — EVIDENCE/cpuigen_trace.md)
- TIMING: đồng bộ (direct) hoặc sau delay-chain (evict)
- THREAD: queue 165118 (direct) hoặc main (continuation)
- ORDER: sau present-commit; trước/độc lập onHosted
- FAILURE: UNKNOWN
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.6/§1.7; EVIDENCE/cnab_observers.md §8.3

## SE-2410C-008 — onHosted callback
- FUNCTION: 2410C → 2565C → onHosted(copy hostedSlotBids) (2565C.c:132-140)
- CONDITION: v11 success (count-match && showLayoutPanes==YES) && onHosted non-null && v10 non-null
- EFFECT: callback invocation (IPC nội bộ SB, không phải notify)
- TARGET: block captures từ 218D8 a5 (host-side continuation)
- DATA: v10 = copy hostedSlotBids
- TIMING: đồng bộ (direct) hoặc sau delay-chain (evict)
- THREAD: queue 165118 hoặc main
- ORDER: sau SE-2410C-007
- FAILURE: fail/null → skip im lặng
- EVIDENCE: EVIDENCE/async_host_2410C.md §1.6

## SE-2410C-009 — global mutations host path (gom)
- FUNCTION: 2410C (:406-407, :427-552, :201-202)
- CONDITION: host path (trừ clear 163978 ở guard)
- EFFECT: global mutations (scalars/arrays/frames/tombstone) — chi tiết ở 2410C.md GLOBAL WRITES
- TARGET: 163978/163A02/163A00/162E90/163B18/163B88/163B28/163B20/163BB8/162E80/162E88/tỉ lệ/flags/1639C8/163A18/163970
- DATA: từ answer struct (clamp/defaults) + computed (v36/v142/v81/tombstone)
- TIMING: đồng bộ theo thứ tự call trace
- THREAD: queue 165118
- ORDER: theo CALL TRACE 2410C.md
- FAILURE: UNKNOWN từng field
- EVIDENCE: RECONSTRUCTION/functions/2410C.md

## SE-2565C-001 — natives/slot globals (success)
- FUNCTION: 2565C (2565C.c:53-74)
- CONDITION: B01 success (count khớp + showLayoutPanes true)
- EFFECT: global mutations (3 CGSize + 2 scalars)
- TARGET: `unk_1639D0[0..2]`, `qword_1639C0`, `dword_1639BC`
- DATA: natives copy/pad-Zero; 1639C0=expected; 1639BC=1639B8
- TIMING: đồng bộ trong body
- THREAD: thread của caller (queue 165118 hoặc main)
- ORDER: sau spike/show, trước 7B6D8
- FAILURE: UNKNOWN
- EVIDENCE: RECONSTRUCTION/functions/2565C.md B01/B02

## SE-2565C-002 — splash teardown (fail)
- FUNCTION: 2565C (2565C.c:85-106)
- CONDITION: B01 fail + `byte_164508==1`
- EFFECT: view teardown + global clears + layout calls
- TARGET: splash root view (removeFromSuperview), 164508/164500/164510, via 52338 + 746C(layout=164518)
- DATA: setGen+1 trước remove; v13 retained root
- TIMING: đồng bộ
- THREAD: thread caller
- ORDER: trong fail branch, trước ack
- FAILURE: v13 uninitialized nếu B05 false? (U01 — cần verify assembly)
- EVIDENCE: RECONSTRUCTION/functions/2565C.md B05/B06

## SE-2565C-003 — cpuiGen increment
- FUNCTION: 2565C (2565C.c:127)
- CONDITION: luôn (cả success lẫn fail)
- EFFECT: global mutation (monotonic counter)
- TARGET: `qword_162E60++` (giá trị cũ vào IPC)
- DATA: —
- TIMING: đồng bộ trước 9424
- THREAD: thread caller
- ORDER: sau fetch cpui (B07), trước 9424
- FAILURE: UNKNOWN (overflow/wrap không xử lý)
- EVIDENCE: EVIDENCE/cpuigen_trace.md (H3); functions/2565C.md

## SE-2565C-004 — host.state ack
- FUNCTION: 2565C → 9424 → 8D78 (2565C.c:128; 9424.c:45-102)
- CONDITION: luôn (dict đầy/vơi theo B08)
- EFFECT: NSDistributedNotification post (deliverImmediately — INFERRED từ 8D78 wrapper)
- TARGET: `com.sensetechlab.appbridge.host.state`, dict {activated, bundleIdentifier, sbPid} + cond {cpuiBid/cpuiRectX/Y/W/H, cpuiMore, cpuiGen, cpuiKilled}
- DATA: v11=success flag; gen=162E60++ (xem SE-2565C-003)
- TIMING: đồng bộ trong body
- THREAD: thread caller
- ORDER: sau fetch + increment, trước 4D0F4/onHosted
- FAILURE: UNKNOWN
- EVIDENCE: functions/2565C.md B08 + CALL TRACE 11a-11f

## SE-2565C-005 — onHosted callback
- FUNCTION: 2565C (2565C.c:132-140)
- CONDITION: v11 && +64 non-null && v10 non-null (3 lớp)
- EFFECT: block invocation (1 arg = copy hostedSlotBids)
- TARGET: onHosted block từ 218D8 a5
- DATA: v10
- TIMING: đồng bộ trong body
- THREAD: thread caller
- ORDER: sau ack + 4D0F4 log
- FAILURE: skip im lặng nếu bất kỳ null
- EVIDENCE: functions/2565C.md B10

## SE-202D0-001 — debounce decrement
- FUNCTION: 202D0 (202D0.c:87-88)
- CONDITION: `dword_162E70>=1`
- EFFECT: global mutation (decrement, không check tiếp trong body)
- TARGET: `dword_162E70`
- DATA: -1
- TIMING: đồng bộ đầu handler
- THREAD: notification delivery thread (INFERRED)
- ORDER: đầu tiên trong body
- FAILURE: UNKNOWN (consumer ở nơi khác)
- EVIDENCE: functions/202D0.md B01

## SE-202D0-002 — frame cache overwrite
- FUNCTION: 202D0 (202D0.c:101-104)
- CONDITION: luôn (mỗi request)
- EFFECT: global mutations (4 doubles, không gen-guard)
- TARGET: `qword_163998/9A0/9A8/9B0`
- DATA: từ 27670(userInfo) (mapping exact UNKNOWN — U02)
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: sau retain, trước keys parse
- FAILURE: UNKNOWN
- EVIDENCE: functions/202D0.md (INPUTS lần 1)

## SE-202D0-003 — gen increment (activate)
- FUNCTION: 202D0 (202D0.c:188)
- CONDITION: activate branch
- EFFECT: global mutation (monotonic ++)
- TARGET: `qword_163980` (v52 = new gen, truyền in-place + delayed block)
- DATA: —
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: trước in-place/host calls
- FAILURE: UNKNOWN
- EVIDENCE: functions/202D0.md B04/B05

## SE-202D0-004 — gen increment (deactivate)
- FUNCTION: 202D0 (202D0.c:259)
- CONDITION: deactivate branch
- EFFECT: global mutation (++)
- TARGET: `qword_163980`
- DATA: —
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: đầu deactivate block
- FAILURE: UNKNOWN
- EVIDENCE: functions/202D0.md B08

## SE-202D0-005 — in-place attempt
- FUNCTION: 202D0 → switchCarPlayUIInPlace:gen: (202D0.c:189-196)
- CONDITION: envOnly=1 (skip khi envOnly=0)
- EFFECT: ObjC call có điều kiện (success → skip host block)
- TARGET: CNABSpringBoardObserver (self), args ([L,R,C] array, gen v52)
- DATA: bids retains v48/v49/v50
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: sau gen++, trước reapdelay read
- FAILURE: return 0 → rơi vào host block (không phải lỗi)
- EVIDENCE: functions/202D0.md B05

## SE-202D0-006 — file read reapdelay
- FUNCTION: 202D0 (202D0.c:198-224)
- CONDITION: host block (activate + (¬envOnly ∨ in-place fail))
- EFFECT: file read + parse + clamp
- TARGET: `/var/tmp/duodash_ab_reapdelay` (UTF-8, trim, double, clamp (0,60] else 0.0)
- DATA: v60 delay giây
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: sau in-place, trước hostSlots
- FAILURE: missing/empty/malformed → 0.0 (dispatch + verify ngay)
- EVIDENCE: functions/202D0.md B06

## SE-202D0-007 — hostSlots call
- FUNCTION: 202D0 → hostSlots:skipEvict:onHosted: (202D0.c:225-238)
- CONDITION: host block
- EFFECT: ObjC call (sync; async boundaries nằm trong 218D8)
- TARGET: self, args (v63=[L,R,C] array, v69=skipEvict bool, v74=279F4-block(delay v60, old-bids copy))
- DATA: v62=copy hostedSlotBids (old)
- TIMING: đồng bộ (218D8 nội bộ dispatch tiếp)
- THREAD: delivery thread
- ORDER: sau reapdelay, trước delayed-verify schedule
- FAILURE: xử lý trong 218D8 (record riêng)
- EVIDENCE: functions/202D0.md B07; functions/218D8.md

## SE-202D0-008 — delayed verify schedule
- FUNCTION: 202D0 (202D0.c:239-246)
- CONDITION: host block (sau hostSlots, unconditional)
- EFFECT: dispatch_after lên main (block 27AC8 gen-guard)
- TARGET: _dispatch_main_q, delay v60*1e9 ns, block captures gen v65=163980
- DATA: —
- TIMING: async after v60s (0 = gần như ngay)
- THREAD: delivery → main
- ORDER: sau hostSlots
- FAILURE: UNKNOWN (dispatch fail?)
- EVIDENCE: functions/202D0.md B07

## SE-202D0-009 — deactivate teardown
- FUNCTION: 202D0 (202D0.c:259-264)
- CONDITION: !activate (incl. nil/missing → 0)
- EFFECT: ObjC calls + log + teardown (conditional dismiss + unconditional hide)
- TARGET: [DDz2 dismiss] (chỉ nếu 23454 file tồn tại); [DDz1 hide] (luôn); 4D0F4("split.deactivate"); 76224(v61)
- DATA: v61 = 4D0F4 return (semantics UNKNOWN — U04)
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: sau gen++
- FAILURE: không error path (không check return)
- EVIDENCE: functions/202D0.md B08

## SE-27E20-001 — tmp migrator (carnav_* → duodash_*)
- FUNCTION: 27E20 (27E20.c:110-196)
- CONDITION: opendir ok + calloc ok + prefix match + cap 256 + snprintf bounds + lstat-missing + rename-ok-or-copy-fallback
- EFFECT: FS scan + rename (hoặc copy thủ công + utimes, unlink nếu lỗi)
- TARGET: /var/tmp (scan); `/var/tmp/<name>` → `/var/tmp/duodash_<name+7>`
- DATA: copy 0x1000-chunks, mode 0666 (INFERRED), utimes giữ atime/mtime (nsec/1000)
- TIMING: đồng bộ, bound 256 entries
- THREAD: caller thread
- ORDER: đầu body, trước 76224
- FAILURE: opendir/calloc null → skip; snprintf>1023 / exists → skip entry; copy-fail → unlink dst
- EVIDENCE: functions/27E20.md B01-B06

## SE-27E20-002 — hooks install (MSHook + 10×4049C)
- FUNCTION: 27E20 (27E20.c:257-274)
- CONDITION: master+latch (B09) + !getenv(HOST_HOOKED) (B10)
- EFFECT: function hook + method hooks (hook-fn/orig 4049C UNKNOWN — F-018) + env set
- TARGET: objc_exception_throw → 4001C (orig off_163E30); 10 SB scene selectors; env DUODASH_AB_HOST_HOOKED=1
- DATA: —
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: sau gate, trước display-once/observers
- FAILURE: dlsym nil → skip MSHook (vẫn 4049C + tiếp tục)
- EVIDENCE: functions/27E20.md B09/B10

## SE-27E20-003 — observers + singletons + pollTick
- FUNCTION: 27E20 (27E20.c:281-311)
- CONDITION: B09 (không once-guard riêng — chạy mỗi lần gọi!)
- EFFECT: once (4DEB4), alloc singletons (release old), observer registrations (887C×4, NSNotification×2), method call
- TARGET: once 164448; 163E28/163A70; notifies uiapp.request/host.request(.split)/cpui.status/CarPlayIsConnectedDidChange/UIScreenDidDisconnect; [163A70 carPlayPollTick]
- DATA: —
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: sau hooks, trước Darwin observers
- FAILURE: UNKNOWN (alloc nil?)
- EVIDENCE: functions/27E20.md B10/B11

## SE-27E20-004 — Darwin observers (3+8+1) + NavData + purge + keyinput init
- FUNCTION: 27E20 (27E20.c:199-225, :312-459)
- CONDITION: dashboard gate (B07) / B09 / keyinput-once (B14)
- EFFECT: observer registrations (Coalesce/Immediate exact) + NavData start + prefs purge (dock_mode nil+Sync) + keyinput purge/reset/post-dismiss
- TARGET: 3 dashboard + 8 settings/keyinput + cproleup notifies; CNABNavData; navbubble_dock_mode key; seed/out plists + card state + keyinput.dismiss post
- DATA: —
- TIMING: đồng bộ (delivery async sau này)
- THREAD: caller thread
- ORDER: xen kẽ observers/alloc (B11-B15)
- FAILURE: UNKNOWN (double-register khi reentry — U07)
- EVIDENCE: functions/27E20.md B07/B12-B15

## SE-27E20-005 — dashboard retire (prefs)
- FUNCTION: 27E20 (27E20.c:226-248)
- CONDITION: !290F4(retired) || retired==0
- EFFECT: CFPreferences writes (2 keys) + Synchronize
- TARGET: dashboard_mode_enabled=False, dashboard_mode_retired=True (CurrentUser/AnyHost)
- DATA: —
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: sau dashboard observers, trước counters/gate
- FAILURE: Sync fail → tiếp tục (không check — INFERRED)
- EVIDENCE: functions/27E20.md B08

## SE-27E20-006 — config-repair + republish
- FUNCTION: 27E20 (27E20.c:460-709)
- CONDITION: B09 (không once riêng)
- EFFECT: file read/parse (record) + knob check + prefs snapshot/compute/write-back + Sync + file write record + mkdir + republish call + bringup call
- TARGET: config_repair.record (read + write `at/result/fixes/sync/last_*` + `\n`); off_154208 keys (via 7E908 writes); DuoDash dir; 74C8(); 7B29C("springboard.bringup")
- DATA: formats verbatim trong record; knob noconfigrepair → skipped-record
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: cuối body
- FAILURE: record missing → "none"; knob → skip; sync ok/failed ghi vào record (không abort)
- EVIDENCE: functions/27E20.md B15

## SE-20010-001 — prune-set reset
- FUNCTION: 20010 (20010.c:71-80)
- CONDITION: stale-fail (!ok && gen+1==counter) + (!set || set-gen != incoming)
- EFFECT: global mutations (new set + lastFailedGen)
- TARGET: `qword_163990` (release old, = new NSMutableSet); `qword_163988` (= incoming gen)
- DATA: —
- TIMING: đồng bộ sau forward, trước prune-check
- THREAD: delivery thread
- ORDER: trong B04
- FAILURE: UNKNOWN
- EVIDENCE: functions/20010.md B04

## SE-20010-002 — prune-once (85B8)
- FUNCTION: 20010 → 85B8 (20010.c:81-85)
- CONDITION: stale-fail + set chưa chứa bid
- EFFECT: call (add + logical evict prefs — body F-036)
- TARGET: set addObject bid; 85B8(bid) → ui[_more] removal + sync + regenerate
- DATA: bid (NSString non-empty, đã guard)
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: sau reset-check
- FAILURE: đã prune → skip im lặng
- EVIDENCE: functions/20010.md B05; F-036 (85B8 prefs-only)

## SE-20010-003 — async handoff block
- FUNCTION: 20010 (20010.c:53-68)
- CONDITION: bid valid (B01) — TRƯỚC và ĐỘC LẬP stale-check
- EFFECT: async có điều kiện (main? direct : dispatch_async main)
- TARGET: block {37924, copy bid, gen, ok} → DDz1 noteCarPlayUIStatus (cross-ref)
- DATA: bid copy, gen ULL, ok bool
- TIMING: đồng bộ build, async invoke nếu không main
- THREAD: delivery → (main?)
- ORDER: sau guard, trước stale-check
- FAILURE: UNKNOWN (block fail?)
- EVIDENCE: functions/20010.md B02

## SE-1FB5C-001 — request counter
- FUNCTION: 1FB5C (1FB5C.c:85)
- CONDITION: luôn (mọi notification, kể cả deactivate)
- EFFECT: global mutation (++)
- TARGET: `qword_163980`
- DATA: —
- TIMING: đồng bộ sau parse, trước singletons
- THREAD: delivery thread
- ORDER: đầu body
- FAILURE: UNKNOWN
- EVIDENCE: functions/1FB5C.md (INPUTS sau)

## SE-1FB5C-002 — deactivate hide + ack-zero
- FUNCTION: 1FB5C (1FB5C.c:89-92 → :166-178)
- CONDITION: !activate (incl. nil/missing → 0)
- EFFECT: ObjC call + IPC ack (via 9424)
- TARGET: [DDz1 hide]; 9424(0, bid, nil×3, 0, ZeroRect) → (không 8D78 trực tiếp trong body)
- DATA: bid ("?" nếu nil)
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: trước LABEL_11 log
- FAILURE: UNKNOWN (hide fail?)
- EVIDENCE: functions/1FB5C.md B01/B10

## SE-1FB5C-003 — spike/show/fast/full DDz actions
- FUNCTION: 1FB5C (1FB5C.c:94-194)
- CONDITION: các sub-branches B02/B03-gate/B05/B06/B07
- EFFECT: ObjC calls (showSpike, dismiss có điều kiện, showWithHostView, present, setAppContentFrame + getters)
- TARGET: DDz1/DDz2 (bodies riêng)
- DATA: bid, frame doubles, hostView v52
- TIMING: đồng bộ tuần tự
- THREAD: delivery thread
- ORDER: theo TRACE 05-12
- FAILURE: false → LABEL_10 (ack 0) / LABEL_11 (log)
- EVIDENCE: functions/1FB5C.md B02-B08

## SE-1FB5C-004 — acks gen-zero (×4 sites)
- FUNCTION: 1FB5C → 9424 (1FB5C.c:98/:134/:167/:182)
- CONDITION: spike / fast / LABEL_10 / show (mọi exit trừ LABEL_11-trực-tiếp? — LABEL_11 không ack riêng; ack đã phát trước)
- EFFECT: IPC gián tiếp (9424 → dict → caller? — 9424 trong body này KHÔNG kèm 8D78 call-site; 9424.c:102 tự post host.state — cross-ref COMPARISON 2565C B08)
- TARGET: host.state dict {activated=result, bid, sbPid, NO cpui keys (nil×3), gen 0, ZeroRect}
- DATA: result ∈ {showSpike, present, 0, show}
- TIMING: đồng bộ tại điểm ack
- THREAD: delivery thread
- ORDER: trước LABEL_11/22 tương ứng
- FAILURE: UNKNOWN
- EVIDENCE: functions/1FB5C.md B02/B04/B08/B10

## SE-1FB5C-005 — success log + 7B6D8
- FUNCTION: 1FB5C (1FB5C.c:195-208)
- CONDITION: LABEL_22 (spike-ok / fast-ok / show-ok)
- EFFECT: ObjC call (arg UNKNOWN — array built nhưng call argless) + log call
- TARGET: 7B6D8(); 4D0F4("host.request")
- DATA: v54=[bid] (built, use UNKNOWN — U03)
- TIMING: đồng bộ cuối
- THREAD: delivery thread
- ORDER: sau ack, trước releases
- FAILURE: UNKNOWN
- EVIDENCE: functions/1FB5C.md B09/B11

## SE-9D64-001 — refused rollback
- FUNCTION: 9D64 (9D64.c:744-774)
- CONDITION: hostRefused==1 (boolValue) + (rollback đầy đủ chỉ nếu 163688==1 && 1635E8==1)
- EFFECT: global mutations (11 stores) + ticker call + notification userInfo read
- TARGET: 1635E8=0; 1635F0=163689; 1634B8/C0/C8←1634D0/D8/E0 (storeStrong); 162DE8←163690; 162DF8←163DF0 (literal, anomaly U02); 1636A0←163698; 1636B0←1636A8; 1636C0←1636B8; 1634E8←1634F0; 1634F8←163500; 163628←1636C8; B144("host refused")
- DATA: refuseReason string-or-"?" (đọc, không persist)
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: đầu refused branch, trước releases/return
- FAILURE: guards false → skip rollback (vẫn return sạch)
- EVIDENCE: functions/9D64.md B00/B15

## SE-9D64-002 — header + base state writes
- FUNCTION: 9D64 (9D64.c:205-214, :337-347, :402-448, :456-458, :502-504)
- CONDITION: normal path (các sub-branches tương ứng)
- EFFECT: global mutations (sbPid, killed-dict, base bid/rect/gen, pending bid, cpui gen marker, sets clear)
- TARGET: 1635E8=0; 1635EC=int-or-0; 163570=copy-or-0; 163528/ymmword_163668/1636E8/163538/1636F0/1636E0/163540; 1637A0; 1635A0/1635A8 (clear/add/set)
- DATA: từ userInfo (sbPid/activated/bid/cpui*) + computed (rects, filtered dicts)
- TIMING: đồng bộ theo call trace
- THREAD: delivery thread
- ORDER: theo TRACE 02-16
- FAILURE: invalid → defaults/skip (B05/B06 guards)
- EVIDENCE: functions/9D64.md B02/B04/B06/B09/B11

## SE-9D64-003 — B768 async notify block
- FUNCTION: 9D64 (9D64.c:230-246)
- CONDITION: activated && bid valid && 1635F0==1
- EFFECT: async block (copy bid) → main-or-direct invoke (body B768: SB visible+dock — record F-032)
- TARGET: main queue (nếu không phải main) với block {B768, copy bid}
- DATA: bid copy
- TIMING: async có điều kiện thread
- THREAD: delivery → (main?)
- ORDER: sau header, trước LABEL_20
- FAILURE: UNKNOWN (block fail?)
- EVIDENCE: functions/9D64.md B03

## SE-9D64-004 — spawn/teardown callees (gom, bodies ở F-032)
- FUNCTION: 9D64 → BBF8/BCDC/BD18/BEE4/BFF4/C2A4/C37C/CB08/D01C/D154/D4C4/CE5C/B9A8 (9D64.c:354-727)
- CONDITION: từng sub-branch (base-rect chain, cpuiMore classify, GC, spawn, !activated)
- EFFECT: invocations (evict/register/launch/wait/teardown/spawn/abort — semantics ở EVIDENCE/spawn_teardown_kb.md, không duplicate)
- TARGET: như callee records
- DATA: bid/gen/rect args exact trong 9D64.md TRACE
- TIMING: đồng bộ trong body (CB08 nội bộ async — record callee)
- THREAD: delivery thread
- ORDER: theo TRACE 10/16
- FAILURE: graceful fallbacks (C2A4-nil→C37C; BE34→BFF4; LABEL_152 skips)
- EVIDENCE: functions/9D64.md B06-B13; EVIDENCE/spawn_teardown_kb.md

## SE-9D64-005 — acks + ticker (986C ×2, B144 ×2)
- FUNCTION: 9D64 (9D64.c:419-422, :608-613, :734, :769)
- CONDITION: already-hosted / is_base_app / epilogue / refused-rollback
- EFFECT: IPC gián tiếp (986C→8D78 cpui.status {gen,bid,ok,why}) + ticker calls (B144 dock-hide, không phải ack)
- TARGET: cpui.status reasons {"already", "is_base_app"}; ticker labels {"host.state", "host refused"}
- DATA: gen v137 (=cpuiGen incoming), bid
- TIMING: đồng bộ
- THREAD: delivery thread
- ORDER: tại điểm ack + epilogue
- FAILURE: UNKNOWN
- EVIDENCE: functions/9D64.md B08/B11/B14/B15; EVIDENCE/cnab_observers.md §8.5

## SE-74C8-001 — clearpanes wipe (9 keys)
- FUNCTION: 74C8 (74C8.c:100-204)
- CONDITION: attributes non-nil && .done parse && mtime > done+0.5
- EFFECT: file write (.done) + CFPreferences 9× nil + Synchronize + file delete (clearpanes)
- TARGET: .done (`"%.3f"` atomic UTF-8); keys split_left/right/third, layout, frac_a/b/frac_layout, carplay_ui/_more (domain duodash.settings CurrentUser/AnyHost); file clearpanes
- DATA: —
- TIMING: đồng bộ đầu body
- THREAD: caller thread
- ORDER: trước sync/refresh
- FAILURE: attrs nil / .done empty→0.5 / gate false → skip (không lỗi)
- EVIDENCE: functions/74C8.md B01-B03 (F-041: 9 keys, đính chính 8)

## SE-74C8-002 — sync + refresh (floor/keypane)
- FUNCTION: 74C8 (74C8.c:207-209)
- CONDITION: luôn (sau clear-phase)
- EFFECT: CFPreferences AppSynchronize + helper calls 7EA4(v8)/8058(v9) (bodies riêng)
- TARGET: domain duodash.settings; globals floor/keypane (trong callees)
- DATA: args v8=sync-return, v9=floor-return (use UNKNOWN — U03)
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: sau clear, trước reads
- FAILURE: UNKNOWN (callee internals)
- EVIDENCE: functions/74C8.md (INPUTS call args)

## SE-74C8-003 — plist publish + resolved post
- FUNCTION: 74C8 (74C8.c:215-419)
- CONDITION: luôn (reads → compute → build → write → post)
- EFFECT: CFPreferences reads (enabled/bridgedApps/autostart/bulk/nav ×2) + file write (plist atomic) + Darwin notify post
- TARGET: `/var/tmp/com.sensetechlab.appbridge.plist` (16 entries: 14 core + nav ×2); `com.sensetechlab.appbridge.resolved`
- DATA: 14 keys exact + derives (enabled=value&&exists; autostart=85CDC; split_enabled hằng YES); nav gates (string-check; bool&&exists)
- TIMING: đồng bộ cuối body
- THREAD: caller thread
- ORDER: sau compute; trước releases
- FAILURE: write fail → vẫn post (INFERRED); reads nil → defaults/skip
- EVIDENCE: functions/74C8.md B04-B11 + TRACE 06-18

## SE-218D8-001 — reset globals full-host
- FUNCTION: 218D8 (218D8.c:359-377)
- CONDITION: full-host route (B04 true)
- EFFECT: global mutations (17 stores: 162ED8/162EDA/163C18/163AF1/162E90/163AF2/162E98/162EA0/163AF3/163AF8/163B00/163B08/163B10/163AF0/163B18/163B20/162E80/162E88/v158/v159)
- TARGET: như trên (values: 256/2/0/0/2/0/-0.5/-0.5/0/0/0/0/fmin-check/0/0/0/50/50/0/0)
- DATA: —
- TIMING: đồng bộ sau geometry, trước knobs
- THREAD: thread caller
- ORDER: trước SE-218D8-002
- FAILURE: UNKNOWN
- EVIDENCE: functions/218D8.md (full-host reset)

## SE-218D8-002 — knob overrides (file reads + global writes)
- FUNCTION: 218D8 (218D8.c:381-550)
- CONDITION: full-host route; nopanepad? hard-defaults : 4 file reads
- EFFECT: file reads (7 knob paths) + global mutations (162EA8/162EB0/162E90/163AF2/163AF8/163B00/163B08/163AF3/163AF1 + locals)
- TARGET: /var/tmp/duodash_ab_{nopanepad,panepad,nopaneround,layout,panefracs,paneratio,noratio}
- DATA: clamps (0,40]/13.0/1..8/"a,b"/1..99 + fallbacks 4.0/73E8/81EC/8154/80D0)
- TIMING: đồng bộ
- THREAD: thread caller
- ORDER: sau reset, trước log/gen/dispatch
- FAILURE: missing/empty/malformed → defaults (không throw)
- EVIDENCE: functions/218D8.md B07-B10

## SE-218D8-003 — geometry log async
- FUNCTION: 218D8 → ABB7C block → queue 1652F0 (218D8.c:553-600)
- CONDITION: 163AC0.w/h>=1 (×2 redundant) && queue tồn tại && ABAEC dedup cả 2 queues miss
- EFFECT: async dispatch (fire-and-forget) + IPC gián tiếp (env telemetry — INFERRED)
- TARGET: queue qword_1652F0, block {ABB7C, format 9-doubles + captures}
- DATA: llround sizes + 163AD0 + v127/v119/v58/v109 + consts 160.0/80.0
- TIMING: dispatch_async, không delay
- THREAD: caller → queue 1652F0
- ORDER: sau knobs, trước gen
- FAILURE: gate false → skip im lặng
- EVIDENCE: functions/218D8.md B11

## SE-218D8-004 — gen pair + dispatch host block
- FUNCTION: 218D8 → A8424 (218D8.c:601-653)
- CONDITION: full-host route (sau log)
- EFFECT: global mutations (163980++/163978=) + async dispatch (block 2410C + captures DDz2/DDz1/onHosted/geometry/skipEvict/splash/"host")
- TARGET: qword_163980/163978; queue via A8424 (165118 hoặc sync fallback)
- DATA: v92=new gen; block v138 (+48 onHosted copy, +168 skipEvict, +169 splash)
- TIMING: dispatch (async/sync theo A8424)
- THREAD: caller → target queue
- ORDER: cuối full-host path (trước releases)
- FAILURE: UNKNOWN (A8424 fail path)
- EVIDENCE: functions/218D8.md (gen + block setup + A8424)

## SE-218D8-005 — reshow posts (89D8 per-slot + 9424 ack)
- FUNCTION: 218D8 (218D8.c:659-706)
- CONDITION: reshow route (B04 false: hosting + !visible + identical + flags ok)
- EFFECT: NSDistributedNotification posts (gián tiếp via 89D8 → uiapp.state; via 9424 → 8D78 host.state) + cpuiGen++
- TARGET: uiapp.state per-slot (89D8 bid,1,orient,1,w,h); host.state dict (9424 v105=162E60++)
- DATA: sizes 163D90 fallback unk_1639D8; cpuiBid/More via 234A0/23AB0
- TIMING: đồng bộ trong body
- THREAD: thread caller
- ORDER: loop 89D8 → 70248 → 234A0/23AB0 → 9424 → touch → 4D0F4
- FAILURE: slot CPUI-flagged trong phạm vi → skip 89D8 (không lỗi)
- EVIDENCE: functions/218D8.md B12/B13

## SE-218D8-006 — refused notices (full-host errors)
- FUNCTION: 218D8 → 97A0 (218D8.c:325,349)
- CONDITION: no-display (empty + !prepareShell) / degenerate (w<1||h<1)
- EFFECT: NSDistributedNotification post (gián tiếp 97A0→8D78 host.state refused)
- TARGET: host.state {hostRefused:1, refuseReason ∈ {"no-display","degenerate-content"}}
- DATA: —
- TIMING: đồng bộ (no-display → goto LABEL_115 return)
- THREAD: thread caller
- ORDER: trong geometry phase
- FAILURE: degenerate fallthrough tiếp tục (INFERRED — U04 218D8)
- EVIDENCE: functions/218D8.md B05/B06
