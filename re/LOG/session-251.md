# LOG/session-251.md
_Date: 2026-10-09. Objective: reconcile session-250's unresolved-suffix assumption against static F-012 and promote the exact AC5FC supplied-path role classifier without enabling path acquisition/cache state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 31d1364.
- Working tree clean; branch ahead 66.

## Evidence reconciliation
Session-250 treated the five AC5FC suffix constants as unresolved because the decompile omitted AC738's second arguments. Static evidence already resolved them in F-012 (`re/FINDINGS.md`, session-002), and `re/TODO.md`/`re/OPEN_QUESTIONS.md` mark that question closed.

## Exact F-012 suffix chain
- `/SpringBoard.app/SpringBoard` -> role 1.
- `/Preferences.app/Preferences` -> role 2.
- `/CarPlay.app/CarPlay` -> role 3.
- `/mediaserverd` -> role 4.
- `/TextInput/kbd` -> role 6.
- no match -> role 5.
- `backboardd` exists elsewhere in strings/evidence but is not part of AC5FC's chain.

## Executable promotion
Added `DDRoleForExecutablePathCString(path)` to compiled `InitRoleHelpers.m`. It uses the exact AC738 suffix predicate and exact F-012 order/constants.

## Boundary
This helper classifies a caller-supplied C path only. It does not call `_NSGetExecutablePath`, read/write `byte_165504` or `dword_165500`, model acquisition failure/cache behavior, or enable AC7A4 latch/filesystem/notify/arming/global state.
