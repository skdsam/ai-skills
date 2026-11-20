#!/usr/bin/env python3
"""render_html.py - Rasterize an HTML/CSS design mockup to a PNG target.

The point: when the design input is a Stitch/Figma HTML export, an HTML/CSS
mockup, or any web-native source, we need a single PNG to diff against the
JUCE snapshot output. This script produces that PNG reliably, at a chosen
size + device pixel ratio, clipped to a specific selector if wanted.

Preferred: Playwright (`pip install playwright && playwright install chromium`).
Falls back to wkhtmltoimage if available and Playwright is not installed.

Usage:
    render_html.py INPUT --out target.png [--size 400x300] [--dpr 2]
                                          [--selector '#knob-container']
                                          [--viewport 1440x900]
                                          [--wait-for 'load|domcontentloaded|networkidle']

INPUT can be a file path or http(s) URL.

`--size` is the rendered area. When combined with `--selector`, the selector's
bounding box is captured at its natural size and `--size` is informational.
Without a selector, the page is viewport-sized and clipped to `--size`.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def parse_wh(text: str, arg_name: str) -> tuple[int, int]:
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except Exception as e:
        raise SystemExit(f"{arg_name} must be WxH (e.g. 400x300): {e}")


def resolve_input(src: str) -> str:
    """Turn a local path into a file:// URL Playwright can load."""
    if src.startswith(("http://", "https://", "file://")):
        return src
    p = Path(src).resolve()
    if not p.exists():
        raise SystemExit(f"input not found: {src}")
    return p.as_uri()


def render_with_playwright(url: str, out: Path, size: tuple[int, int],
                           viewport: tuple[int, int], dpr: float,
                           selector: str | None,
                           wait_for: str) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "Playwright not installed. Install once:\n"
            "  pip install playwright && playwright install chromium\n"
            "Or use --fallback-wkhtml if wkhtmltoimage is available.")

    vp_w, vp_h = viewport
    out_w, out_h = size

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": vp_w, "height": vp_h},
            device_scale_factor=dpr)
        page = context.new_page()
        page.goto(url, wait_until=wait_for)

        if selector:
            el = page.locator(selector).first
            el.wait_for(state="visible")
            el.screenshot(path=str(out))
        else:
            page.screenshot(path=str(out),
                            clip={"x": 0, "y": 0, "width": out_w, "height": out_h})

        browser.close()


def render_with_wkhtml(url: str, out: Path, size: tuple[int, int],
                       dpr: float) -> None:
    if not shutil.which("wkhtmltoimage"):
        raise SystemExit(
            "Neither Playwright nor wkhtmltoimage available. "
            "Install one:\n"
            "  pip install playwright && playwright install chromium\n"
            "  brew install wkhtmltopdf")
    w, h = size
    cmd = [
        "wkhtmltoimage",
        "--width", str(int(w * dpr)),
        "--height", str(int(h * dpr)),
        "--format", "png",
        url, str(out),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", help="HTML file path or http(s) URL")
    ap.add_argument("--out", type=Path, required=True,
                    help="output PNG path")
    ap.add_argument("--size", default="400x300",
                    help="rendered target size (WxH, default 400x300)")
    ap.add_argument("--viewport", default="1440x900",
                    help="browser viewport for layout (WxH, default 1440x900)")
    ap.add_argument("--dpr", type=float, default=2.0,
                    help="device pixel ratio (default 2.0 — matches Retina)")
    ap.add_argument("--selector",
                    help="CSS selector to clip to (recommended for mockups)")
    ap.add_argument("--wait-for",
                    choices=["load", "domcontentloaded", "networkidle"],
                    default="networkidle",
                    help="page load event to wait for (default networkidle)")
    ap.add_argument("--fallback-wkhtml", action="store_true",
                    help="use wkhtmltoimage instead of Playwright")
    args = ap.parse_args()

    size = parse_wh(args.size, "--size")
    viewport = parse_wh(args.viewport, "--viewport")
    url = resolve_input(args.input)

    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.fallback_wkhtml:
        render_with_wkhtml(url, args.out, size, args.dpr)
    else:
        render_with_playwright(url, args.out, size, viewport,
                               args.dpr, args.selector, args.wait_for)

    print(json.dumps({
        "out": str(args.out),
        "size": list(size),
        "dpr": args.dpr,
        "selector": args.selector,
        "source": url,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
