#!/usr/bin/env python3
"""diff_images.py - Compare two PNGs for JUCE UI fidelity testing.

Wraps odiff (SIMD-fast, anti-alias-aware, the right default) and falls back
to a pure-Python PIL+NumPy pixel compare if odiff is not on PATH. Emits a
JSON report plus a diff overlay PNG; exit code 0 when the diff score is
below the tolerance, 1 when above.

Install odiff once (recommended):
    brew install odiff        # macOS
    npm i -g odiff-bin        # cross-platform

Usage:
    diff_images.py TARGET ACTUAL [--out DIR] [--threshold 0.01]
                                 [--no-antialiasing]

The threshold is the fraction of changed pixels the diff tolerates (odiff's
"diffThreshold" maps 1:1). 0.01 = 1 percent, a sensible default for UI work
once AA matching is enabled.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run_odiff(target: Path, actual: Path, out_png: Path,
              threshold: float, antialiasing: bool) -> dict:
    """Invoke odiff and parse its JSON output."""
    cmd = [
        "odiff",
        str(target), str(actual), str(out_png),
        "--threshold", str(threshold),
        "--output-diff-mask",
        "--parsable-stdout",
    ]
    if antialiasing:
        cmd.append("--antialiasing")

    result = subprocess.run(cmd, capture_output=True, text=True)
    # odiff exit codes: 0 match, 21 layout mismatch, 22 pixel mismatch
    match = result.returncode == 0
    # stdout when --parsable-stdout is a single number: the diff pixel count
    try:
        diff_pixels = int(result.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        diff_pixels = -1

    return {
        "backend": "odiff",
        "match": match,
        "diff_pixels": diff_pixels,
        "stderr": result.stderr.strip() or None,
        "exit_code": result.returncode,
    }


def run_pillow_fallback(target: Path, actual: Path, out_png: Path,
                        threshold: float) -> dict:
    """Pure-Python fallback. Not AA-aware - use only when odiff is missing.

    Compares pixels above a small per-channel delta to filter trivial noise,
    then writes a red-highlighted overlay.
    """
    try:
        from PIL import Image, ImageChops
        import numpy as np
    except ImportError as e:
        return {
            "backend": "none",
            "error": (
                "odiff not found and Pillow/numpy not installed. Install"
                " one: `brew install odiff` or `pip install pillow numpy`."
            ),
            "missing": str(e),
            "match": False,
        }

    a = Image.open(target).convert("RGBA")
    b = Image.open(actual).convert("RGBA")
    if a.size != b.size:
        return {
            "backend": "pillow",
            "match": False,
            "error": f"size mismatch target={a.size} actual={b.size}",
        }

    # Per-pixel max-channel delta; count pixels that exceed 8/255 (dodges
    # trivial AA fringing without being generous about real changes).
    arr_a = np.asarray(a, dtype=np.int16)
    arr_b = np.asarray(b, dtype=np.int16)
    delta = np.abs(arr_a - arr_b).max(axis=-1)
    changed = delta > 8
    diff_pixels = int(changed.sum())
    total = int(changed.size)
    ratio = diff_pixels / total if total else 0.0

    overlay = np.asarray(b, dtype=np.uint8).copy()
    overlay[changed] = [255, 0, 0, 255]
    Image.fromarray(overlay, "RGBA").save(out_png)

    return {
        "backend": "pillow",
        "match": ratio <= threshold,
        "diff_pixels": diff_pixels,
        "total_pixels": total,
        "diff_ratio": ratio,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", type=Path, help="reference PNG (design)")
    ap.add_argument("actual", type=Path, help="rendered PNG (JUCE output)")
    ap.add_argument("--out", type=Path, default=Path("diff"),
                    help="directory for diff.png + report.json (default: diff/)")
    ap.add_argument("--threshold", type=float, default=0.01,
                    help="max fraction of changed pixels tolerated (default 0.01)")
    ap.add_argument("--no-antialiasing", dest="antialiasing",
                    action="store_false",
                    help="disable odiff's AA tolerance (rarely useful)")
    args = ap.parse_args()

    if not args.target.exists():
        print(f"target not found: {args.target}", file=sys.stderr)
        return 2
    if not args.actual.exists():
        print(f"actual not found: {args.actual}", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    diff_png = args.out / "diff.png"
    report_json = args.out / "report.json"

    if shutil.which("odiff"):
        report = run_odiff(args.target, args.actual, diff_png,
                           args.threshold, args.antialiasing)
    else:
        print("warning: odiff not on PATH, using Pillow fallback",
              file=sys.stderr)
        report = run_pillow_fallback(args.target, args.actual, diff_png,
                                     args.threshold)

    report["target"] = str(args.target)
    report["actual"] = str(args.actual)
    report["diff_png"] = str(diff_png)
    report["threshold"] = args.threshold

    report_json.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

    return 0 if report.get("match") else 1


if __name__ == "__main__":
    sys.exit(main())
