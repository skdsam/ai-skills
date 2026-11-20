# juce-ui-fidelity

A Claude Code skill for building and verifying JUCE audio-plugin UI against a
visual reference — pixel-accurately, via a headless screenshot-diff loop.

Use this when you are writing custom `LookAndFeel` overrides
(`drawRotarySlider`, `drawButtonBackground`, `drawToggleButton`,
`drawComboBox`), custom knobs/sliders/toggles/panels, and theme/color wiring,
and you want the rendered JUCE `Component` to match a design (image mockup,
Figma/Stitch HTML export, PDF spec).

Skip it for `WebBrowserComponent` / React-in-JUCE UIs and for DSP or
parameter-plumbing work.

## What the skill gives you

- **A headless snapshot harness** — a ~100-line JUCE executable that renders any
  registered `juce::Component` to a PNG with no display, no plugin host, no
  window. Drop it into your CMake once; stays out of the way after.
- **A design-capture step** — scripts to turn a Stitch HTML export, a reference
  screenshot, or a Figma-linked SVG into a PNG at the same size the JUCE
  Component will render at.
- **A perceptual diff** — `odiff` with anti-alias tolerance, producing a score
  and an overlay PNG that shows exactly which pixels moved.
- **Reference material** — patterns for knobs, multi-pass phosphor glow,
  gradient-based body lighting, filmstrip-vs-vector trade-offs, hi-DPI, fonts,
  CSS-to-Graphics translation, and how to integrate into an existing theme
  system without introducing ad-hoc color state.

## Install

Clone into your Claude Code skills directory:

```sh
git clone https://github.com/mcaserta/juce-ui-fidelity.git \
    ~/.claude/skills/juce-ui-fidelity
```

Then install the diff tool (one-time):

```sh
brew install odiff          # macOS
# or:
npm i -g odiff-bin          # any platform
```

The bundled `scripts/diff_images.py` Pillow fallback runs if `odiff` isn't
available, but `odiff` is faster and AA-aware.

For HTML mockup rasterisation:

```sh
pip install playwright && playwright install chromium
```

## Use

Start Claude Code in a JUCE plugin repo and ask for UI work tied to a visual
reference ("match this mockup", "translate this Figma frame", "add visual
regression tests for FilterPanel"). The skill activates automatically on
relevant tasks.

For manual use of individual pieces:

- `scripts/snapshot_main.cpp` — drop into `tests/snapshots/main.cpp` in your
  project.
- `scripts/snapshot_CMakeLists.snippet` — paste into your `CMakeLists.txt`.
- `scripts/run_snapshots.sh` — driver that renders every story + diffs.
- `scripts/render_html.py` — HTML/CSS → PNG via Playwright.
- `scripts/diff_images.py` — `odiff` wrapper with Pillow fallback.

See `SKILL.md` for the full workflow and `references/` for deep-dive material.

## Layout

```
SKILL.md                    entry point; loaded by Claude Code
scripts/                    snapshot harness + diff/render tooling
references/
  screenshot-testing.md     headless rendering internals, CI wiring
  juce-ui-primitives.md     Graphics API recipes (knobs, buttons, glow)
  design-translation.md     CSS/Figma -> juce::Graphics call mapping
  theme-integration.md      plugging into existing LookAndFeel/ThemeData
  synth-ui-catalog.md       open-source synth study library
evals/                      skill evaluation fixtures
```

## License

MIT. See `LICENSE`.
