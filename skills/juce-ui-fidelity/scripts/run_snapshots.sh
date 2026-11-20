#!/usr/bin/env bash
# run_snapshots.sh — render every registered story and diff against goldens.
#
# Usage (from a plugin repo that wired up the snapshot harness):
#   ./run_snapshots.sh [path/to/snapshot_binary] [tests/snapshots]
#
# Defaults assume the Pamplejuce-ish layout:
#   build/snapshot
#   tests/snapshots/{golden,current,diff}/
#
# Exit 0 when every story passes (or is marked "new"), non-zero otherwise.
# Failed stories leave their diff PNGs in $SNAP_ROOT/diff/ for review.

set -euo pipefail

HARNESS=${1:-build/snapshot}
SNAP_ROOT=${2:-tests/snapshots}

if [[ ! -x "$HARNESS" ]]; then
    echo "harness not found / not executable: $HARNESS" >&2
    echo "build it first: cmake --build build --target snapshot" >&2
    exit 2
fi

if ! command -v odiff >/dev/null; then
    echo "warning: odiff not on PATH, falling back to scripts/diff_images.py" >&2
    echo "  install once: brew install odiff  OR  npm i -g odiff-bin" >&2
fi

GOLDEN="$SNAP_ROOT/golden"
CURRENT="$SNAP_ROOT/current"
DIFF="$SNAP_ROOT/diff"
mkdir -p "$GOLDEN" "$CURRENT" "$DIFF"

# Discover stories by asking the binary. Format: name|w|h.
mapfile -t stories < <("$HARNESS" --list)

if [[ ${#stories[@]} -eq 0 ]]; then
    echo "no stories registered — add REGISTER_COMPONENT calls and rebuild" >&2
    exit 2
fi

fail=0
new=0
pass=0
for story in "${stories[@]}"; do
    IFS='|' read -r name w h <<< "$story"
    : "${w:=400}"; : "${h:=300}"
    out="$CURRENT/$name.png"
    gold="$GOLDEN/$name.png"
    diff="$DIFF/$name.png"

    "$HARNESS" "$name" "$w" "$h" "$out" >/dev/null

    if [[ ! -f "$gold" ]]; then
        echo "[new]  $name  (inspect $out, then: cp $out $gold)"
        new=$((new+1))
        continue
    fi

    if command -v odiff >/dev/null; then
        if odiff --antialiasing --threshold 0.05 \
                 --diff-color "#ff00ff" \
                 "$gold" "$out" "$diff" >/dev/null 2>&1; then
            echo "[pass] $name"
            pass=$((pass+1))
        else
            echo "[FAIL] $name  diff -> $diff"
            fail=$((fail+1))
        fi
    else
        # Fallback uses the Python diff bundled with this skill.
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if python3 "$SCRIPT_DIR/diff_images.py" \
                "$gold" "$out" --out "$DIFF/$name" >/dev/null; then
            echo "[pass] $name"
            pass=$((pass+1))
        else
            echo "[FAIL] $name  diff -> $DIFF/$name/diff.png"
            fail=$((fail+1))
        fi
    fi
done

echo
echo "summary: $pass pass, $fail fail, $new new"
exit $fail
