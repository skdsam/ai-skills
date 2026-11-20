---
name: juce-ui-fidelity
description: Build or fix JUCE audio-plugin UI — writing custom LookAndFeel overrides (drawRotarySlider, drawButtonBackground, drawToggleButton, drawComboBox), custom knobs/sliders/toggles/panels, and theme/color wiring — and make them match a visual reference pixel-accurately via a headless screenshot-diff loop. Use when the user is working on a native JUCE (C++) synth or effect UI and wants to match a design (image mockup, Figma/Stitch HTML export, PDF spec), troubleshoot why their editor doesn't look like the mockup, add visual regression / screenshot tests, or iterate between design tools (Stitch, nano-banana, Gemini) and JUCE rendering. Skip for WebBrowserComponent / React-in-JUCE UIs, DSP or parameter-plumbing work.
---

# juce-ui-fidelity

Translate a visual design into native JUCE C++ and prove it matches — by
compiling the code, rendering it headlessly to a PNG, and diffing the PNG
against the design target. The goal is not "approximately right". The goal is a
tight, measurable feedback loop: change a line of `paint()`, see the diff
shrink, repeat until the delta is under the threshold.

The skill has three moving parts:

1. **A headless snapshot harness** bundled in `scripts/` — a ~100-line JUCE
   executable that renders any registered `juce::Component` to a PNG with no
   display, no plugin host, no window. Wired into the project's CMake once;
   stays out of the way after.
2. **A design-capture step** — turn whatever the designer gave you (a Stitch
   HTML export, a reference screenshot, a Figma-linked SVG) into a single PNG
   at the same size the JUCE Component will render at.
3. **A perceptual diff** — `odiff` with anti-alias tolerance, producing a score
   and an overlay PNG that shows exactly which pixels moved.

Everything else is in service of that loop.

## When to reach for this skill

- You have a visual target (image, HTML mockup, Figma frame, PDF spec) and need
  JUCE code that looks like it.
- You are inside a `drawRotarySlider`, `drawButtonBackground`, or similar
  `LookAndFeel` override and want to verify the output objectively.
- You're translating between design-generation tooling (Stitch MCP, nano-banana
  image iteration, web mockups) and native C++ painting.
- A JUCE project is shipping without visual tests and you want to add them
  without adopting a plugin-host-level snapshot system.

Do **not** use this skill for:

- `WebBrowserComponent`-based UIs (HTML/React embedded in JUCE). Different
  workflow — stay in web dev tooling.
- Code-only refactors of UI that don't touch appearance.
- DSP, parameter wiring, or preset work.

## The core loop

```
┌──────────────────────────┐
│ 1. State the objective   │   "Match FilterPanel cutoff-knob to mockup.png"
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 2. Capture target PNG    │   HTML → render_html.py ; image → already PNG
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 3. Write/edit Component  │   follow theme system; no hardcoded colours
│    or LookAndFeel code   │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 4. Register as a story   │   REGISTER_COMPONENT (Name_Variant, []{ ... })
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 5. Build + render        │   cmake --build build --target snapshot
│                          │   ./build/snapshot Name_Variant W H out.png
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 6. Diff                  │   python scripts/diff_images.py target out.png
└────────────┬─────────────┘
             ▼
      ┌──────┴───────┐
      ▼              ▼
  ┌───────┐      ┌─────────┐
  │ Pass  │      │  Fail   │  read diff.png, identify the specific
  │ ship  │      │ iterate │  delta, change one thing, re-render
  └───────┘      └────┬────┘
                      └──→ back to step 3
```

State the objective out loud before writing code. "I'm going to match the
cutoff knob's arc glow and the corner radius of the filter panel card." A
named objective gives the diff a meaning — otherwise you end up chasing
every pink pixel the overlay highlights, including AA noise.

## Once per project: set up the snapshot harness

Most JUCE projects don't yet have this. Set it up the first time you touch a
project with this skill; subsequent work just adds stories.

1. Check whether the project already has a `snapshot` target or a
   `tests/snapshots/` directory. If yes, skip to "Per task".

2. Copy the template files into the project:

   ```sh
   mkdir -p tests/snapshots/{stories,golden,current,diff}
   cp ~/.claude/skills/juce-ui-fidelity/scripts/snapshot_main.cpp \
      tests/snapshots/main.cpp
   cp ~/.claude/skills/juce-ui-fidelity/scripts/run_snapshots.sh \
      tests/snapshots/
   chmod +x tests/snapshots/run_snapshots.sh
   ```

3. Paste the CMake snippet from
   `~/.claude/skills/juce-ui-fidelity/scripts/snapshot_CMakeLists.snippet` into
   the project's `CMakeLists.txt`. Adjust the `target_sources` and
   `target_link_libraries` blocks to match what the plugin already has
   (typically mirror the plugin's binary-data target + `juce_gui_basics`).

4. Add `.gitignore` entries for `tests/snapshots/current/` and
   `tests/snapshots/diff/`. Keep `tests/snapshots/golden/` under git.

5. Install the diff tool once: `brew install odiff` (macOS) or
   `npm i -g odiff-bin`. The driver script falls back to
   `scripts/diff_images.py` (Pillow) if odiff is missing, but odiff is faster
   and AA-aware.

6. Configure + build the harness to confirm it links:
   ```sh
   cmake -B build -G Ninja -DENABLE_SNAPSHOT_TESTS=ON
   cmake --build build --target snapshot
   ./build/snapshot --list    # empty is fine; no stories yet
   ```

Rationale for the design choices:

- **`SoftwareImageType{}`** (in the harness): the default JUCE image uses
  CoreGraphics on macOS, Direct2D on Windows, software on Linux — three
  different rasterizers for the same `paint()` code. Forcing software gives
  cross-platform byte-level reproducibility.
- **`JUCE_DISABLE_COREGRAPHICS_FONT_SMOOTHING=1`**: kills the macOS subpixel-AA
  lottery that otherwise varies by display orientation, Retina factor, and
  point release.
- **`EXCLUDE_FROM_ALL`**: keeps the harness opt-in so it doesn't slow the
  default build. Matches the common pattern of secondary test/tooling targets.

Full background and CI wiring: `references/screenshot-testing.md`.

## Per task: the iteration cycle

Assume the harness is set up. Typical workflow for "reproduce design X in
component Y":

### Step 1 — State the objective and target size

Write it down in the conversation: *"Render MyFilterPanel at 420x240 to match
`mockups/filter-panel.png`."* Agree on a pixel size before coding. Mismatched
sizes mean the diff is never meaningful.

### Step 2 — Capture the target PNG

Pick the right path for the input type:

| Input                           | Tool                                                               |
| ------------------------------- | ------------------------------------------------------------------ |
| PNG/JPG screenshot or render    | Use as-is; if JPG, convert with `sips -s format png`.              |
| HTML/CSS mockup (Stitch/Figma)  | `scripts/render_html.py` (Playwright) — supports selector clipping. |
| Figma frame (SVG export)        | Render SVG to PNG: `rsvg-convert -a -w 420 frame.svg > target.png`. |
| PDF design spec                 | `pdftoppm -png -r 288 spec.pdf target` (288 dpi → 4x).             |
| Generate from scratch           | Invoke Stitch MCP or nano-banana; then treat output as image/HTML.  |

For image-generation flows the skill should drive the MCPs directly:

- **Stitch MCP** (`mcp__stitch__*`): when the design doesn't exist yet, use
  Stitch to generate a starting screen, iterate on it, then export the HTML/CSS
  and rasterize.
- **nano-banana** (`mcp__nano-banana-2__*`): use for focused refinements on an
  existing reference image — "take the knob from this screenshot, give it a
  brighter phosphor ring".
- **Playwright MCP** (`mcp__plugin_playwright_playwright__*`): when the mockup
  is live HTML, the MCP is a faster alternative to `render_html.py` for
  interactive inspection (measuring bounds, reading computed styles).
- **Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`):
  use `evaluate_script` to dump computed styles — borderRadius, box-shadow,
  gradient stops — straight into numbers you can translate to JUCE calls.

### Step 3 — Write or edit the JUCE code

Work inside the project's existing theme system, not in isolation. If the
project has a central `LookAndFeel` subclass with a `ThemeData` (or similar)
struct, add or extend drawing there — do not hardcode colours in `paint()`.
See `references/theme-integration.md`.

For widget implementation patterns (knobs, buttons, toggles, scopes, gradients,
text rendering), consult `references/juce-ui-primitives.md`. It has
code-ready recipes including multi-pass phosphor-bloom strokes, SVG
`Drawable` integration, filmstrip vs. vector trade-offs, and the hi-DPI
rules.

For translating web/CSS constructs (border-radius, box-shadow, gradient, font
metrics) into JUCE Graphics calls: `references/design-translation.md`.

For inspiration about how mature open-source synths structure great UIs (Surge
XT, Vital, Shortcircuit, Dexed, Helm), consult
`references/synth-ui-catalog.md`. Read patterns, do not copy GPL code into a
non-GPL plugin.

### Step 4 — Register a story

Create a stories TU next to the component:

```cpp
// tests/snapshots/stories/FilterPanel_stories.cpp
#include "source/ui/FilterPanel.h"

// Default view — matches the Figma mockup at 420x240.
REGISTER_COMPONENT_SIZED (FilterPanel_Default, []{
    auto c = std::make_unique<FilterPanel>();
    c->setCutoff (0.62f);
    c->setResonance (0.35f);
    return c;
}, 420, 240);

// Edge case — ensure the arc bloom doesn't bleed at full cutoff.
REGISTER_COMPONENT_SIZED (FilterPanel_MaxCutoff, []{
    auto c = std::make_unique<FilterPanel>();
    c->setCutoff (1.0f);
    c->setResonance (0.85f);
    return c;
}, 420, 240);
```

Add the story file to the `target_sources` list in the CMake snippet.

### Step 5 — Build and render

```sh
cmake --build build --target snapshot
./build/snapshot FilterPanel_Default 420 240 \
    tests/snapshots/current/FilterPanel_Default.png
```

If the build is slow (>15s for a one-file edit), check that ccache is wired
(`CMAKE_CXX_COMPILER_LAUNCHER=ccache`), the generator is Ninja, and the
harness has a PCH. `references/screenshot-testing.md §7` has the tuning
ladder.

### Step 6 — Diff

```sh
python ~/.claude/skills/juce-ui-fidelity/scripts/diff_images.py \
    mockups/filter-panel.png \
    tests/snapshots/current/FilterPanel_Default.png \
    --out tests/snapshots/diff/FilterPanel_Default \
    --threshold 0.01
```

Or from inside the project, just `./tests/snapshots/run_snapshots.sh` which
runs every registered story, generates diffs, and exits non-zero if any
exceed threshold. Inspect `diff.png` and `report.json`.

### Step 7 — Iterate on the specific delta

Do not change five things at once. The diff overlay localises the problem —
pink pixels show where. Pick one (the corner radius, the arc colour, the
shadow spread), change it, re-render, watch the diff shrink. If the diff
grows, you changed the wrong knob; revert immediately.

### Step 8 — Accept the golden

When the diff is under threshold and the visual objective is satisfied:

```sh
cp tests/snapshots/current/FilterPanel_Default.png \
   tests/snapshots/golden/FilterPanel_Default.png
```

Commit both the code and the golden PNG together. Future changes to
`FilterPanel` will diff against this golden, catching accidental regressions.

## Writing custom LookAndFeel code — essentials

Full recipes in `references/juce-ui-primitives.md`. The high-leverage rules:

- **Subclass `juce::LookAndFeel_V4`**, not earlier versions. It's the modern
  baseline for Slider / Button / ComboBox / PopupMenu defaults.
- **Push colours through colour IDs** (`Slider::rotarySliderFillColourId`,
  `TextButton::buttonColourId`, etc.) rather than hardcoding in `paint()`. This
  keeps theme data authoritative and makes swapping palettes free.
- **Force your bundled typeface** by overriding `getTypefaceForFont()` to
  return the loaded face unconditionally. Otherwise certain FontOptions flags
  silently fall back to platform defaults and your labels drift.
- **Vector over filmstrip** for knobs in modern synth UIs. Filmstrips are
  pixel-perfect at one size but can't re-skin; `drawRotarySlider` with
  `Path::addCentredArc` + multi-pass glow strokes is resolution-independent
  and theme-aware.
- **Multi-pass phosphor glow**: stack 3–4 `strokePath` passes with
  decreasing width + increasing alpha to fake a bloom. Cheap and readable;
  matches the "neon halo" look modern synths converge on.
- **`Graphics::setGradientFill(ColourGradient)`** handles linear and radial
  gradients. For vignette / dome lighting on knob bodies, stack several
  radial gradients (light from above, dark on rim) to build a cylinder look
  without resorting to bitmaps.
- **Recompute layout in `resized()` from `getLocalBounds()`** — never cache
  pixel positions. FlexBox for knob strips, Grid for 2D panels.
- **Semantically-fixed colours** (red meter, amber warning, cyan LED) still
  don't belong as raw hex in `paint()`. Put them on a small co-located
  struct (e.g. `MeterColours { Colour high, mid, low; }`) exposed as a
  setter on the Component. Keeps intent legible and lets themes override
  if they want. See `references/theme-integration.md §8`.

## Translating design inputs — quick rules

Detail in `references/design-translation.md`. Mental map:

| CSS / design term          | JUCE equivalent                                                   |
| -------------------------- | ----------------------------------------------------------------- |
| `border-radius: 8px`        | `drawRoundedRectangle (bounds, 8.0f, lineThickness)`              |
| `box-shadow: 0 4px 12px …`  | `melatonin_blur` if available, else multi-pass `strokePath`       |
| `linear-gradient(...)`      | `ColourGradient` with `addColour(stopProportion, colour)`         |
| `background: radial-...`    | `ColourGradient(..., isRadial=true)`                              |
| `font-family: 'Foo'`         | Bundle TTF via `juce_add_binary_data` + `Typeface::createSystemTypefaceFor` |
| `padding: 12px 16px`         | `bounds.reduced(16, 12)`                                          |
| `opacity: 0.6`               | `Colour::withAlpha(0.6f)` on the stroke/fill                      |
| `filter: blur(4px)`          | `melatonin_blur` (no native equivalent; workaround: stacked strokes) |

## When the diff stays high — troubleshooting

- **Shape is right, colours are off**: you're ignoring the theme. Check
  whether the component uses `theme.colors.*` / colour IDs or hardcodes.
- **Colours match, stroke position is off by 1 pixel**: AA / subpixel issue.
  Offset integer bounds by `0.5f` before `drawRect` / `drawRoundedRectangle`.
- **Text looks "softer" than the target**: the mockup was rendered by
  CoreText/DirectWrite/FreeType, JUCE uses its own rasteriser plus the
  platform font engine. If you must byte-match text, bundle the exact TTF
  and force `getTypefaceForFont`. Otherwise accept small text delta and
  lower the threshold for text regions only.
- **Entire snapshot is black**: the Component probably scheduled async layout
  in its constructor. Add a longer `runDispatchLoopUntil` before rasterizing,
  or call `resized()` explicitly on the test instance.
- **Diff image shows a halo around every shape**: AA mismatch between the
  design PNG (rendered at higher DPR) and the JUCE PNG (rendered at 1x).
  Re-render with `--dpr 2` in `render_html.py`, and call the harness with
  the doubled size: `./snapshot Name W*2 H*2`.

## Project conventions to respect

Always check for a project-level `CLAUDE.md` / `AGENTS.md` / style guide — its
rules override skill defaults. Commonly applicable conventions to watch for:

- **ASCII-only C++ string literals.** Em-dashes, arrows, emoji break the font
  pipeline on some compiler/platform combinations. Use `-`, `->`, or wrap
  non-ASCII in `juce::String::fromUTF8(u8"...")`.
- **UI naming conventions**: projects often have domain-specific label
  conventions (e.g. `VCO`/`VCF` vs `OSC`/`Filter`). Check the project's style
  guide before renaming anything the user sees.
- **Never `git commit` without explicit instruction.** Make the edit, build to
  verify, and stop. Golden PNGs + code change together in the same commit
  the user requests.
- **Update `CHANGELOG.md`** for user-visible visual changes before the commit
  (Keep-a-Changelog format, under `## [Unreleased]`).
- **GPL references are for patterns, not code.** Surge XT, Vital, Dexed, Helm
  are instructive but GPL-3.0 — do not transcribe their source into a non-GPL
  plugin. See `references/synth-ui-catalog.md` for the permissive-licensed
  alternatives (`sst-jucegui`, `melatonin_blur`, `foleys_gui_magic`).

## Study library (pointers)

When in doubt about a pattern, look at how a mature synth solved the same
problem. `references/synth-ui-catalog.md` has the detailed analysis; the
cheat-sheet:

- **Shortcircuit XT / sst-jucegui** (MIT) — cleanest modern "stylesheet"
  architecture; copy-friendly.
- **Surge XT** (GPL-3.0) — XML-skin + SVG assets + CRTP widget base. Study the
  theming pipeline; don't lift code.
- **Dexed** (GPL-3.0) — canonical PNG-filmstrip + `LookAndFeel_V4` hardware
  emulation. Good reference for "rendered from hardware photos" aesthetic.
- **Vital** (GPL-3.0) — OpenGL shaders per widget + JSON skin. Reference for
  "what does a shader-accelerated modulation UI look like" — not needed unless
  you're attacking 60fps modulation visualisation.
- **melatonin_inspector + melatonin_blur** (both MIT) — pair these with the
  snapshot harness for dev-loop quality. Inspector = Chrome DevTools for
  JUCE; blur = the de-facto soft-shadow primitive.

## Reference files (progressive disclosure)

Detail lives in:

- `references/juce-ui-primitives.md` — Graphics API, knob/button/toggle
  patterns, custom LookAndFeel overrides, asset pipeline, hi-DPI, fonts,
  animation, layout, cross-platform pitfalls.
- `references/screenshot-testing.md` — The full screenshot workflow: headless
  rendering internals, platform specifics for macOS/Linux/Windows, odiff +
  alternatives, CI wiring, fast-iteration tricks, prior art in the JUCE
  ecosystem.
- `references/synth-ui-catalog.md` — Catalog of open-source JUCE synths
  ranked by UI-craft instructiveness, with license + rendering approach per
  project.
- `references/design-translation.md` — Mapping from web/CSS/Figma constructs
  to JUCE `Graphics` calls, with worked examples.
- `references/theme-integration.md` — How to integrate a new Component into
  an existing ThemeData + LookAndFeel system without introducing ad-hoc
  colour state.

## Scripts bundled

- `scripts/snapshot_main.cpp` — the harness executable, drop into project.
- `scripts/snapshot_CMakeLists.snippet` — CMake wiring template.
- `scripts/run_snapshots.sh` — driver that renders every story + diffs.
- `scripts/diff_images.py` — odiff wrapper with Pillow fallback.
- `scripts/render_html.py` — Playwright-based HTML/CSS → PNG with selector
  clipping and configurable DPR.
