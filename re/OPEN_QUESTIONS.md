# OPEN_QUESTIONS.md (session-002)
1. ~~Q-01 mod_init order~~ → CLOSED (F-011).
2. ~~Q-02 AC5FC suffixes~~ → CLOSED (F-012).
3. Q-03: hook-fn/orig 10 SB selectors — BLOCKED ON ARTIFACTS (F-018, cần raw asm 27E20).
4. ~~Q-04 12DB98 loop~~ → CLOSED (F-017, 7 AZ* hooks).
5. ~~Q-05 off_164450~~ → CLOSED (F-013, BKSSetScreenBlanked).
6. ~~Q-06 sub_4001C~~ → CLOSED (F-014, passthrough).
7. ~~Q-07 crash URL~~ → CLOSED (F-016, configurable endpoint + /v1/reports).
8. ~~Q-08 missing actions~~ → CLOSED (F-015, dylib CN* controllers).
9. Q-09: entitlements thực? Vẫn OPEN (không có file).
10. Q-10 (partial session-006): info-schema keys + 4 nhánh + side-effects DONE (EVIDENCE/version_device_ainfo.md §B); còn lại: mapping số v4 tuyệt đối (cần xref disasm), bodies AA9FC/AAAD0/A7E04, 16 strings whitelist, threshold 46340→4008, MITM server-side.
11. Q-11 (partial session-009): + spikeHostSlots: nội bộ + skipEvict truth + 85B8/7764C verdict (EVIDENCE/spike_hostslots.md, EVIDENCE/evict_helpers.md); còn lại: evictFromPhone nội bộ, DDz3 buildKitLevel + bodies, DDz4, a3 codes 0-4, 162E60 setter, snapshot nguồn *(a1+56/32/88). HYPOTHESIS evictFromPhone = phone-side unhost (kill? UNKNOWN).
12. Q-12 (mới): stru block handlers `12CD40/12CD60/130618/.../146268` + `stru_12D0C8/12D108` delayed — chưa resolve (cần disasm blocks).
13. Q-13 (mới session-004): schedulers `1A820/7B9EC/7BD58` (callers:none) — ai arm/cancel? HYPOTHESIS connect/notify paths ngoài decompile.
14. Q-14 (mới session-004): HYPOTHESIS cần runtime: 74C8.c:251 filter đảo, 746C 1..8, 10 keys off_154208 mapping, blacklist 164758, bounds 73E8/80D0 (xem TESTS.md dynamic).
