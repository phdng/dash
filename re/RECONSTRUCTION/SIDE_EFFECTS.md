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

## SE-163EC-001 — observer + sendEvent hook
- FUNCTION: 163EC (163EC.c:131-144)
- CONDITION: master enable (B01)
- EFFECT: alloc singleton + method hook (orig off_1637E0)
- TARGET: 1635F8=new CNABCarPlayObserver (release old); UIApplication.sendEvent:→17204 (Class = instance-or-getClass)
- DATA: log-tag "CarPlay sendEvent: (pane-touch wake)"
- TIMING: đồng bộ
- THREAD: caller thread (từ 4A08 once — INFERRED)
- ORDER: sau counters, trước Darwin observers
- FAILURE: sharedApplication nil → getClass fallback (vẫn hook)
- EVIDENCE: functions/163EC.md B02 + HOOKS.md CarPlay cloak

## SE-163EC-002 — observers (Darwin ×3 + notifyd ×2) + plist load
- FUNCTION: 163EC (163EC.c:145-180)
- CONDITION: master enable
- EFFECT: observer registrations + resolved-plist load
- TARGET: listchanged/resolved→17344 + exit→173FC (Immediate, &unk_163608); cpdisconnect/cpconnect blocks (main, tokens); 17410() load
- DATA: —
- TIMING: đồng bộ (delivery async sau này)
- THREAD: caller thread
- ORDER: sau hooks, trước elig install
- FAILURE: UNKNOWN (re-register khi reentry — U08)
- EVIDENCE: functions/163EC.md B03/B04 + notify_matrix

## SE-163EC-003 — elig hooks install
- FUNCTION: 163EC (163EC.c:181-298)
- CONDITION: !getenv(ELIG_HOOKED) + classes tồn tại (nested v8/v9)
- EFFECT: 8 method hooks + env set + capability probe store
- TARGET: policy/declaration/library/carPlayDeclaration/icon×2/displayName×2 (origs 163858-163890); env=1; 162E08=probe
- DATA: log-tags "elig ..." per-hook; DB→CAR fallbacks; struct-magic gate (icon variant 2)
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: sau load, trước chain
- FAILURE: env set → skip lần sau; classes nil → fallbacks/skips (một số calls unguarded — U03)
- EVIDENCE: functions/163EC.md B05-B07; EVIDENCE/elig_cloak.md (bodies); CarPlayCloak.m

## SE-163EC-004 — chain + delayed triggers
- FUNCTION: 163EC (163EC.c:299-308)
- CONDITION: master enable (ngoài elig-if)
- EFFECT: chained installer calls + one-shot dispatches
- TARGET: 189D0→18A7C→18C2C→18F48→19014→1910C (threaded returns); after-5s block; 191A4()
- DATA: —
- TIMING: sync chain + async 5s one-shot (main)
- THREAD: caller → main (async parts)
- ORDER: sau elig
- FAILURE: UNKNOWN (chain semantics U04)
- EVIDENCE: functions/163EC.md B08/B09

## SE-163EC-005 — one-shot file triggers
- FUNCTION: 163EC (163EC.c:309-501)
- CONDITION: file exists (spike/host-nonempty/hostsplit-nonempty/splitstart) + clamps
- EFFECT: file consume (removeItem) + reads + scheduled blocks (one-shots)
- TARGET: ab_spike (4s+19s); ab_host (+hold clamp [10,3600]→900s, blocks 191D4/19210); ab_hostsplit (tokens≥2, 4s + hold, blocks 1925C/192C0); ab_splitstart (5s)
- DATA: bid strings retains; hold doubles
- TIMING: async one-shots main (4s/5s/19s/hold-computed)
- THREAD: caller → main
- ORDER: sau chain, trước cproleup
- FAILURE: missing/empty/malformed → skip/clamp/defaults
- EVIDENCE: functions/163EC.md B10

## SE-163EC-006 — cproleup + cpuicaps
- FUNCTION: 163EC (163EC.c:502-528)
- CONDITION: luôn (post) + probe-gate (set/post)
- EFFECT: notify post + conditional notify set/post + token register
- TARGET: cproleup post; cpuicaps: set_state(token, caps) + post (skip nếu register fail)
- DATA: caps = (F3E0-non-nil | rootVC-responds) & icon-hook-installed; token 162E58 (-1 khi fail)
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: cuối body
- FAILURE: register fail → skip post (vẫn releases)
- EVIDENCE: functions/163EC.md B11

## SE-44C0-001 — role dispatches + 4760 calls
- FUNCTION: 44C0 (44C0.c:29-123)
- CONDITION: role = AC5FC() (1..6; default silent)
- EFFECT: async dispatches (main: roles 1/2/5-unlisted/6; global-QOS17: roles 3/4) + sync 4760() calls (roles 2 + 5-unlisted) + pool push/pop (role5)
- TARGET: blocks 12CBD8/12CBF8/12CC18/12CC58/12CC78/12CC98 (→4C34/4A80/49A8/48FC/4838/47C4 — F-011)
- DATA: role5 bundle-path/bid gates (siri-exclusion + blocklist-scan → unlisted-only dispatch)
- TIMING: dispatches fire-and-forget (không delay)
- THREAD: dyld init thread → main/global queues
- ORDER: role? → (4760?) → dispatch
- FAILURE: role 0 (fail-cache) → silent; bundle-path false / siri / listed → silent return (đã releases)
- EVIDENCE: functions/44C0.md B01-B07 + TRACE

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

## SE-CRASH-001 — collecting-file guard (re-entrancy)
- FUNCTION: crashreport.send → 80C04 → DDCrashMayCollect (notify_matrix 7F14C.c:136-142; CrashReporting.m)
- CONDITION: `/var/mobile/Library/DuoDash/crashreport_collecting` tồn tại (tạo khi bắt đầu collect, unlink khi xong/fail — INFERRED lifecycle)
- EFFECT: skip collect + status "Disabled - last report crashed" (9DEEC → prefs row crashreport_status)
- TARGET: (không ghi file mới) + status UI
- DATA: —
- TIMING: đồng bộ trước collect
- THREAD: 80C04 spinlock byte_1650B0 (busy → "Already sending", không queue thêm) rồi async queue 9DFD4
- ORDER: trước SE-CRASH-002/003
- FAILURE: N/A (guard pure-check)
- EVIDENCE: RECONSTRUCTION/CrashReporting.m (B-08/F-016 synthesis)

## SE-CRASH-002 — cr_off kill-switch
- FUNCTION: DDCrashMayCollect (CrashReporting.m)
- CONDITION: `/var/tmp/duodash_cr_off` tồn tại
- EFFECT: disabled, return NO (không collect/upload)
- TARGET: —
- DATA: —
- TIMING: đồng bộ sau SE-CRASH-001
- THREAD: caller thread (trong 80C04 async block)
- ORDER: sau SE-CRASH-001, trước SE-CRASH-003
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/CrashReporting.m (F-016 toggle row 9E014:104)

## SE-CRASH-003 — collect + queue cap 3
- FUNCTION: DDCollectCrashReport ← 9EE88 (CrashReporting.m; B-08)
- CONDITION: guards pass (SE-CRASH-001/002)
- EFFECT: file writes (artifacts) + prune queue
- TARGET: `/var/mobile/Library/DuoDash/reports/outgoing` (bundle.tar.gz + meta.json; subdir layout UNKNOWN)
- DATA: status "Collecting…" (9DEEC); giữ tối đa 3 (xóa từ index 3, sort mtime — F-016)
- TIMING: đồng bộ trong async block
- THREAD: queue 9DFD4 (block 146158)
- ORDER: sau guards, trước SE-CRASH-004/005
- FAILURE: collect-fail → giữ collecting file? (lifecycle INFERRED — CrashReporting.m)
- EVIDENCE: RECONSTRUCTION/CrashReporting.m (9EE88 meta schema UNKNOWN)

## SE-CRASH-004 — endpoint-nil default (no network)
- FUNCTION: DDCrashEndpoint ← 9DE28 getter (9DE28.c:18-35; CrashReporting.m)
- CONDITION: CFPreferences `crashreport_endpoint` không phải NSString (nil default — KHÔNG literal)
- EFFECT: skip upload + status "Saved on device (no server configured)"
- TARGET: (local-only, giữ bundle trên máy)
- DATA: token optional `crashreport_token` (Bearer, nếu có)
- TIMING: sau collect
- THREAD: caller thread
- ORDER: sau SE-CRASH-003, thay SE-CRASH-005 khi nil
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/CrashReporting.m (F-016)

## SE-CRASH-005 — upload multipart + semaphore + dryrun
- FUNCTION: DDUploadCrashReport ← 9E014 (9E014.c:228-231+; CrashReporting.m)
- CONDITION: endpoint non-empty
- EFFECT: network POST + semaphore wait
- TARGET: `<endpoint.trim('/')/v1/reports>` multipart/form-data (meta.json + bundle.tar.gz), timeout 60s; headers X-DuoDash-Protocol / Idempotency-Key / optional Bearer
- DATA: semaphore 300s (300000000000ns — INFERRED); dryrun `/var/tmp/duodash_cr_dryrun` tồn tại → local-only, không upload
- TIMING: đồng bộ chờ completion (tối đa 300s)
- THREAD: caller thread (block semaphore)
- ORDER: sau SE-CRASH-004 (endpoint-pass)
- FAILURE: timeout/completion-fail → progress/timer/cleanup bodies UNKNOWN (chưa đọc 9E014 FULL)
- EVIDENCE: RECONSTRUCTION/CrashReporting.m (F-016; F-023 latch cross-ref)

## SE-RESPRING-001 — latch.reset wipe + post request
- FUNCTION: latch.reset → 80574 (7F14C.c:121-127; Respring.m)
- CONDITION: `duodash_reenable_tweaks` tồn tại/khác-false (đọc flag exact UNKNOWN)
- EFFECT: file unlinks + status + Darwin post
- TARGET: `/var/mobile/Library/DuoDash/*.plist` (glob list exact UNKNOWN) + flag=false (which UNKNOWN) + unlink crashreport_collecting + 9DEEC("Idle") + Post `com.sensetechlab.respring.request`
- DATA: —
- TIMING: đồng bộ trong handler (Immediate)
- THREAD: notify thread (Immediate delivery)
- ORDER: đầu chain latch→respring (kích SE-RESPRING-002)
- FAILURE: guard fail → no-op (không wipe, không post)
- EVIDENCE: RECONSTRUCTION/Respring.m (F-023/B-14)

## SE-RESPRING-002 — respring.request guards + delayed execute
- FUNCTION: respring.request → 8097C (7F14C.c:129-135; Respring.m)
- CONDITION (thứ tự): duodash_norespring/duodash_ab_norespring vắng (stat!=0 → return) → respring_last throttle 8/60s (touch khi pass; path exact UNKNOWN) → latch carsleep off (9C530) → 9C790 pass (điều kiện UNKNOWN)
- EFFECT: Darwin post + delayed respring execute
- TARGET: Post `com.sensetechlab.respring.ack` (→ SE-RESPRING-003) + dispatch_after 21.6s block 12FC70 + thực hiện (811B0/81624 HOẶC async 812F4/81304/81344 — mapping UNKNOWN) + `respring_soft`/`no_msrv_restart` sub-paths (UNKNOWN exact)
- DATA: —
- TIMING: post đồng bộ; execute sau 21.6s
- THREAD: notify thread + delayed block
- ORDER: sau SE-RESPRING-001 (hoặc trigger trực tiếp), trước SE-RESPRING-003
- FAILURE: guard fail → return silent/throttled (branch/thông báo exact UNKNOWN)
- EVIDENCE: RECONSTRUCTION/Respring.m (F-023 + toggle_matrix §B)

## SE-RESPRING-003 — respring.ack flag
- FUNCTION: respring.ack → 96D60 (96D2C.c:14-20; Respring.m)
- CONDITION: ack notify received (observer unk_164B58)
- EFFECT: global write (ack flag)
- TARGET: byte_164B4E=1
- DATA: —
- TIMING: đồng bộ
- THREAD: notify thread
- ORDER: sau SE-RESPRING-002
- FAILURE: N/A (không post tiếp, không prefs-write)
- EVIDENCE: RECONSTRUCTION/Respring.m (notify_matrix row)

## SE-POLL-001 — poll tick transitions + retry labels
- FUNCTION: carPlayPollTick → 22AD0 (22AD0.c:26-109; PollFlush.m)
- CONDITION: self-rescheduling tick mỗi 3s (22D5C); truth = DDz1.carPlayConnected
- EFFECT: atomics + notify post + retry-label probe + flush dispatch
- TARGET: byte_1652B0/qword_1652B8 (atomics); prev!=1&&now==1 → post cpconnect (Darwin) + 163A68=5; labels poll.retry/connect/bringup "%@#%d" 6-163A68 → 365D4(label,1) (0 → =0 else --); 163C40>0 → 371AC (main) else async; v3==1 → 370F8 (main) else async; chốt 162E74=v3 + after 3s re-arm
- DATA: prev!=1&&now==0 → disconnect "poll"; reconnect → 7BCBC log (cnab evidence)
- TIMING: đồng bộ trong tick + after 3s self-reschedule
- THREAD: poll thread + main/async flushes
- ORDER: atomics → transition → labels/probe → flushes → chốt + re-arm
- FAILURE: 365D4 bodies UNKNOWN (cross-ref PollFlush.m); 12D548/12D4F8 async bodies UNKNOWN
- EVIDENCE: RECONSTRUCTION/PollFlush.m (spawn_teardown §C; cnab_observers §5)

## SE-POLL-002 — display probe persist + notify
- FUNCTION: 365D4(label,force) (365D4.c:9; PollFlush.m; caller thứ hai 218D8:552 "panel.host")
- CONDITION: Display 34250() non-nil + w,h>=1 (else return 0)
- EFFECT: prefs writes + Darwin post (chỉ khi force || đổi)
- TARGET: SetAppValue(headunit_resolution/video_quality) + Sync + Post ble.status.changed; lưu 163AC0=w/h, 163AD0=scale; format "%.0f × %.0f", bucket 480p/720p/1080p; return h>0
- DATA: clamp xmmword_163AA8>=40; FBSDisplayConfiguration CONFIRMED theo string
- TIMING: đồng bộ trong poll tick (163A68 loop) hoặc 218D8 geometry phase
- THREAD: caller thread
- ORDER: probe → clamp → compare → persist+post
- FAILURE: nil/display-nhỏ → return 0 (không persist/post)
- EVIDENCE: RECONSTRUCTION/PollFlush.m (F-032 §C)

## SE-POLL-003 — UI flushes (overdue + nudge tick)
- FUNCTION: 371AC + 370F8 (PollFlush.m)
- CONDITION: 371AC vô điều kiện; 370F8 khi DDz1.visible && !livePresentRunning && nonudgetick vắng
- EFFECT: DDz1 method calls (dropOverdueNotice; nudgePresent:"tick")
- TARGET: [DDz1 shared] (không plist/post/knob ở 371AC; post trong nudgePresent nếu có = UNKNOWN)
- DATA: —
- TIMING: main (163C40>0) else async (từ 22AD0 dispatch)
- THREAD: main hoặc async queue
- ORDER: sau probe trong tick (371AC trước 370F8 theo 22AD0:78-100)
- FAILURE: guards fail → return (không flush)
- EVIDENCE: RECONSTRUCTION/PollFlush.m (F-032 §C)

## SE-CNAB-001 — connChanged/screenDisconnect fan-in
- FUNCTION: onCarPlayConnChanged: (229FC.c:9) + onScreenDisconnect: (22A8C.c:9) (CNABConn.m)
- CONDITION: 229FC userInfo IsConnected bool (true → 7BCBC log gated 164710/164709, else disconnect); 22A8C bỏ qua a3, !carPlayConnected → disconnect @"UIScreenDidDisconnect"
- EFFECT: (chỉ forward) gọi cnabDoCarPlayDisconnect: (SE-CNAB-002)
- TARGET: —
- DATA: reason string (229FC exact UNKNOWN; 22A8C = "UIScreenDidDisconnect")
- TIMING: đồng bộ
- THREAD: NSNotification thread
- ORDER: trước SE-CNAB-002
- FAILURE: N/A (void, không transform/globals)
- EVIDENCE: RECONSTRUCTION/CNABConn.m (cnab_observers §4)

## SE-CNAB-002 — disconnect teardown + posts
- FUNCTION: cnabDoCarPlayDisconnect: (227E4.c:9; CNABConn.m)
- CONDITION: reason bất kỳ; teardown đầy đủ CHỈ khi DDz2.active (inactive → chỉ log)
- EFFECT: teardown + log + async block + conditional posts
- TARGET: 76224 + 7B924 log; async queue 165118 block 146308 (UNKNOWN); 163C40>0 → 371F4 else async; active → dismiss + DDz1 invalidateForDisconnect + notify_set_state(162DD8,0) + zero xmmword_163A98/AA8/AC0+qword_163AD0 + notify_post(cpdisconnect) + 4D0F4("CarPlay disconnect")
- DATA: —
- TIMING: đồng bộ + async block
- THREAD: caller thread + queue 165118
- ORDER: log/teardown → async → flush → (active) dismiss/invalidate/state/posts
- FAILURE: inactive → skip teardown (chỉ log); 371F4/146308 bodies UNKNOWN
- EVIDENCE: RECONSTRUCTION/CNABConn.m (cnab_observers §5)

## SE-CNAB-003 — carWin registry + nudger
- FUNCTION: onCarWindow: (99D4.c:9; CNABConn.m)
- CONDITION: userInfo NSDictionary + bid NSString length>0 + W,H NSNumber >=1.0 (else return)
- EFFECT: dict writes (size/pid) + conditional nudger
- TARGET: lazy 1635B8[bid]=CGSize + 1635C0[bid]=@(pid) (pid>=1); pid đổi → remove 1635C8[bid] (throttle map, init UNKNOWN, nil-safe); 13AB8-hit → 127F0(bid) debounced nudger (skip nếu nonudge-knob / CACurrentMediaTime>=1635D0+? / 12C48 rect; set now+4.0, after 1s → 12D84)
- DATA: counter 163640 cap 59
- TIMING: đồng bộ
- THREAD: NSDistributed notify thread (carwindow)
- ORDER: gates → lazy dicts → pid-change clear → persist → lookup → nudger
- FAILURE: gates fail → return (không ghi); 1635C8/nudger-arithmetic UNKNOWN
- EVIDENCE: RECONSTRUCTION/CNABConn.m (cnab_observers §6)

## SE-SPIKE-001 — skipEvict single-use gate
- FUNCTION: spikeHostSlots:natives:carPlayUI:skipEvict: (3CC44.c:311; SpikeHosting.m)
- CONDITION: `!skipEvict && exists(/var/tmp/duodash_ab_split_evict)` (v49 :308-309)
- EFFECT: conditional DDz2 call (evictFromPhone — nội bộ UNKNOWN)
- TARGET: [DDz2 evictFromPhone] (suppress khi skipEvict=1; no-op khi flag vắng)
- DATA: a6 use duy nhất cả chain (decl :9 + check :311); KHÔNG forward vào hàm con
- TIMING: đồng bộ trong spike loop setup
- THREAD: caller thread (2565C present-commit)
- ORDER: trước slot loop (sau globals init :102-124)
- FAILURE: N/A (ngoài điểm này không kill/unhost/dismiss nào khác)
- EVIDENCE: RECONSTRUCTION/SpikeHosting.m (F-035; sửa giả thiết "forward nguyên vẹn")

## SE-SPIKE-002 — slots guard + error dismiss
- FUNCTION: 3CC44 loop (:74-80, :292-305; SpikeHosting.m)
- CONDITION: v14=min(counts); guard 0..3 (v14>=4 → return nil, không tạo/dismiss/notify)
- EFFECT: view creation (via spikeCreateSlot:) + NSMutableArray slots (autoreleased) + error-path dismiss
- TARGET: slots[k] (bid sanitized 3DD4C + native CGSizeValue); error nil → dismiss + post cpdisconnect + return nil (:298-304)
- DATA: return HYPOTHESIS caller 2565C kiểm tra count; không xóa slot trực tiếp (chỉ evictFromPhone gián tiếp)
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: sau SE-SPIKE-001 + IPC-FS (lscape/.tripped/.inflight/respring + 372CC) + globals (163DC8++/163DC0/163D48/163D50/162F08)
- FAILURE: spikeCreateSlot==nil → dismiss + notify (nhánh duy nhất); v14>=4 → nil silent
- EVIDENCE: RECONSTRUCTION/SpikeHosting.m (F-035)

## SE-SPIKE-003 — slot create/degrade paths
- FUNCTION: spikeCreateSlot:index:native: (3BBF0.c:10) + degradeSlot: (3C1F0.c:9; SpikeHosting.m)
- CONDITION: 3 nhánh — CPUI flag (163D50) → tag-7020 pane; SB bid non-empty → entity/VC chain (3 degrade reasons → placeholder 36E98); bid rỗng → placeholder
- EFFECT: view alloc + VC ivars + globals (163D88/163D30[]/163D90[]) + degrade unhost (removeFromSuperview + invalidate, KHÔNG kill) + placeholder
- TARGET: slot view (SB VC.view / tag-7020 / 36E98); ivar self+8/24/32; 163D30[slot] clear khi degrade
- DATA: CPUI fallback carPlayDisplaySize (DDz1-use duy nhất) → <2 Zero else *2; setRequestedMode:2 + homeGrabberDisplayMode:1; 2 nil-cases (class-nil, index>2) không degrade
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: trong SE-SPIKE-002 loop (sau globals 3CC44)
- FAILURE: entity/VC/view-nil → degradeSlot (luôn placeholder — 36E98-success HYPOTHESIS)
- EVIDENCE: RECONSTRUCTION/SpikeHosting.m (F-035)

## SE-SPIKE-004 — geometry pushes schedule
- FUNCTION: scheduleGeometryPushesForSlot: (3D4FC.c:9; SpikeHosting.m; caller 3CC44:313-314)
- CONDITION: slot<=2 + bid non-empty + !CPUI-flag (else early-return)
- EFFECT: dispatch_after blocks (delays off_154160 — nội dung UNKNOWN)
- TARGET: main queue blocks 3DC38 captures (generation=163DC8, nativeSize=163D90, orientation=162F08, bid copy)
- DATA: —
- TIMING: async theo delays
- THREAD: main (dispatch_after)
- ORDER: sau slot loop (mỗi slot)
- FAILURE: early-returns (không throws); downstream 3DC38 UNKNOWN
- EVIDENCE: RECONSTRUCTION/SpikeHosting.m (F-035)

## SE-HSPLIT-001 — 2-pane wrapper
- FUNCTION: hostSplitL:right:skipEvict: (217EC.c:10-42; HostSplit.m)
- CONDITION: unconditional (nil-coalesce L/R → @"")
- EFFECT: array build + hostSlots call (onHosted=nil → 2565C skip callback)
- TARGET: [L,R] arrayWithObjects:count:2 → hostSlots(...,0)
- DATA: —
- TIMING: đồng bộ (async nằm trong 218D8/2410C chain)
- THREAD: caller thread
- ORDER: entry wrapper (không slots/evict/DDz/IPC/globals riêng, không chạm layout)
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/HostSplit.m (F-031)

## SE-HSPLIT-002 — in-place switch guards + convert
- FUNCTION: switchCarPlayUIInPlace:gen: (208F4.c:9; HostSplit.m; caller 202D0 envOnly)
- CONDITION: guards từ chối → return 0 (!active/split/visible, inFlight/maximized/gen/layout/count/word-flags); bids khớp hostedSlotBids + size>=1 + 22D64 (else 0)
- EFFECT: slot convert (convertSlotToCarPlayUI: + 26F60 view + replacePaneAtSlot:) + rollback (setSlot:0 đã làm) + rebuildMat + async completion (25EDC 100ms → 25FE0 else direct)
- TARGET: word_163A00[slot]=1; v112/v107 merges; 163970 pending; 763E0 kill-conditional (R3); block 26FE4 captures
- DATA: return 1 = accept KỂ CẢ rollback một phần (semantics HYPOTHESIS); eligible flags 22E40; index order giữ nguyên HYPOTHESIS
- TIMING: convert đồng bộ + completion async 100ms
- THREAD: caller thread + 25EDC/25FE0
- ORDER: convert loop → rebuildMat → merge → 763E0 → schedule continuation
- FAILURE: convert-fail → rollback + return 1 (không phải lỗi); guards-fail → return 0 → caller rơi vào host block
- EVIDENCE: RECONSTRUCTION/HostSplit.m (F-031)

## SE-HSPLIT-003 — in-place continuation
- FUNCTION: 26FE4 block (208F4.c:544-573, body :81-260; HostSplit.m)
- CONDITION: gates active&&split&&visible&&carPlayConnected (trong continuation)
- EFFECT: DDz calls + prefs evict + ack post
- TARGET: clear 163970; 7764C check; 85B8 evict; setSlot:1/0 + spikeCreateSlot: + replacePaneAtSlot: + scheduleGeometryPushes: + rebuildMatForEnvironment + 9424(1,...,cpuiGen=162E60++) + 4D0F4("split.cpui-in-place")
- DATA: —
- TIMING: async (sau 25EDC 100ms / 25FE0)
- THREAD: continuation queue
- ORDER: sau SE-HSPLIT-002
- FAILURE: gates fail trong continuation → skip (evict = setSlot+replacePane+85B8 HYPOTHESIS)
- EVIDENCE: RECONSTRUCTION/HostSplit.m (F-031)

## SE-EVICT-001 — prefs logical evict
- FUNCTION: 85B8(bid) (85B8.c:9-47 FULL; Evict.m)
- CONDITION: bid non-empty + !(bid==main && ∉merged-list) (inverted-check :31-33)
- EFFECT: prefs writes + regenerate + notify (logical evict — KHÔNG kill/unhost process)
- TARGET: SetAppValue(ui)+SetAppValue(more)+Sync (84D8) + 74C8() → writeToFile plist + post resolved (sau clear-main-hoặc-giữ + removeObject:bid)
- DATA: main via 7044(carplay_ui); merged via 70FC (7E730 dedup trừ main)
- TIMING: đồng bộ
- THREAD: caller thread (20010 / 25C4C / 26FE4 call-sites)
- ORDER: read → check → mutate-copy → save → republish
- FAILURE: guard-fail → no-op (không ghi)
- EVIDENCE: RECONSTRUCTION/Evict.m (F-036; FULL body, callees objc/CF only)

## SE-EVICT-002 — liveness probe (read-only)
- FUNCTION: 7764C(snapshot,filter) (7764C.c:9-116 FULL; Evict.m)
- CONDITION: SB-gated (once + byte_1646A1==1 + bundle springboard, else return -1)
- EFFECT: counter return (KHÔNG side-effect: retain/release + stack buffer)
- TARGET: return count (live khớp pid+path) / 0 (không khớp) / -1 (non-SB/UNKNOWN)
- DATA: a1 NSArray<{pid,path,bid}>; filter rỗng/nil = match-all; pid>=2 + proc_pidpath + strcmp
- TIMING: đồng bộ
- THREAD: caller thread (25C4C / 25FE0 / 26FE4)
- ORDER: gate → iterate → count
- FAILURE: TÀN DƯ callers ép unsigned + !=0 truthy → -1 cũng truthy ngoài SB (intent UNKNOWN); 25C4C:113 pure-call bỏ kết quả
- EVIDENCE: RECONSTRUCTION/Evict.m (F-036; không check gen/state/frontmost/sleeping)

## SE-EVICT-003 — Home-transition evict
- FUNCTION: evictFromPhoneThen: (3AE50.c:9-186 FULL; Evict.m; wrapper 3AE48 nil-completion)
- CONDITION (thứ tự): noevict vắng → skipfrontmost-vắng-hoặc-không-frontmost → SBMainWorkspace+entity classes + responds → request tạo ok
- EFFECT: SB Home-transition request (app background gián tiếp — KHÔNG SIGKILL) + exactly-once completion
- TARGET: createRequestWithOptions:0 + setActivatingEntity:Home (block 3F100) + executeTransitionRequest:; completion!=nil → version-gated block attach (setCompletionBlock:/addCompletionHandler: CF<1946.102 đảo) + watchdog 2s (3F170, guard 1-lần)
- DATA: frontmost via 3EDFC (slot0 bid vs _accessibilityFrontMostApplication)
- TIMING: đồng bộ request + async completion/watchdog
- THREAD: caller thread + main (watchdog)
- ORDER: guards → workspace → request → completion-attach → execute → cleanup
- FAILURE: guard/class/request-fail → LABEL_2 (completion ngay, không evict); v20==0 → completion ngay
- EVIDENCE: RECONSTRUCTION/Evict.m (F-037; callers 3CC44:312/3B2D8:189/211)

## SE-CPUIGEN-001 — counter lifecycle
- FUNCTION: 162E60 post-increments (27C88:42 / 26FE4:256 / 2565C:127 / 218D8:699; Cpuigen.m)
- CONDITION: mỗi site guards riêng (27C88 đầy đủ nhất: main + active/split/visible/connected + bid/more; 26FE4 outer-4-đk; 2565C unconditional v11=0/1; 218D8 reshow-branch)
- EFFECT: global write (monotonic host-side counter, idiom `old = counter++`)
- TARGET: qword_162E60++; BSS-init HYPOTHESIS 0 (không store tường minh; reset UNKNOWN)
- DATA: counter nội bộ (không userInfo/timestamp); IPC numberWithUnsignedLongLong (9424:92)
- TIMING: đồng bộ tại site
- THREAD: caller thread (27C88 main-thread gate)
- ORDER: site-guard → increment → 9424:a6
- FAILURE: N/A (27C88 else → v6=0 return)
- EVIDENCE: RECONSTRUCTION/Cpuigen.m (F-040; 4 sites cùng idiom)

## SE-CPUIGEN-002 — consume + readers + stale-check
- FUNCTION: 9424:a6 → host.state + readers 20010/9D64 (Cpuigen.m)
- CONDITION: 9424 length||count → dict["cpuiGen"] (:90-93) → post host.state (:102); 1FB5C/9400 truyền 0 cứng (chỉ 4 split/CPUI sites dùng counter)
- EFFECT: IPC publish + CarPlay-side echo/reads
- TARGET: host.state cpuiGen → 20010:35-36 read (stale-check !ok && incoming+1==counter → dedup per-gen 163988/163990 → 85B8 retry; forward DDz1 trước, độc lập) + 9D64:252-253 read (→1636E8/1637A0/986C echo "already"/gates BFF4/C37C) + 986C pack vào cpui.status
- DATA: —
- TIMING: đồng bộ (post + reads tại handlers)
- THREAD: notify threads
- ORDER: increment → 9424 → post → readers
- FAILURE: stale-check duy nhất 20010:69 (không site nào khác); forward-before-check (độc lập)
- EVIDENCE: RECONSTRUCTION/Cpuigen.m (F-040; H1-H5)

## SE-SPAWN-001 — teardown một bid
- FUNCTION: D154(bid,a2) (D154.c:9; SpawnTeardown.m; caller 9D64 GC/spawn + CE5C)
- CONDITION: VC=163578[bid] tồn tại (probe 13AB8); background-scene path khi VC + EEF0 + responds (else v14=0)
- EFFECT: scene-background + detach view + conditional tombstone/evict
- TARGET: block 13F90 + afters 15s (14040/1404C, điều kiện bit) → detach (10188/willMoveToParent/view-hide/removeFromSuperview/removeFromParent) → a2==1: 163590 add (tombstone) else xóa 163590 + F150 + xóa 163578[bid] + (v14==0&&bits) BBF8 → 163588-count==0 → 127B4()
- DATA: v5/v28 nghĩa UNKNOWN; không post trực tiếp
- TIMING: đồng bộ + after 15s schedules
- THREAD: caller thread + timer blocks
- ORDER: probe → background → detach → tombstone/evict → empty-check
- FAILURE: v14==0-path (không background) vẫn detach
- EVIDENCE: RECONSTRUCTION/SpawnTeardown.m (F-032)

## SE-SPAWN-002 — teardown toàn cục
- FUNCTION: CE5C() (CE5C.c:9; SpawnTeardown.m; caller 9D64 !activated)
- CONDITION: unconditional (CCEC ensure trước)
- EFFECT: per-bid teardown loop trên snapshot-copy + container clears
- TARGET: copy allKeys 163588 → D154(key,0) từng key; copy 163590 → D154 từng object; removeAllObjects 163590 + 1635A8
- DATA: arg call-site 9D64:727 ignored (armless — U04 9D64)
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: ensure → snapshot → loop → clear
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/SpawnTeardown.m (F-032)

## SE-SPAWN-003 — abort/reset + support globals
- FUNCTION: B9A8(keep) + BBF8/BCDC/BD18 (SpawnTeardown.m)
- CONDITION: B9A8 nhánh 163528 non-empty / 163550 non-empty / cả-hai-rỗng no-op; BBF8 key non-empty (+gen-match khi a2!=0); BCDC source non-nil; BD18 key non-empty + w,h>=1
- EFFECT: abort bid hiện tại (clear state + grace delayed-evict HYPOTHESIS hoặc BBF8+15A94) + conditional-evict dicts + timer-cancel + size-register
- TARGET: B9A8: ++1636E0, clear 163540/15278/163528/rect/1636E8/163538/1636F0 (+after 3s 15DA4 khi keep-match, else BBF8(bid,0)); BBF8: xóa 163510/163518; BCDC: cancel+nil 163558; BD18: 163510[key]=CGSize + ++163718 + 163518[key]=gen (UNKNOWN value)
- DATA: BE34 predicate dùng trong B9A8 branches; không post trực tiếp
- TIMING: đồng bộ (+after 3s grace khi keep)
- THREAD: caller thread
- ORDER: branch-select → clear → evict/cancel/register
- FAILURE: guards-fail → no-op từng helper
- EVIDENCE: RECONSTRUCTION/SpawnTeardown.m (F-032)

## SE-SPAWN-004 — spawn router + base gate
- FUNCTION: D4C4(bid,gen,rect) + D01C(bid,gen,retry,rect) (SpawnLaunch.m; caller 9D64/CB08-paths)
- CONDITION: D01C gate 1637A0==gen (else no-op) + BE34 base-check (base → 986C/backoff, else D4C4); D4C4 fast khi 163588+163578 có bid (→D684), else C2A4-route
- EFFECT: route spawn (fast re-layout / waiter / base-reject)
- TARGET: D4C4: D684 ngay / CB08(copy,killed,20,E7C4,E7DC) / D684-telemetry-direct; D01C: 986C "is_base_app" (retry<=0) / after-100ms-14060 (còn retry) / D4C4 (non-base)
- DATA: rect via v75 lookup (passing UNKNOWN — U05 9D64)
- TIMING: đồng bộ route (+async waiter/retry)
- THREAD: caller thread
- ORDER: gate → base-check → fast/waiter/reject
- FAILURE: gate-fail → no-op (D01C); C2A4-nil → D684 telemetry-direct
- EVIDENCE: RECONSTRUCTION/SpawnLaunch.m (F-032)

## SE-SPAWN-005 — launch dispatcher
- FUNCTION: BFF4(bid,gen,retry,rect) (BFF4.c:9; SpawnLaunch.m)
- CONDITION: gate 163528 non-empty + 1636E8==gen (else return); BE34 base? (base: retry<=0 → timeout-ack else after-100ms-15238; non-base: confine-test)
- EFFECT: confine/retry/timeout dispatch + acks + retry schedules + env persist
- TARGET: B9A8(0)+986C "launch_timeout" / after-100ms 15238 / 14CA0 confine-test → 163538=FAF0 + 14E74(bid,gen,30,rect) / B9A8(1)+986C "confine_failed"; ghi 163538
- DATA: 13220 nil + 163720<=9 gate cho 14C80-path; post 986C (ack)
- TIMING: đồng bộ + after-100ms retries
- THREAD: caller thread + timer blocks
- ORDER: gate → base/timeout-route → confine-route → ack/schedule
- FAILURE: gate-fail → return silent; confine-false → confine_failed ack
- EVIDENCE: RECONSTRUCTION/SpawnLaunch.m (F-032)

## SE-SPAWN-006 — predicates + killed-waiter
- FUNCTION: BE34 + C2A4 + CB08 (SpawnLaunch.m)
- CONDITION: BE34 rỗng→nil (pure); C2A4 rỗng→nil + array/count/byte_163748/nodeathwait-vắng/14080==0 (else nil); CB08 check-pass + 14080!=0 → done-ngay / hết-retry → done / còn → after-50ms
- EFFECT: predicate values (không side-effect) + waiter schedules
- TARGET: BE34: isEqual/contains hướng-chứa ("base" tên HYPOTHESIS); C2A4: 163570[bid] array; CB08: after-50ms 1427C retained / lock-1423C + đọc 163560 + done
- DATA: C2A4 chọn CB08-vs-C37C (D4C4/9D64:451-452); CB08 20 retries (D4C4:63), 9D64:473 count UNKNOWN
- TIMING: đồng bộ predicates + async waiter
- THREAD: caller thread + timer
- ORDER: predicate → waiter → done/retry
- FAILURE: CB08 check-false → return (không schedule); llround-UB HYPOTHESIS (AAAD0-style, không overflow-check)
- EVIDENCE: RECONSTRUCTION/SpawnLaunch.m (F-032)

## SE-EVLAUNCH-001 — event-launch 3 tiers + acks
- FUNCTION: C37C(bid,gen,rect) (C37C.c 324 dòng; EventLaunch.m; caller 9D64 C2A4-nil fallback)
- CONDITION: tier-0 BE34-base / tier-1 cached-validator (F654+1439C+145F8 true) / tier-2 heavy (noeventlaunch vắng)
- EFFECT: launch attempt + ack (BFF4 retry 0/30) hoặc fail-ack + telemetry-reasons
- TARGET: BFF4(bid,gen,0) (base) / 163530=copy + BFF4(bid,gen,30) (cached/success) / B9A8(0) + 986C "no_launch_route" + 9 reasons (fail); heavy: DB/CAR introspect + mode/validate + build + handleEvent:
- DATA: OS-class HYPOTHESIS; F654/1439C/145F8/build-helpers/v25/knob UNKNOWN
- TIMING: đồng bộ (tiers) + BFF4 async retries
- THREAD: caller thread
- ORDER: base → cached → heavy → ack
- FAILURE: heavy-fail → no_launch_route + reason (9 taxonomy); base/cached → BFF4 trực tiếp
- EVIDENCE: RECONSTRUCTION/EventLaunch.m (F-032 item 9)

## SE-SPAWNMISC-001 — active-notify + view predicate
- FUNCTION: B768 + BEE4 (SpawnMisc.m)
- CONDITION: B768 unconditional (nil-safe selectors); BEE4 view+superview non-nil (else return nil)
- EFFECT: SB notify + dock refresh (B768) / view position-check/move + out-flag (BEE4)
- TARGET: B768: _bundleIdentifierDidBecomeVisible + setActiveBundleIdentifier:animated: + _refreshAppDock (15F40 object HYPOTHESIS SB/HomeScreen); BEE4: convertPoint → lệch<=0.5 cả-2 ? *out=0 : setFrame + *out=1 (size-giữ UNKNOWN)
- DATA: bid chọn a1+32 else 1634B8/1634C0; không post/global trong file
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: độc lập (helpers lẻ)
- FAILURE: 15F40-nil → chỉ release; thiếu selector → skip; view/superview-nil → return
- EVIDENCE: RECONSTRUCTION/SpawnMisc.m (F-032 items 1,6)

## SE-SPAWNMISC-002 — dock ticker + containers
- FUNCTION: B144 + CCEC (+D684-note) (SpawnMisc.m; caller 9D64 ticker ×2)
- CONDITION: B144 main-thread (else async-return) + window (else create) + hide-gates (1635F0==1, nodockhide vắng, 1635EC>=1, pid-live); CCEC unconditional idempotent
- EFFECT: dock-hide ticker + timer 1s + 7-containers ensure
- TARGET: B144: 1635E0 timer + 12D0A8 handler + bookkeeping 1637D0/1/8 + setHidden:1 + bid-quét (163528∩bounds else 163588/1635A8); CCEC: 7 dicts/sets/arrays lazy-init; D684 body UNKNOWN (không bịa)
- DATA: hide-semantics HYPOTHESIS; cancel + restore-hidden khi gates-fail
- TIMING: đồng bộ + timer 1s + handler
- THREAD: main (async-return nếu non-main)
- ORDER: gates → window → bid-select → timer → hide
- FAILURE: gates-fail → cancel timer + restore hidden (không hide)
- EVIDENCE: RECONSTRUCTION/SpawnMisc.m (F-032 items 11,17)

## SE-FASTRELAY-001 — fast re-layout path
- FUNCTION: D684 fast (D684.c:124-168; FastRelayout.m; callers D4C4 + E7DC)
- CONDITION: v11=163588[bid] && v12=163578[bid] VC (else slow path)
- EFFECT: meta-update + embed/resize + timer-re-arm hoặc geometry-push
- TARGET: luôn update rect/gen/posted=NO/since + xóa nopic/rebinds/bgsince/refg; BD18 + E7F4 embed; ECB8 resolve; giống → EE4C re-arm; khác → ED5C push + stamp pushed + EE4C + after-50ms 12D068
- DATA: rect-compare cũ-vs-mới (CGRectValue)
- TIMING: đồng bộ (+after 50ms khi khác)
- THREAD: caller thread + timer block
- ORDER: compare → update → embed → same?re-arm:push
- FAILURE: N/A (luôn update meta cả khi giống)
- EVIDENCE: RECONSTRUCTION/FastRelayout.m (F-034 §4; KHÔNG gọi DDz)

## SE-FASTRELAY-002 — slow path + failure telemetry
- FUNCTION: D684 slow (D684.c:171+; FastRelayout.m)
- CONDITION: thiếu một (VC tồn tại nhưng bid ∈163590 + EEF0==1 → attach; else F150-drop + rebuild 2 họ entity)
- EFFECT: VC rebuild (DB/CAR families) + attach/embed/foreground HOẶC fail-telemetry
- TARGET: F3E0 root + environment → (a) DBApplicationSceneViewController/_CAR + insets / (b) DBDashboard[Proxied]Entity (type-encodings verify) → lưu 163578 + addChild + E7F4 + didMoveToParent + state-dict 5 keys →163588 + BD18 + 163598-add + FC10 + foregroundSceneWithSettings (FF98) + ED5C+EE4C; fail → FB9C 14 reasons
- DATA: E7F4/ECB8/EE4C/ED5C/F150/F3E0/FC10/FF98 bodies UNKNOWN
- TIMING: đồng bộ (+foreground completion async)
- THREAD: caller thread
- ORDER: tombstone-check → drop/rebuild → attach → foreground
- FAILURE: 14 fail reasons → FB9C(bid,gen,reason) (no foreground/persist); thiếu foreground-selector → no_foreground
- EVIDENCE: RECONSTRUCTION/FastRelayout.m (F-034 §4; không chạm DDz state)

## SE-DDZ-001 — DDz1 shell map
- FUNCTION: DDz1 class (63 methods; DDzCore.m; F-034 §§0-1)
- CONDITION: class-level map (không single body)
- EFFECT: state + method-cluster inventory (window lifecycle, splash+notice 8, layout, swap/mirror 5, maximize 11)
- TARGET: rootWindow/backdrop/paneContainer/content/splash/notice/matStrips/exitChip + _visible/_maxActive/_maxPos/_maxInFlight/_mirroring; caller-names giải từ address (1FB5C/202D0/208F4/218D8/227E4/… subs)
- DATA: dump* ×5 stub rỗng; totals 63 = 61 instance + 2 class; strings `DDz` ZERO hit; DDz4 tồn tại ngoài-phạm-vi UNKNOWN
- TIMING: N/A (map)
- THREAD: N/A
- ORDER: N/A
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/DDzCore.m (ddz_inventory §§0-1)

## SE-DDZ-002 — DDz1 central methods
- FUNCTION: +shared/+carPlayConnected/showWithHostView:/present (DDzCore.m; F-034 §3 FULL reads)
- CONDITION: shared once; connected AVExternalDevice-check; show non-nil; present _rootWindow non-nil
- EFFECT: singleton + HW-gate + show-entry + present-animation
- TARGET: +shared → 163C20 (once 163C28, không init window); +carPlayConnected stateless (7 callers poll/guard); showWithHostView: → block 33F5C sync-main (buildShell→installContent→present); present → unhidden + interaction + animate 0.25s + _visible=1 + nudgePresentAfterShow + startLivePresent (hide đối xứng async)
- DATA: —
- TIMING: show/present đồng bộ (+animate/hide async)
- THREAD: main (33F5C sync-main)
- ORDER: buildShell → installContent → present → nudge/live
- FAILURE: nil-inputs → NO (show/present); carPlayConnected-nil → NO
- EVIDENCE: RECONSTRUCTION/DDzCore.m (F-034 §3)

## SE-DDZ-003 — DDz2 hosting map + cross-links
- FUNCTION: DDz2 class (35 methods; DDzCore.m; F-034 §§2-3,5)
- CONDITION: class-level map + division hypothesis (tinh chỉnh)
- EFFECT: state/getters + host-spike chain + aux-scene + evict + dismiss/reset + cross-link directions
- TARGET: 163D30 bids/163D48 count/163D50 flags/162F08 orient/163D88+163DC0 active-split/_auxVC; getters 10; chain 3CAA4→3CC44→(3BBF0→3C1F0,3D4FC,dismiss)/3B2D8→(evict/handshake/build)/3AAF8→3C808; +shared 3F1B8 18 callers; DDz1→DDz2 5 sites vs DDz2→DDz1 1 site (3BBF0:6)
- DATA: hostedSlotBids snapshot ≤3 read-only; dismiss-caller-duy-nhất spikeHostSlots (re-host-dọn HYPOTHESIS)
- TIMING: N/A (map; bodies ở SpikeHosting/HostSplit/Evict/PollFlush)
- THREAD: N/A
- ORDER: N/A
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/DDzCore.m (F-034; cầu-nối CNAB↔shell HYPOTHESIS)

## SE-DDZ-004 — commit chain picker→prefs
- FUNCTION: 5F044/5F224/5F538/5F74C/5F8A4 (DDzCommit.m; F-039)
- CONDITION: onTilePressed gates (cnabBid + ∈apps + lọc gesture) → resolve → openSlot-guard → dedup-giữ-prefs-cũ → 6A13C-validate → bake → persist → reconcile → luôn 74C8
- EFFECT: prefs writes + Sync + resolved post (KHÔNG gọi host trực tiếp — sửa HYPOTHESIS SAI)
- TARGET: SetValue left/right/third + Sync; bake ratio/fracs (special-mode-guard); CPUI-reconcile có-điều-kiện 84D8; 74C8 → write plist + post resolved (tín hiệu duy nhất tới host); why chẩn đoán-không-persist ("picked %@ for slot %ld" / "gutter re-host swap")
- DATA: 6A13C 3-valued (clear/cài/lỗi-commit, drop khi chưa-cài-mà-SB-sống); 5F044 legacy tàn-dư (callers none); parallel paths (gutterFrac/swap/layout — layout không qua commitSlotBids)
- TIMING: đồng bộ trong picker tap (close dù commit thành công hay không)
- THREAD: UI thread (picker)
- ORDER: resolve → guard → dedup → validate → bake → persist → reconcile → republish
- FAILURE: guard/dedup/validate-fail → silent return/drop (không alert/log)
- EVIDENCE: RECONSTRUCTION/DDzCommit.m (F-039; host gián tiếp via resolved)

## SE-DDZ-005 — DDz3 UI clusters + buildKitLevel
- FUNCTION: DDz3 class (153 methods map-level; DDzPicker.m; F-034 §6)
- CONDITION: map-level (tên/cụm/addr-range CONFIRMED; thân HYPOTHESIS trừ commit-chain)
- EFFECT: cluster inventory (không bodies): init → handles/gutter-drag → picker open/close → grid/tile → arrange → commit (=DDzCommit.m) → resize → chips → kit → buildKitLevel → layout-tiles
- TARGET: 0x524d4–0x69c4c instance-only (không +shared); hàng trăm call-sites tới DDz1/DDz2 (tầng UI trên cùng — data CONFIRMED); buildKitLevel:pane: 0x63CE4 asm-only (~100 callees, stack 0xB90 — NỘI DUNG UNKNOWN, không suy thân)
- DATA: —
- TIMING: N/A (map)
- THREAD: N/A
- ORDER: N/A
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/DDzPicker.m (F-034 §6)

## SE-PREFS-001 — setters → republish
- FUNCTION: 746C/84D8/637E8 setters (PrefsResolver.m cross-ref section; 74C8 publish ở SE-74C8-001..003 — không duplicate)
- CONDITION: 746C layout 1..8 (else return nguyên); 84D8 normalize via 7E730; 637E8 flip via 836C-read
- EFFECT: prefs writes + republish chain
- TARGET: SetAppValue + Sync + 74C8() → 14 keys + navprovider ×2 + write appbridge.plist + post resolved (8 callers republish: 746C/84D8/27E20/29198/56B24/5F8A4/637E8/69824)
- DATA: —
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: validate/normalize → SetAppValue → Sync → republish
- FAILURE: 746C out-of-range → return nguyên (không ghi)
- EVIDENCE: RECONSTRUCTION/PrefsResolver.m (B-15/F-025; bulk-keys off_154208 content HYPOTHESIS U04)

## SE-MIG-001 — import True→Duo
- FUNCTION: import guards + precheck + wipe-then-migrate + files (Migration.m §§1-5; license branch ở License.m)
- CONDITION: import.done vắng + import.running vắng (else abort-goto LABEL_162) + precheck pass (blob/key/counts)
- EFFECT: prefs migrate + license import/reseal + file copies + done-log
- TARGET: 85148 2-hosts migrate (rename-map/denylist/off_154268 UNKNOWN) + xóa nguồn SetMultiple-nil; license A/B1/B2/C (verify "duodash", A4558/A50CC, xóa off_154238 UNKNOWN); airplay/iconstate 85800-copies + navapps merge (union/đè/ưu-tiên) + flags msrv/standdown; log import.done exact-format + remove running
- DATA: —
- TIMING: đồng bộ trong 4C34 ctor (once-only)
- THREAD: main (role-1 ctor)
- ORDER: guards → precheck → prefs → license → files → log
- FAILURE: guard/precheck-fail → goto LABEL_162 (skip); write-fail running → giữ lock (lần sau abort tiếp)
- EVIDENCE: RECONSTRUCTION/Migration.m (F-019)

## SE-MIG-002 — defaults bootstrap
- FUNCTION: DDBootstrapDefaults (Migration.m §6; F-020)
- CONDITION: stat(defaults.done)!=0 (else skip) + existing = airplay-marker || settings-keys || import.done-existed
- EFFECT: conditional seed-false + done-record
- TARGET: existing==1 → keys thiếu trong 3 (pane_unload_close_enabled/appbridge_autostart/disconnect_close_enabled) = kCFBooleanFalse + sync ok/failed; existing==0 (fresh) → không seed; ghi defaults.done (existing: at/v/result/why/pinned/kept/sync; new: at/v/result=new) + "\n" UTF-8
- DATA: 85D30 format-only (join/none)
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: guard → existing? → seed → record
- FAILURE: N/A
- EVIDENCE: RECONSTRUCTION/Migration.m (F-020)

## SE-LOCALE-001 — language write/read/observers
- FUNCTION: 6A4E4/9AFB0/9B314 + 6 observers (LocaleFlow.m; F-030/B-20)
- CONDITION: write guard 9B284-whitelist; read tier-order (lang_force → prefs → carnav-migrate → en) + validate mỗi bước; observers unconditional clear+reload
- EFFECT: prefs writes + Sync + posts + cache ops
- TARGET: write: SetAppValue(duodash_language) + Sync + 9B314-clear + post language.changed; read: cache 164C38+lock (whitelist 17, 16 strings UNKNOWN); observers (9B848/948C0/8C41C/8EFE4/920C0/93A3C → 9B314 + async main reloads; CN* bodies UNKNOWN)
- DATA: truedash_language 0-hit dead/legacy (giữ nguyên); NSLocale en_US_POSIX chỉ formatter
- TIMING: đồng bộ (+async main reloads)
- THREAD: caller + main
- ORDER: write → post → clear+reload; read → tier-fallback → cache
- FAILURE: whitelist-fail → write bị chặn; knob tồn tại (EndEditing-cousin, không ở đây)
- EVIDENCE: RECONSTRUCTION/LocaleFlow.m (F-030/B-20; version/device fail-soft ở COMPARISON)

## SE-LIC-001 — offline verify + validators (pure)
- FUNCTION: DDVerifyLicense + DDParseDouble/DDParseInt (License.m; F-006 + aa_validators)
- CONDITION: blob format b64url(json).b64url(sig) 2 parts; JSON v==1 + device + product + iat/exp windows
- EFFECT: return codes (KHÔNG side-effect): 0 OK / 1 empty / 2 format / 3 no-pubkey / 4 kid / 5 device / 6 expired / 7 skew / 8 v!=1 / 10 product (KHÔNG 9); ECDSA P-256/SHA256/X9.62 via SecKey (pubkey 65B uncompressed off_1542E0 HYPOTHESIS)
- TARGET: (return value only)
- DATA: validators NSNumber-only + finite-mask (Inf/NaN reject); AAAD0 llround (non-strict, no-whitelist, overflow-UB HYPOTHESIS); out ghi chỉ khi pass
- TIMING: đồng bộ
- THREAD: caller thread
- ORDER: format → schema → crypto → codes
- FAILURE: mọi fail silent return-code (không throw/log)
- EVIDENCE: RECONSTRUCTION/License.m (F-006/A397C + aa_validators exact)

## SE-LIC-002 — license clients (network)
- FUNCTION: DDActivate/DDInfo/DDEnv/DDHealthz (License.m; F-006/B-09/F-016/F-030)
- CONDITION: base hardcode (license_endpoint key dead); device_hash (A3558) + client 1.1.5+b1d14e0
- EFFECT: HTTPS POST/GET + persist verdicts/geometry + throttles
- TARGET: activate 30s {product_key,device_hash,email?,model,udid?,ios,client,product}; info 6s 16-keys obfuscated → 4 nhánh (403 conditional-verify / 200 cache+persist / 429 retry-1-lần-v89ms / error-D code 2); env 6s rate-limit <8; healthz GET 6s throttle 3s + spinlock → server_health row; verdicts file + 24h retry (rate_limited/invalid_key/device_limit/blocked/unavailable)
- DATA: thiếu device_hash → no_device_id; thiếu base → no_server (fail-soft)
- TIMING: async callbacks (timing thực UNVERIFIED)
- THREAD: session queues + main callbacks
- ORDER: offline-verify-trước (semantics giữ) → network → verdicts
- FAILURE: no-connection/unavailable → verdicts + retry (B-09 map)
- EVIDENCE: RECONSTRUCTION/License.m (MITM/server-side UNKNOWN)

## SE-LIC-003 — unrefuse + migrate-branch + prefs UI
- FUNCTION: DDUnrefuseIfNonceMatches + DDMigrateLicense + CN controllers (License.m; F-019 + aa_validators + F-015)
- CONDITION: unrefuse stored-nonce == async-nonce (non-empty copy, queue 1650E0); migrate theo (TrueDash-valid?, DuoDash-valid?, iat-mới-hơn?)
- EFFECT: conditional-delete file + license import/reseal/delete/keep + UI refresh (không verify lại ở UI)
- TARGET: unrefuse: refused.plist nonce-match → removeItem silent + re-arm (device-check + alert nếu fail), else giữ file; migrate: A-import (A4558 → imported/failed; key none/kept vs resealed/failed; xóa off_154238 UNKNOWN) / B1-delete+reseal / B2-none/kept / C-kept(+reseal); UI: CNLicenseActivation (~20 methods) + CNTweakManagement ← openLicenseActivation:/openTweakManagement: (bodies CN* chưa record)
- DATA: product prefixes 3 thế hệ; blob cũ verify dưới product "duodash"; pending_key/email stored (email never-required)
- TIMING: unrefuse async; migrate trong 4C34 once; UI on-push
- THREAD: license queue + main + UI
- ORDER: verify → unrefuse/migrate → UI verdicts (not_activated/activating/active/…)
- FAILURE: nonce-mismatch → no-op giữ file; deviceId-rỗng → no-device-id/none
- EVIDENCE: RECONSTRUCTION/License.m (KHÔNG write/chmod nào ở unrefuse — đính chính persist-SAI)

## SE-KEY-001 — focus intercept + publish
- FUNCTION: DDFieldDidFocus + DDPublishField + DDKeyPurge/DDKeyCardSet (KeyinputRelay.m §§focus/purge)
- CONDITION: gates thứ tự 4B90C (fail → passthrough native): --163054, 163ED9, keypane-on (162F88), nokeypane-knob, chưa-focus, cooldown, isSplit; secure → PASSWORD BYPASS (native, không vào relay); publish gate 45568 + path non-empty
- EFFECT: dummy inputView + plist write + chmod + notify begin (+ purge/card state)
- TARGET: weak 163F30/class 163F38 + dummy 163F40 + orig; snapshot 163F48 + duodash_keyinput.plist {bid,text,selLoc,selLen=0,kbType,returnKey,secure=@NO CỨNG,ts} + chmod off_154400 + post begin (+after 1.5s/ async bodies UNKNOWN); purge per-bid + seed/out; card 30F48 set/post
- DATA: serialize-fail → nuốt; secure field KHÔNG BAO GIỜ vào relay (password-literal 0 hit)
- TIMING: đồng bộ focus (+afters async)
- THREAD: UI thread
- ORDER: gates → bypass-check → store → dummy+orig → snapshot+publish+post
- FAILURE: gate-fail → passthrough (không chặn user); secure → native passthrough
- EVIDENCE: RECONSTRUCTION/KeyinputRelay.m (B-17; KeyApp writers HYPOTHESIS)

## SE-KEY-002 — seed + forward + patch + teardown
- FUNCTION: DDRebuildSeed + DDForwardOutToIn + DDDismissSB + password/keypane gates (KeyinputRelay.m)
- CONDITION: seed ts-window 10s (3A588, KHÔNG 30s) + secure!=1 + 38240-ok; forward 163CA0 non-empty + out-plist types; teardown triggers (lost-twice/rebuild-failed/watchdog≥3s + nokprecover)
- EFFECT: seed.plist write + post seed/apply + text-patch + notifications + teardown posts
- TARGET: rebuild (seed/out merge, out.text newer-wins) → 3896C seed.plist + post seed (3A588: bid→163CA0, ++163D18, 163D20=80, 6-entry dict); forward in.plist + post apply + --163D20; 44B1C patch (diff/insertText-setText + notifications + ret→shouldReturn/\\n, bypass-lần-2); dismiss (purge + post dismiss/fallback/end + teardown + card 38240-gates + UIApp 4C650/4D068/49778/449C8 + othertap-throttle/retap)
- DATA: ts<30s HYPOTHESIS (cảnh báo: hằng dylib là 10s/600s); keypane-OFF → passthrough + teardown + 38240-từ-chối
- TIMING: đồng bộ + watchdogs/afters
- THREAD: SB + UIApp threads (relay qua plists + notifies)
- ORDER: seed → KeyApp(HYPOTHESIS) → out → forward → apply-patch → dismiss/teardown
- FAILURE: rebuild-fail → fallback/teardown (tôn trọng nokprecover); out-nil/wrong-type → return
- EVIDENCE: RECONSTRUCTION/KeyinputRelay.m (B-17; 10 blocks sau-hop + KeyApp-writers UNKNOWN)

## SE-KBD-001 — hook mapping install (bodies UNKNOWN)
- FUNCTION: 455D0 + 4C858 ctors + AZ loop + swizzle + BKS (KeyboardHooks.m; HOOKS.md + F-017/F-013)
- CONDITION: 455D0 role5-unlisted (bundle-conditional Maps/Waze/duodashkey/RCT); 4C858 IFF duodash_kbpoc_kbd tồn tại (exists=ENABLE — đảo KILL)
- EFFECT: MSHook installs (mapping CONFIRMED; hook-fn bodies UNKNOWN trừ focus/swizzle/AZ)
- TARGET: orientation/geometry ~17 (UIScreen/UIWindow/VC/CPWindow/scene/orientation [!RCT]) + keyboard-size ~17 (UIKeyboardImpl/UIPeripheralHost/UIKBScreenTraits/duodashkey-gated/setters + didMoveToWindow + sendEvent:48924 + AVExternalDevice + NSBundle-cptrip-gated) + AZ×7 (counter + swallow-gate, F-017) + _UIKeyboardLayerHostView ×3 (native-kb màn-ngoài, 376DC) + BKS blank (4DF94 keepawake + backlight<0.2 + display_held) + PSTableCell swizzle (94E9C, body UNKNOWN)
- DATA: orig-slots off_163Fxx; RCT-minimal khi RCT app
- TIMING: install lúc ctor (once); hooks chạy per-call
- THREAD: target-process threads
- ORDER: ctor-guard → installs (focus bodies ở KeyinputRelay.m — không duplicate)
- FAILURE: class-nil → skip install (INFERRED từ pattern); SB-scene ×10 BLOCKED (F-018, raw asm)
- EVIDENCE: RECONSTRUCTION/KeyboardHooks.m (ledge mapping, KHÔNG nâng cấp nhãn)

## SE-KBOBS-001 — observer stubs + state machine
- FUNCTION: onKbShow/Hide/onDismiss/449C8/onEndEditing (KBObservers.m; F-032 §B)
- CONDITION: stubs unconditional no-op; onDismiss 163ED9==1 (+162F58>=1 → --); 449C8 163ED9 + responder-tồn-tại; onEndEditing gate 163ED9 + 162F88!=0 + knob-vắng (knob-tồn-tại → return, LOGIC ĐẢO)
- EFFECT: no-op / gated-decrement + full-teardown / conditional-teardown + post end
- TARGET: stubs `;` (CONFIRMED, sửa UNKNOWN cũ); 449C8: clear flags/weaks/counters + setInputView:nil+reload + resign (nếu responds); onEndEditing: 163F58=164130=v4^1 + object-match branches (v8) + --162F58 (+lần-nữa khi post end, chỉ khi 163F58==1) + clear + post keyinput.end có-điều-kiện
- DATA: 453B8 nokeypane TTL-1s-cache; posts cousin ở KeyinputRelay.m (không duplicate)
- TIMING: đồng bộ trong notification delivery
- THREAD: NSNotification threads
- ORDER: gate → match → decrement → teardown → conditional-post
- FAILURE: guard-fail → return (không teardown, không post)
- EVIDENCE: RECONSTRUCTION/KBObservers.m (F-032 §B; header-callees-stale note)
