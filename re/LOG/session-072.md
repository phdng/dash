# LOG/session-072.md
_Date: 2026-10-06. Objective: continue after session-071 GitHub Actions build GREEN; promote the next private-framework-free runtime slices._

## R-061 — sub_7764C liveness probe
Directly re-read 7764C.c + callers 25C4C/25FE0/26FE4 + gate 771D4.

Promoted `DDCountLiveSnapshotEntries` into ReconstructionRuntime:
- exact SpringBoard gate uses `[NSBundle mainBundle].bundleIdentifier == com.apple.springboard` (771D4), not executable suffix inference;
- accepts snapshot entries shaped `{pid:NSNumber,path:NSString,bid:*}`;
- nil/empty filter matches all; non-empty filter requires NSString bid equality;
- pid < 2 skipped;
- `proc_pidpath(pid, 4096)` + exact `strcmp` against stored path; matching entries increment counter;
- outside SpringBoard returns lower-32-bit sentinel `0xFFFFFFFF` (`UINT32_MAX`), preserving known callers' unsigned-int/truthy behavior;
- read-only: no kill, prefs, unhost, view or private SpringBoard objects.

Build target now links `libproc` via `DuoDashReconstruction_LIBRARIES = proc`. The runtime keeps a local `proc_pidpath` declaration instead of requiring extra headers.

## R-062 — sub_7E63C / sub_7EEDC
Directly re-read 7E63C.c, 7EEDC.c and 7E908.c.

Promoted:
- `DDValidateIntegerValue` with exact status model:
  - 0 missing => fallback;
  - 1 integer CFNumber within inclusive range;
  - 2 NSString coerced with integerValue within range;
  - 3 float NSNumber, non-CFNumber NSNumber/other type, or out-of-range => fallback.
- `DDNormalizeIntegerSetting` mirrors 7EEDC: statuses 2/3 write NSNumber canonical value to `writes[key]` and append `fixName`; statuses 0/1 do not self-heal.

Did NOT wire these helpers into the full 7E908 resolver yet. Some decompiled 7E908/73E8/80D0 numeric bounds/default arguments remain elided; guessing them would reduce reconstruction fidelity.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- Session-071 GitHub Actions build was GREEN per user. Session-072 libproc/Objective-C edits require the next pushed macOS CI compiler run.

## Next
R-063: after CI green, read 73E8/80D0/8154/81EC directly and promote only numeric cache-reader wrappers whose min/max/default arguments are recoverable. Keep decompiler-elided bounds UNKNOWN rather than guessing.
