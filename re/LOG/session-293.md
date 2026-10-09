# LOG/session-293.md
_Date: 2026-10-09. Objective: continue respring reconstruction with the exact pure final execution-path selector embedded in 8097C while excluding worker acquisition, dispatch machinery and execution bodies._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD abb8b54.
- Working tree clean; branch ahead 108.

## Evidence
Near the end of `sub_8097C`:
- result of `sub_811B0()` is cast to int;
- values `< 1` call `sub_81624` directly;
- values `>= 1` construct the `sub_812F4` block and dispatch through the `sub_81304` queue / `sub_81344` wrapper path.

## Executable promotion
Added `DDRespringUsesDirectExecutionForWorkerCount(workerCount)` to compiled `Respring.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `sub_811B0` acquisition, Objective-C block retention/release, queue acquisition, dispatch, `sub_81624`, `sub_812F4`, `sub_81304`, `sub_81344`, or other respring execution side effects are enabled.
