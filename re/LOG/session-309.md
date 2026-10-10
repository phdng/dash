# Session-309 — DDRoleName duplicate linker symbol

Theos arm64 linker reported `_DDRoleName` twice, from `ReconstructionRuntime.m` and `InitRoleHelpers.m`. The runtime version returned generic labels, while the latter preserves the evidence-backed AC7A4 role labels (`bridge`, `prefsrefresh`, etc.). Removed the redundant runtime implementation and redundant `ReconstructionRuntime.h` declaration, preserving the canonical `DuoDashShared.h` declaration and `InitRoleHelpers.m` implementation. No linker warning suppression.

Added regression guard checking canonical definition and forbidding the runtime duplicate. PASS: reconstruction verification, Python py_compile, git diff --check (LF/CRLF warning only). Exact Theos arm64 link must be confirmed by CI. No push.
