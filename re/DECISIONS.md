# DECISIONS.md
- D-001: Dùng cấu trúc `re/` theo ROLE thay vì tạo duplicate (repo chưa có). Session-001.
- D-002: Static-first, không suy behavior từ tên hàm; mọi kết luận gắn CONFIRMED/HIGH/HYPOTHESIS/UNKNOWN.
- D-003: Không reconstruct code vội; khóa hook/prefs/IPC maps trước (P0/P1 trước P2).
- D-004: Mọi code tương lai gắn APPROXIMATION + giữ timing/queue/retain semantics gốc.
- D-005: 3 subagents song song cho entry/hooks, prefs/IPC/network, apps/prefs (tránh context overflow 4018 funcs).
- D-006: Chưa init git (ngoài scope session-001, để P4-1).
