# LOG/session-202.md
_Date: 2026-10-08. Objective: recover exact import-success record counter mapping from raw ARM64 and promote only the final record/write boundary, leaving license status derivation external._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 2823dab.
- Working tree clean; branch ahead 17.

## Raw final-record mapping
At 0x5D78..0x5DE8:
- settings migration BOOL is loaded from sp+0x98;
- settings counter[0] at sp+0x360 is selected to zero when that BOOL is false;
- settings counters[1..2] are loaded as q0 from sp+0x368/sp+0x370;
- settings counter[3] is loaded from sp+0x378 without BOOL gating;
- rescuer counters[0] and [1] are loaded from sp+0x2D0/sp+0x2D8 and added;
- the rescuer sum is selected to zero when rescuer migration BOOL at sp+0x94 is false.

Therefore final record fields are:
- settings = settingsCounters[0] iff settingsMigrated else 0;
- renamed = settingsCounters[1];
- dropped = settingsCounters[2];
- removed = settingsCounters[3];
- rescuer = rescuerCounters[0] + rescuerCounters[1] iff rescuerMigrated else 0.

## Executable boundary
Added `DDFinalizeTrueDashImportRecord(...)`.
It accepts already-resolved licence/blob/key/old_key/undo strings rather than reconstructing license/device-ID branches.
It writes the exact `at=<ms> result=ok ...` record through the existing newline+atomic UTF-8 helper.
`import.running` is removed only after `import.done` write succeeds.

## Boundary
No licence/blob/key/old_key/undo derivation is implemented in this batch.

## Next
After compiler green, continue with a license-independent migration helper or another bounded executable subsystem.