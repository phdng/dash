# EVIDENCE/cpuigen_trace.md — qword_162E60 lifecycle (session-011)
_Nguồn: subagent general grep `162E60` toàn decompile/ — **duy nhất 5 hits**. Mỗi claim có file:line + nhãn._

## 1. Bảng hits (CONFIRMED toàn bộ)
| # | Site | Code | Loại |
|---|---|---|---|
|H1|20010:69|`if ((v11&1)==0 && v6+1==(char*)qword_162E60)`|ĐỌC stale-check|
|H2|218D8:699|`v105 = qword_162E60++;` → 9424(1,...,v105,...) :700|GHI post-increment (reshow path)|
|H3|2565C:127|`v23 = qword_162E60++;` → 9424(v11,...,v23,...) :128|GHI (host.request.split completion)|
|H4|26FE4:256|`v41 = qword_162E60++;` → 9424(1,...,v41,...) :257|GHI (in-place switch tail)|
|H5|27C88:42|`v6 = qword_162E60++;` → 9424(1,...,v6,...) :43-44|GHI (có đk nội dung + return gen)|

Không store khởi tạo `=0/1` nào → BSS zero-init (HYPOTHESIS Mach-O; UNKNOWN reset khi relaunch).

## 2. Chi tiết
- **H1 đọc** (onCarPlayUIStatus:): v6 = userInfo["cpuiGen"].unsignedLongLongValue (:35-36); v11 = ["cpuiOk"].boolValue (:43-44); block async forward gen/ok/bid lên DDz1 noteCarPlayUIStatus (37924 :55-62, :14-19) TRƯỚC và độc lập stale-check. Check: !ok && incoming+1==counter (:69) → chính là gen cuối vừa phát (post-increment ⇒ counter = lastSent+1). Guard bid NSString non-empty (:51). Pass → dedup bid per-gen (163988=lastFailedGen, 163990=set :71-78) → 85B8(bid) retry (:81-84).
- **H5 ghi** (27C88, gọn nhất, return gen): main-thread (:23) + DDz2.active && split && DDz1.visible && carPlayConnected (:26-32) + 234A0 có bid/more (:38-40) → v6=counter++ (:42) → 9424(1,...,v6) (:43-44) else v6=0 (:49,56) → return v6 (:59). Counter thuần nội bộ (không userInfo/timestamp/random). Callers: 2F754:95 (v33=27C88(); !v33 → restore else maxCPUIWaitGen=v33 + after 2s check :95-106, maximize/re-host chờ echo); 2FC5C:103 (fire-and-forget sau rebuildMat :101-103).
- **H4 ghi** (26FE4:256, tail in-place): callers 208F4 (26FE4:6; đăng ký block 208F4:552). Không check length/count tại site (khác 27C88); guard duy nhất outer 4-đk (:81-87). Counter nội bộ.
- **H3 ghi** (2565C:127, completion split): caller 2410C (site 2410C:715). v11=0/1 đều tăng (:115-128). Counter nội bộ.
- **H2 ghi** (218D8:699, reshow): callers 202D0/217EC. Nhánh else LABEL_37 (:307-313; v28 flag "không cần reshow" từ so bids/geometry/pane-ratio :240-303, HYPOTHESIS ngữ nghĩa reshow). Increment chỉ khi split-hosting + DDz1 chưa visible + geometry ổn + present ok (HYPOTHESIS "reshow").

## 3. Lifecycle
- **Khởi tạo**: không store tường minh → BSS zero → gen đầu phát = 0 (HYPOTHESIS). Reset khi relaunch UNKNOWN (không site reset). Kiểu __int64 post-increment; IPC qua numberWithUnsignedLongLong (9424:92).
- **Tăng**: 4 sites cùng idiom `old = counter++` (27C88, 26FE4, 2565C, 218D8). Không từ userInfo/timestamp. `++` hậu tố ⇒ check v6+1==counter ⟺ v6==lastSent.
- **Consume**: duy nhất 9424(a6=gen) (callers 218D8/2565C/26FE4/27C88 + 1FB5C/9400 truyền 0 cứng — 1FB5C:98-192 chứng tỏ chỉ 4 sites split/CPUI dùng counter). 9424:90-93 (length||count → dict["cpuiGen"]) → :102 post host.state (Darwin).
- **Readers IPC**: 20010:35-36 (status → stale-check) + 9D64:252-253 (v137 → lưu 1636E8 :402,419,440 + 1637A0 :502 + echo 986C "already" :422 + BFF4 :487 + C37C :480). Chiều ngược: 986C pack cpuiGen vào cpui.status (986C:23-54; a1 chính là v137 từ host.state — 9D64:422 + 986C:26).
- **Stale-check duy nhất**: 20010:69 (!ok && incoming+1==counter). Không site nào khác. Pass → dedup + 85B8 retry. Forward lên DDz1 xảy ra trước, độc lập.

## 4. Kết luận 1 dòng (Q-11)
162E60 = monotonic host-side counter (BSS-init HYPOTHESIS 0), 4 post-increments (27C88/26FE4/2565C/218D8) → 9424:a6 → cpuiGen → host.state (9424:92-93,102); đọc tại 20010:35-36 + 9D64:252-253; stale-check duy nhất 20010:69. Toàn bộ CONFIRMED trừ init/reset và tên biến phụ trợ.
