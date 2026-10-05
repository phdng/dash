# HYPOTHESES.md

## H-001 RESOLVED → F-012 (CONFIRMED): suffix order đúng như đoán (SpringBoard/Preferences/CarPlay/mediaserverd/kbd).

## H-002 RESOLVED → F-011 (CONFIRMED): order = dyld 4 ctors → 44C0 dispatch blocks → dispatch_once(165508/AC7A4) → role body → once lồng (12CD20/12D378/12DD08/12DA78/12DAB8/12DA98/12DCE8).

## H-003 HYPOTHESIS: sub_4049C 10 SpringBoard selectors share cùng orig-table off_1637xx
Lý do: 27E20.c:263-274 gọi cùng wrapper nhưng decompile strip a3-a6.
Cần: raw asm 27E20 (BLOCKED — F-018).

## H-004 RESOLVED → F-017 (CONFIRMED): 12DB98 = 7 AZ* CarPlay-state hooks (spoof về 0 khi 163ED8).

## H-005 REJECTED → F-013: off_164450 là BKSDisplayServicesSetScreenBlanked (không phải IOMobileFramebuffer).

## H-006 RESOLVED (negative) → F-016: license_endpoint dead/legacy (0 code path đọc key).

## H-007 RESOLVED → F-016: crash upload về `crashreport_endpoint + /v1/reports` (configurable, default nil), không phải license host.

## H-008 (RESOLVED → F-006): ECDSA verify — đã CONFIRMED, giữ để khỏi regress.

## UNKNOWN (session-005):
- Entitlements thực (carplay-audio/maps/navigation? bluetooth-central?).
- Toggle effect chi tiết cho ~70 knobs chưa đọc body (P3-1 partial: tồn tại CONFIRMED, semantics-theo-tên HYPOTHESIS — EVIDENCE/toggle_matrix.md).
- Rename-map/denylist/off_154268/off_154238 nội dung (cần raw ARM64/__objc_dictobj decode).
- Stru block handlers opaque (Q-12) + schedulers 1A820/7B9EC/7BD58 (Q-13).
