# LOG/session-197.md
_Date: 2026-10-08. Objective: promote bounded exact Foundation migration helpers without enabling unresolved static-table migration phases, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 9851250.
- Working tree clean; branch ahead 12.

## Exact helpers
85800:
- compose source `/var/mobile/Library/TrueDash/<name>`;
- if source absent, return false;
- compose destination `/var/mobile/Library/DuoDash/<name>`;
- remove destination ignoring error;
- copy source to destination and return copy result;
- does not create directories and does not delete source.

8597C:
- non-NSArray -> nil;
- array -> NSMutableOrderedSet;
- keep only NSString with length > 0;
- deduplicate while preserving first occurrence order;
- return ordered-set array.

85B14/85BCC:
- non-NSDictionary -> nil;
- dictionary -> mutable dictionary;
- keep only entries whose key and value are both NSString;
- no non-empty requirement.

85D30:
- count > 0 -> componentsJoinedByString:@",";
- zero count (including nil receiver semantics) -> `none`.

## Executable promotion
Added:
- DDMigrateTrueDashFileNamed
- DDMigrationUniqueNonemptyStrings
- DDMigrationStringDictionary
- DDMigrationJoinOrNone

Defaults bootstrap now reuses DDMigrationJoinOrNone.
All unresolved migration phases remain inside #if 0.

## Next
After compiler green, only decode/promote static migration tables if their raw object boundaries and all entries can be proven exactly; otherwise move to another subsystem.