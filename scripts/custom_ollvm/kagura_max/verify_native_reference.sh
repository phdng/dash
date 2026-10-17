#!/usr/bin/env bash
# Compare compiled native C KaguraLab harness to independent Python oracle.
# The host binary is NEVER treated as physical iPhone Kagura execution.
set -euo pipefail
out="$1"
dir="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$out"
for variant in plain protected; do
  xcrun clang -O1 -std=c11 -Wall -Wextra -Werror \
    -DDD_KAGURA_ENTRY=dd_kagura_"$variant" \
    -c "$dir/critical.c" -o "$out/reference-$variant.o"
done
xcrun clang -O1 -std=c11 -Wall -Wextra -Werror \
  "$dir/ios_canary.c" "$dir/ios_reference_host.c" \
  "$out/reference-plain.o" "$out/reference-protected.o" \
  -o "$out/reference-host"
"$out/reference-host" > "$out/host-reference.log"
python3 "$dir/ios_reference.py" \
  --check-host "$out/host-reference.log" \
  --out "$out/KaguraLab-runtime-reference.json"
echo "KAGURA_HOST_C_REFERENCE_PASS: native C checksums match independent oracle; NOT iPhone"
