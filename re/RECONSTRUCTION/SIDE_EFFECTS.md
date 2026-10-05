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
