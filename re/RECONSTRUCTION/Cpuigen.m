// RECONSTRUCTION/Cpuigen.m — APPROXIMATION synthesis (session-050)
// Source: EVIDENCE/cpuigen_trace.md (F-040; grep `162E60` toàn decompile/ —
//   duy nhất 5 hits, CONFIRMED trừ init/reset).
// KHÔNG compile ở đây (không toolchain iOS). UNKNOWN giữ nguyên.
// Semantics phải giữ: monotonic host-side counter, post-increment idiom
//   (check v6+1==counter ⟺ v6==lastSent), consume duy nhất qua 9424:a6,
//   stale-check duy nhất 20010:69, BSS-init HYPOTHESIS (không store tường minh).

#import "DuoDashShared.h"
// Writers (4 post-increments, counter nội bộ — không userInfo/timestamp):
//   27C88:42 (có đk + return gen), 26FE4:256 (in-place tail), 2565C:127 (split completion),
//   218D8:699 (reshow). Reader/stale: 20010 (status + stale-check + 85B8 retry).
//   Echo/readers CarPlay-side: 9D64:252-253 (→1636E8/1637A0/986C/BFF4/C37C).
// Cross-refs: HostSplit.m (26FE4), PresentCommitAck.m (2565C/218D8/9424),
//   SpawnLaunch.m (BFF4/C37C dùng echo), Evict.m (85B8 retry), functions/20010.md + 9D64.md.

// ---- Lifecycle ----
// Khởi tạo: KHÔNG store `=0/1` nào → BSS zero → gen đầu phát = 0 (HYPOTHESIS Mach-O).
//   Reset khi relaunch UNKNOWN (không site reset). Kiểu __int64 post-increment;
//   IPC qua numberWithUnsignedLongLong (9424:92).
// Tăng: 4 sites cùng idiom `old = counter++` (27C88, 26FE4, 2565C, 218D8).
// Consume: duy nhất 9424(a6=gen) (1FB5C/9400 truyền 0 cứng — chỉ 4 sites split/CPUI
//   dùng counter). 9424:90-93 (length||count → dict["cpuiGen"]) → :102 post host.state.
// Readers IPC: 20010:35-36 (status → stale-check) + 9D64:252-253 (v137 → lưu 1636E8
//   + echo 986C "already" + gates BFF4/C37C). Chiều ngược: 986C pack cpuiGen vào
//   cpui.status (a1 chính là v137 từ host.state).

// ---- 5 hits (bảng §1) ----
static void DDCpuiGenSites(void) {
    // H1 ĐỌC — 20010:69 stale-check (onCarPlayUIStatus:): v6=userInfo["cpuiGen"],
    //   v11=["cpuiOk"]; block async forward gen/ok/bid lên DDz1 noteCarPlayUIStatus
    //   (37924) TRƯỚC và độc lập stale-check. Check !ok && incoming+1==counter
    //   (⟺ incoming==lastSent) + bid non-empty → dedup per-gen
    //   (163988=lastFailedGen, 163990=set) → 85B8(bid) retry.
    // H2 GHI — 218D8:699 reshow: v105=counter++ → 9424(1,...,v105). Increment chỉ khi
    //   split-hosting + DDz1 chưa visible + geometry ổn + present ok (HYPOTHESIS "reshow").
    // H3 GHI — 2565C:127 split completion: v23=counter++ → 9424(v11,...,v23). v11=0/1 đều tăng.
    // H4 GHI — 26FE4:256 in-place tail: v41=counter++ → 9424(1,...,v41).
    //   Không check length/count tại site (khác 27C88); guard duy nhất outer 4-đk.
    // H5 GHI — 27C88:42 (gọn nhất, return gen): main-thread + DDz2.active && split &&
    //   DDz1.visible && carPlayConnected + 234A0 có bid/more → v6=counter++ →
    //   9424(1,...,v6) else v6=0 → return v6. Callers: 2F754:95 (maximize/re-host chờ echo:
    //   !v33 → restore else maxCPUIWaitGen=v33 + after 2s check); 2FC5C:103 (fire-and-forget).
}
