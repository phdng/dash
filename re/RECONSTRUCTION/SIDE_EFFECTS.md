# SIDE_EFFECTS.md — Side-effect ledger (starter session-012, function 2410C)
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
