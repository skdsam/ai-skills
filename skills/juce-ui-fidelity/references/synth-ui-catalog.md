# Open-Source JUCE Synth UIs: Reference Catalog for Pixel-Perfect Replication

Research compiled 2026-04-18. Purpose: build a reference catalog for a skill
that teaches Claude to replicate great synth UIs in JUCE native C++.

All metadata (stars, license) taken live from GitHub via `gh api`. Screenshots
live in each repo's README unless noted; "canonical" means the image a new
contributor would first see.

---

## 1. Top 5 Most Instructive Examples

These five cover the full spectrum of how serious JUCE synth UIs are built.

### 1.1 Vital — `mtytel/vital`

- **URL**: https://github.com/mtytel/vital
- **License**: GPL-3.0 (last open-source snapshot before source-available move;
  repo has not been updated in ~4 years)
- **Screenshots**: README references https://vital.audio — product-shot style,
  the synth is famous for the fluid wavetable 3D viewer and animated
  modulations.
- **UI rendering**: Hybrid JUCE + **heavy OpenGL**. Almost every visible
  control (knobs, sliders, meters, filter responses, oscilloscope, wavetable
  viewer) is drawn by custom **GLSL shaders**. The entire rendering layer is
  organized around `OpenGlComponent` (base class) and a `Shaders` registry.
- **LookAndFeel strategy**: `DefaultLookAndFeel : public LookAndFeel_V4`
  provides popup menu/scrollbar theming; everything else is
  `OpenGlComponent` subclasses that bypass `Graphics&` entirely. There are
  three LookAndFeels: default (chrome), `TextLookAndFeel` (text-only knobs),
  `CurveLookAndFeel` (curve editors).
- **Notable widgets**:
  - `OpenGlSlider` + `OpenGlSliderQuad` — shader-based rotary/linear/bar
    sliders (`kRotarySliderFragment`, `kHorizontalSliderFragment`,
    `kVerticalSliderFragment`)
  - Per-filter-type shader for the frequency response curve
    (`kAnalogFilterResponseVertex`, `kCombFilterResponseVertex`,
    `kLadderFilterResponseVertex`, etc.)
  - `ModulationMeter` and `ModulationKnob` with dedicated shaders that animate
    the modulation destination rings in real time
  - Oscilloscope / bar renderer / line renderer with VBO pipelines
- **Asset pipeline**: Custom `.vitalskin` JSON format with ~200 style
  variables (sizes + colors). Shipped fonts: Lato, Montserrat, OpenSans,
  Roboto, DroidSansMono. SVG icons for effects (chorus, compressor, delay,
  etc.) as vector drawables.
- **Code organization worth learning**:
  - `src/interface/editor_sections/*_section.{h,cpp}` — one
    `SynthSection` class per pane (filter, envelope, chorus...). This is a
    clean pattern for breaking up a massive UI.
  - `src/interface/editor_components/` — reusable widgets (knob, button,
    modulation button, tab selector, line_editor).
  - `src/interface/look_and_feel/` — shaders + skin + fonts.
  - Shaders enumerated in one `Shaders` header (kImageVertex, kFillFragment,
    kCircleFragment, ...) — a registry pattern.
- **Why instructive**: the gold standard for animated, smoothly-rendered,
  high-frame-rate synth UIs. If a new project wants Vital-smooth modulation
  feedback, this is the only real open-source reference.

### 1.2 Surge XT — `surge-synthesizer/surge`

- **URL**: https://github.com/surge-synthesizer/surge
- **License**: GPL-3.0
- **Screenshots**: README & https://surge-synthesizer.github.io — the
  classic dark-with-accent "control-heavy" synth aesthetic.
- **UI rendering**: Pure JUCE `paint()` via `SurgeImage` wrapper that can draw
  either a rasterized bitmap **or** an SVG at any scale. No OpenGL. Everything
  is CPU-rendered but image-cached.
- **LookAndFeel strategy**: `SurgeJUCELookAndFeel` overrides system
  chrome; individual controls are **entirely custom `juce::Component`
  subclasses** under `src/surge-xt/gui/widgets/` — they do *not* subclass
  `Slider`/`Button`. This is important: they mix in a `WidgetBaseMixin<T>`
  CRTP helper for consistent modulation/accessibility behavior.
- **Notable widgets**:
  - `ModulatableSlider` — hand-drawn from an image atlas. The atlas is a grid
    (tray types × modulation states), and the widget indexes into it.
  - `LFOAndStepDisplay` — complex combined LFO/step-sequencer canvas
  - `OscillatorWaveformDisplay` — per-osc-type preview rendering
  - `EffectChooser`, `PatchSelector` (with type-ahead search),
    `WaveShaperSelector`
  - `VuMeter`, `MultiSwitch`, `Switch`, `NumberField`, `MenuCustomComponents`
- **Asset pipeline**: **Skins are user-facing**. Each skin is an XML file
  (`memory-skin.xml` is the built-in "Surge Classic") + a folder of SVGs
  (`resources/classic-skin-svgs/bmp00102.svg`, ...). `SkinSupport.{h,cpp}` is
  ~500 lines of skin loader / DB / resolver code. SVGs are rendered through
  JUCE's Drawable with a skin version (v1 = 1.7-1.8, v2 = 1.9+ adds notch /
  image labels).
- **Code organization worth learning**:
  - Skin-first architecture: every widget asks the skin for placement,
    colors, and images by `ui_identifier` (e.g. `"mixer.mute_o1"`).
  - `SkinImageMaps.h`, `SkinColors`, `SkinFonts` — clean separation of what a
    skin can override.
  - Overlays directory: `src/surge-xt/gui/overlays/` holds all popups/modals
    as separate components.
  - Value callbacks split out into `SurgeGUIEditorValueCallbacks.cpp`,
    menus into `SurgeGUIEditorMenuStructures.cpp` — by-concern file splits.
- **Why instructive**: this is the correct reference for anyone who wants
  a community-skinnable GPL synth with pure-JUCE rendering and production
  polish.

### 1.3 Dexed — `asb2m10/dexed`

- **URL**: https://github.com/asb2m10/dexed
- **License**: GPL-3.0
- **Screenshots**: README — the iconic DX7-facsimile grey panel with four
  operator rows, scaling curves, and envelope micro-displays.
- **UI rendering**: Classic **PNG-filmstrip + LookAndFeel** approach, which
  is the lowest-effort way to get a "hardware-looking" plugin.
- **LookAndFeel strategy**: `DXLookNFeel : public LookAndFeel_V4`. It holds
  `Image` members for each widget type (`imageKnob`, `imageSwitch`,
  `imageButton`, `imageSlider`, `imageScaling`, `imageLight`, `imageLFO`,
  `imageOperator`, `imageGlobal`), and overrides `drawRotarySlider`,
  `drawToggleButton`, `drawLinearSlider`, `drawButtonBackground`. The knob
  image is a **vertical filmstrip** and the widget draws the correct frame
  based on slider position.
- **Notable widgets**:
  - `AlgoDisplay` — draws DX7 algorithm diagrams programmatically (lines +
    rectangles + operator numbers)
  - `OperatorEditor` — grouped envelope display + scaling curve
  - `CartManager` — cartridge program browser (ListBox-based)
  - `VUMeter`, `ProgramListBox`, `TuningShow`
- **Asset pipeline**: `assets/ui/` holds each widget at **@1x and @2x** —
  `Knob_34x34.png` + `Knob_68x68.png`, `Slider_26x26.png` +
  `Slider_52x52.png`, etc. `GlobalEditor_1728x288.png` is the full bottom
  panel background. `Projucer` .jucer file enumerates each as a binary
  resource. Fonts: `NotoSans-Bold.ttf`, `NotoSans-Regular.ttf`. There is an
  HD + SD asset set, chosen at load time via `replaceImage()`.
- **Code organization worth learning**:
  - `REG_COLOUR` macro that both `setColour()`s the LAF and registers it in a
    `colourMap` hash — makes per-user color overrides trivial.
  - `DXComponents.{h,cpp}` groups the custom widgets.
  - `PluginEditor` is compact and readable; the complexity lives in LAF +
    images.
- **Why instructive**: if you want hardware-emulation visuals with **minimum
  custom code**, Dexed is the canonical pattern (LookAndFeel + filmstrips).

### 1.4 Shortcircuit XT — `surge-synthesizer/shortcircuit-xt`

- **URL**: https://github.com/surge-synthesizer/shortcircuit-xt
- **License**: MIT (with the usual JUCE/GPL combined-work caveat)
- **Screenshots**: README links nightly builds; the UI is a modern multi-screen
  sampler with sidebar + tabs + zone editor.
- **UI rendering**: Pure JUCE `paint()`, but built on top of a dedicated
  **shared widget library: `sst-jucegui`**
  (https://github.com/surge-synthesizer/sst-jucegui, MIT). This library
  provides fully custom `Knob`, `VSlider`, `HSlider`, `MultiSwitch`,
  `VUMeter`, `JogUpDownButton`, `SevenSegmentControl`, `TabbedComponent`,
  `NamedPanel`, `TypeInOverlay`, `TextPushButton`, etc. — all drawn with
  `juce::Graphics` but parameterized via a stylesheet.
- **LookAndFeel strategy**: `sst::jucegui::style::StyleSheet` — a
  properties-and-classes CSS-ish system (`Styles::Class`,
  `Styles::Property`, `StyleConsumer` mixin). There is a bridge
  `JUCELookAndFeelAdapter` so JUCE's native widgets participate in the same
  theme. Themes are built-in (`WIREFRAME`, `CELTIC`, `LUX2`, `GRAYLOW`,
  `OCEANOR`) plus `FILE_COLORMAP_ID` for user files.
- **Notable widgets**: all sst-jucegui widgets (see above), plus
  `CompactPlot`, `DraggableTextEditableValue`, `RuledLabel`,
  `TickSeparatorLabel`.
- **Asset pipeline**: `json-assets` directory; fonts embedded (Inter Bold /
  Medium / Regular / Light; Anonymous Pro Regular). Theme is JSON-streamable.
- **Code organization worth learning**:
  - `src/scxt-plugin/theme/ThemeApplier.cpp` — single choke-point where a
    color map is applied to a stylesheet, and then layered with per-pane
    overrides (`applyZoneMultiScreenTheme`, `applyMixerEffectTheme`, ...).
  - `src/scxt-plugin/app/` — one screen per directory
    (`edit-screen/`, `mixer-screen/`, `play-screen/`, `browser-ui/`,
    `other-screens/`).
  - `HasEditor.h` — mixin so any subcomponent can reach the editor/data-cache.
  - sst-jucegui widgets separate *painter* from *component* (`Knob` +
    `Knob::paint()`, `ButtonPainter` etc.), which is more
    testable/restylable than directly drawing in the component.
- **Why instructive**: this is the **cleanest modern architecture** for a
  large JUCE plugin. The separation of widget library / stylesheet / theme
  applier / screen is exactly the abstraction you want for a maintainable
  big-synth UI. OB-Xf also uses sst-jucegui components.

### 1.5 Helm — `mtytel/helm`

- **URL**: https://github.com/mtytel/helm
- **License**: GPL-3.0 (last commit ~8 years ago; predecessor to Vital and a
  cleaner read for the *idea*)
- **Screenshots**: README + https://tytel.org/helm — bright teal/green
  modulation arcs, dark panel, animated LFOs and envelopes.
- **UI rendering**: **Hybrid**: `Graphics&`-drawn LookAndFeel for static
  elements + a parallel `open_gl_component` set (`open_gl_envelope`,
  `open_gl_oscilloscope`, `open_gl_peak_meter`, `open_gl_wave_viewer`,
  `open_gl_modulation_meter`, `open_gl_background`) for anything that
  animates. The animated layer draws over the static layer via a shared
  OpenGL context.
- **LookAndFeel strategy**: `DefaultLookAndFeel : public LookAndFeel_V4`
  overrides `drawLinearSlider` (handles bipolar slider fills,
  split-rectangles, thumb shadow via `DropShadow`) and friends.
  `ModulationLookAndFeel`, `BrowserLookAndFeel`, `TextLookAndFeel` are
  specialised subclasses. `colors.h`, `fonts.h` are free-function registries.
- **Notable widgets**: `graphical_envelope`, `graphical_step_sequencer`,
  `modulation_slider`, `modulation_button` (the modulation routing UI is the
  visual signature of Helm), `patch_selector`, `synth_slider`,
  `filter_response`, `formant_response`.
- **Asset pipeline**: `images/` has PNG icons at @1x and @2x
  (`modulation_selected_active_1x.png` / `_2x.png`). `fonts/` ships
  typefaces. No JSON/XML skin system — colors are hard-coded constants.
- **Code organization worth learning**: one-file-per-widget, clear
  naming (`synth_slider`, `graphical_*`, `open_gl_*` prefix for animated).
  This is the most digestible single-synth codebase in this list.
- **Why instructive**: smaller and older than Vital but far easier to read.
  It shows exactly where OpenGL buys you something (animations) vs. where
  plain Graphics is fine (backgrounds, static labels).

---

## 2. Full Catalog

### Synths / Instruments (JUCE)

| Name | GitHub | License | Stars | UI approach | LAF strategy | Notes |
|---|---|---|---:|---|---|---|
| Vital | mtytel/vital | GPL-3.0 | 1.99k | OpenGL shader + minimal LAF chrome | `DefaultLookAndFeel` + `OpenGlComponent` family | `.vitalskin` JSON, per-filter shaders |
| Surge XT | surge-synthesizer/surge | GPL-3.0 | 3.8k | JUCE paint + SVG/PNG via `SurgeImage` | Custom `juce::Component` subclasses, `WidgetBaseMixin` | XML skin system, 100+ SVGs |
| Dexed | asb2m10/dexed | GPL-3.0 | 3.3k | LAF + PNG filmstrips | `DXLookNFeel : LookAndFeel_V4` overrides draw* | @1x/@2x assets, .jucer Projucer project |
| Shortcircuit XT | surge-synthesizer/shortcircuit-xt | MIT | 500 | JUCE paint via `sst-jucegui` | `sst::jucegui::StyleSheet` + `ThemeApplier` | Best reference for clean architecture |
| OB-Xf | surge-synthesizer/OB-Xf | GPL-3.0 | 453 | PNG + SVG "VectorTheme" | `obxf::LookAndFeel` + `Knob : juce::Slider` with `ScalingImageCache` | Fork of OB-Xd with vector theme |
| Monique | surge-synthesizer/monique-monosynth | other | 400 | JUCE paint + ampler panel | `monique_ui_LookAndFeel` | Requires JUCE 5.3 patch (vintage); morphs + 3D modulation UI |
| Helm | mtytel/helm | GPL-3.0 | 2.5k | Hybrid: LAF + OpenGL animation overlays | `DefaultLookAndFeel` + `open_gl_*` widgets | Hard-coded colors, dead repo but very readable |
| Odin 2 | TheWaveWarden/odin2 | other | 765 | SVG filmstrips via `UIAssetManager` | Custom `m_feels` per widget type | SVG-everywhere, per-element theme file `theme.xml` |
| OB-Xd (orig) | reales/OB-Xd | none | 242 | (repo now ~empty; history lives in OB-Xf) | — | Read OB-Xf instead |
| osci-render | jameshball/osci-render | GPL-3.0 | 686 | JUCE paint + custom LAF + Lua/JS extensions | `OscirenderLookAndFeel : LookAndFeel_V4` using colour constants + `jux::SwitchButton` helpers | Built-in Dracula palette |
| RipplerX | tiagolr/ripplerx | GPL-3.0 | 547 | Direct `paint()` (no `juce::Slider`) | `CustomLookAndFeel` + freestanding `Rotary`/`Meter`/`Pitch` components | Each custom control listens to APVTS and repaints on param change |
| blocks | dan-german/blocks | GPL-3.0 | 193 | JUCE paint + theme manager | `BlocksLookAndFeel` + `BoxSliderLooksAndFeel` | Modular-drag UI; `ThemeManager`, `ColourPool`, easing animator |
| AudiblePlanets | gregrecco67/AudiblePlanets | GPL-3.0 | 159 | JUCE paint via **Gin** framework | `gin::ProcessorEditor` base | 1181x725 fixed; `OrbitViz.h` custom planetary modulation viz |
| ChowKick | Chowdhury-DSP/ChowKick | BSD-3-Clause | 188 | **foleys_gui_magic** (XML+CSS) | magic style classes | All GUI defined in `res/gui.xml`; excellent reference for no-code GUI |
| Crypt 2 | vitling/crypt | GPL-3.0 | 60 | JUCE paint | custom LAF | Hyper-unison synth with polished modern UI |
| Wavetable | FigBug/Wavetable | BSD-3-Clause | 201 | JUCE paint via **Gin** | `gin::ProcessorEditor` | Companion to FigBug's Gin showcase |
| TAL-NoiseMaker | Nexbit/tal-noisemaker | (TAL EULA) | 27 | JUCE paint + PNG images | LAF overrides | Original TAL sources; hardware-look; GPL-incompatible |
| Monique-Monosynth | surge-synthesizer/monique-monosynth | other | 400 | Custom JUCE paint | `monique_ui_LookAndFeel` | See above |
| Magical8bitPlug2 | yokemura/Magical8bitPlug2 | GPL-3.0 | 375 | JUCE paint | LAF | 8-bit NES/Famicom aesthetic |
| ADLplug | jpcima/ADLplug | BSL-1.0 | 517 | JUCE paint + filmstrips | LAF + bitmap resources | OPL3/OPN2 FM synths |
| tunefish | paynebc/tunefish | GPL-3.0 | 300 | JUCE paint + own widgets | custom LAF | Virtual Analog |
| juicysfplugin | Birch-san/juicysfplugin | GPL-3.0 | 315 | JUCE paint | minimal LAF | Soundfont synth |
| Hera | jpcima/Hera | GPL-3.0 | 42 | JUCE + custom bitmap widgets | LAF | Juno 60 emulation — good small example |
| ripchord | trackbout/ripchord | GPL-3.0 | 98 | JUCE paint + minimalist LAF | — | Clean MIDI plugin UI |

### Effects / Plugins with Exceptional UIs (JUCE)

| Name | GitHub | License | Stars | Why it's visually relevant |
|---|---|---|---:|---|
| ZLEqualizer | ZL-Audio/ZLEqualizer | AGPL-3.0 | 830 | Dense pro-grade dynamic-EQ UI; `source/gui/` is well-organized (attachment, button, combobox, dragger, slider, tooltip subfolders) |
| BYOD | Chowdhury-DSP/BYOD | GPL-3.0 | 547 | Pedalboard-style drag-and-drop UI; `ByodLNF`, `ProcessorLNF`, per-processor editors in `src/gui/pedalboard/editors/` |
| ChowMatrix | Chowdhury-DSP/ChowMatrix | BSD-3-Clause | 327 | Node-tree delay matrix (`MatrixView/`) with `MatrixAurora` aurora-style visualization |
| AnalogTapeModel (ChowTape) | jatinchowdhury18/AnalogTapeModel | GPL-3.0 | 1.3k | Polished "tape reels" visual, modulatable sliders, shipped with `RobotoCondensed` + custom SVG knob (`knob.svg`), custom `pointer.svg` |
| ChowPhaser | jatinchowdhury18/ChowPhaser | BSD-3-Clause | 86 | Clean vintage-phaser look |
| Fire | jerryuhoo/Fire | AGPL-3.0 | 624 | Multi-band distortion with striking dark-mode spectrum overlay |
| Maim | ArdenButterfield/Maim | GPL-3.0 | 352 | MP3 glitch plugin with playful, expressive UI |
| RoomReverb | cvde/RoomReverb | GPL-3.0 | 140 | Uses **foleys_gui_magic** — reference for no-code GUI |
| valentine | tote-bag-labs/valentine | GPL-3.0 | 182 | Boutique-feeling compressor |
| Simple Reverb | szkkng/simple-reverb | GPL-3.0 | 124 | Minimal clean modern UI, often cited as a starting point |
| Frequalizer | ffAudio/Frequalizer | BSD-3-Clause | 364 | The original foleys_gui_magic showcase |
| Schrammel_OJD | JanosGit/Schrammel_OJD | GPL-3.0 | 187 | Overdrive pedal plugin using `Resvg4JUCE` for crisp SVG rendering |
| SG-323 | greyboxaudio/SG-323 | GPL-3.0 | 91 | Ursa Major Stargate emulation with retro hardware UI |

### GUI Frameworks / Modules

| Name | GitHub | License | Stars | Purpose |
|---|---|---|---:|---|
| foleys_gui_magic | ffAudio/foleys_gui_magic | other (BSD-ish + license-gated commercial) | 542 | WYSIWYG editor + XML/CSS layout engine — builds the entire GUI from `gui.xml`. Used by ChowKick, RoomReverb, Frequalizer. `DESIGNING.md` in the repo is required reading. |
| JIVE | ImJimmi/JIVE | MIT | 185 | Declarative GUI markup for JUCE (ValueTree-driven, FlexBox + Grid) |
| melatonin_blur | sudara/melatonin_blur | MIT | 158 | Fast CPU drop/inner shadows and blurs — *the* library for modern "soft-shadow" JUCE UIs |
| melatonin_inspector | sudara/melatonin_inspector | MIT | 260 | Web-inspector-style component tree for debugging JUCE UIs |
| fontaudio | fefanto/fontaudio | MIT | 393 | Permissively-licensed icon font for audio (knobs, transport, etc.) |
| Resvg4JUCE | JanosGit/Resvg4JUCE | MPL-2.0 | 29 | Wrapper for the resvg Rust SVG rasterizer — solves JUCE's weaker SVG fidelity |
| sst-jucegui | surge-synthesizer/sst-jucegui | MIT | 2 | The widget library behind Surge XT / Shortcircuit XT / OB-Xf |
| Gin | FigBug/Gin | BSD-3-Clause | 375 | Huge extras library; its `gin_plugin` module provides `ProcessorEditor` base class used by AudiblePlanets / Wavetable / slPlugins |
| HISE | christophhart/HISE | other | 1.4k | Full sampler framework; has its own GUI scripting (ScriptComponents, SVG paths) |
| react-juce (Blueprint) | JoshMarler/react-juce | MIT | 826 | React.js front-ends in JUCE plugins (Duktape JS + JUCE backend). **Archived-style: last commit ~4y ago.** |
| plugdata | plugdata-team/plugdata | GPL-3.0 | 2.2k | PureData-in-JUCE with a *completely* custom node-graph UI — instructive for canvas-style plugins |
| melatonin_audio_sparklines | sudara/melatonin_audio_sparklines | MIT | 102 | ASCII waveform debug output |
| animator | bgporter/animator | MIT | 80 | Easing curves for JUCE animations |

### Templates / Build

| Name | GitHub | License | Stars | Notes |
|---|---|---|---:|---|
| Pamplejuce | sudara/pamplejuce | MIT | 701 | JUCE 8 + CMake + Catch2 + Pluginval template. Not a UI project, but the *baseline build scaffold* most modern JUCE plugins use. Ships with sensible CMake targets and GitHub Actions. |

### Non-JUCE (called out to avoid confusion)

- **Cardinal** (`DISTRHO/Cardinal`, GPL-3.0, 3.0k stars) — based on the **DPF
  framework** (DISTRHO Plugin Framework), **not JUCE**. The repo has `dpf/`,
  `carla`, etc. Excluded from JUCE-specific lessons but visually remarkable.
- **Geonkick** (`quamplex/geonkick`, GPL-3.0) — uses its own **Redkite**
  GUI toolkit, not JUCE. Very polished percussion-synth UI, but the code
  will not teach JUCE.

---

## 3. Cross-Cutting Observations: What Makes a JUCE UI Visually Great *and* Functional

Patterns recurring across the best examples above:

### 3.1 Separate the skin from the code
Every top-tier synth ships a skin system, and the skin is where the colors
and positions live:
- **Surge XT**: XML `memory-skin.xml` + folder of SVGs, referenced by
  `ui_identifier` strings. Users can ship custom skins.
- **Vital**: JSON `.vitalskin` with ~200 named variables.
- **Shortcircuit XT / OB-Xf**: `sst-jucegui` stylesheet with classes and
  properties; built-in `ColorMap` presets (`WIREFRAME`, `CELTIC`, `LUX2`,
  `GRAYLOW`, `OCEANOR`).
- **Odin 2**: `theme.xml` plus folders of SVGs keyed by widget name.
- **Dexed**: colors registered via `REG_COLOUR` macro into a `colourMap` so
  each can be re-bound by a user.

Even if you never ship skinning to end users, decoupling colors and sizes
into named variables up front is what enables pixel-perfect iteration.

### 3.2 Custom components beat `juce::Slider` overrides for anything bespoke
- **Surge XT's `ModulatableSlider`** and **RipplerX's `Rotary`** are pure
  `juce::Component`s that implement their own mouse handling. This is
  faster to iterate visually and avoids `juce::Slider`'s layout surprises.
- When you do subclass `juce::Slider` (Vital's `OpenGlSlider`, OB-Xf's
  `Knob`), it's usually because you still want JUCE's keyboard handling and
  accessibility plumbing — but the *drawing* is completely hand-done.

### 3.3 SVG beats PNG for new projects
- Classic codebases (Dexed, OB-Xd, TAL-NoiseMaker) use PNG filmstrips with
  @1x/@2x. Fine for fixed-window plugins, but poor at arbitrary zoom and
  Hi-DPI.
- Modern codebases (Surge XT, Odin 2, OB-Xf, ChowTape) use SVG + a
  scaling/rasterization cache.
- For the best SVG quality, **use Resvg4JUCE** (`JanosGit/Resvg4JUCE`) — it
  wraps the Rust `resvg` renderer and is strictly better than JUCE's
  built-in Drawable at fine SVG details.

### 3.4 Use a BinaryData font and commit to it
Every one of the projects above bundles fonts as BinaryData. Typeface choice
is a massive part of visual identity:
- Vital: Lato, Montserrat, OpenSans, Roboto + DroidSansMono
- Shortcircuit XT: Inter (4 weights) + Anonymous Pro mono
- Dexed: NotoSans (Regular + Bold)
- OB-Xf: Jersey20 + Trek (a custom LED/segment font)
- ChowTape: RobotoCondensed
- blocks: Roboto Medium

Don't use the system font. Load a display face for headings and a mono for
values, both via `Typeface::createSystemTypefaceFor(BinaryData::...)`.

### 3.5 Animation requires OpenGL (or aggressive caching)
The visual "wow" of Vital / Helm is almost entirely in things that **move
every frame**: modulation arcs that track LFOs, filter responses that deform
smoothly, wavetable 3D viewers. If you want this:
- **Option A (Vital)**: go all-in on OpenGL, write shaders for every
  dynamic element. Requires a shader registry pattern, `OpenGlWrapper`
  context holder, and careful viewport/scissor management.
- **Option B (Helm)**: keep static chrome in `Graphics&` + layer `OpenGl`
  components only for animations. Simpler, still smooth.
- **Option C (Surge XT, Shortcircuit XT)**: don't animate continuously.
  Repaint only on parameter change and cache. This is perfectly acceptable
  and is the JUCE-idiomatic choice.

### 3.6 Use `melatonin_blur` for soft shadows
Stock `juce::DropShadow` is slow and grainy. For any modern dark-mode UI
(soft glows, dialog shadows, depressed-button inner shadows),
`sudara/melatonin_blur` is the standard. It's MIT, Metal/CoreGraphics-fast,
and drops in as a JUCE module.

### 3.7 Organize by *screen / section*, not by widget type
- Surge XT: `overlays/`, `widgets/` (widgets are reusable, overlays are
  page-specific).
- Vital: `editor_sections/` one-file-per-pane (`chorus_section`,
  `filter_section`, `envelope_section`, ...) and `editor_components/` for
  shared widgets.
- Shortcircuit XT: `app/edit-screen/`, `app/mixer-screen/`,
  `app/play-screen/`, `app/browser-ui/`.
- This one-directory-per-screen / one-directory-per-widget-type split
  scales well once a UI has 30+ controls.

### 3.8 Split the editor class by concern
Surge's `SurgeGUIEditor` is split across
`SurgeGUIEditorValueCallbacks.cpp`, `SurgeGUIEditorMenuStructures.cpp`,
`SurgeGUIEditorOverlays.cpp`, `SurgeGUIEditorKeyboardActions.h`,
`SurgeGUIEditorInfowindow.cpp`. Once your editor passes ~1000 lines this is
the right move.

### 3.9 Expose a theme-applier as a single choke-point
Shortcircuit XT's `ThemeApplier` exposes one method per themeable region
(`applyHeaderTheme`, `applyMixerEffectTheme`, `applyZoneMultiScreenTheme`,
...). All color/font decisions funnel through it. This makes it trivial to
re-skin or to add a light mode.

### 3.10 Inspector-first development
Install `melatonin_inspector` early. It gives you a Chrome-DevTools-style
component tree inside the running plugin, shows bounds / margins, and lets
you live-edit properties. It's free (MIT) and the single biggest quality
multiplier for pixel-perfect work.

---

## 4. Strategic Notes: WebBrowserComponent vs. Native JUCE

A recurring question is: do I render my synth UI in HTML/CSS/JS via a
WebBrowserComponent, or in native JUCE C++?

### 4.1 Projects actually using WebBrowserComponent
- **JUCE's own `WebViewPluginDemo`** (in `examples/Plugins/`) — the
  canonical "hello world" for web-rendered plugins; uses
  `juce_gui_extra`'s `WebBrowserComponent::Resource` hook to serve HTML/JS
  from BinaryData, with two-way parameter binding.
- **react-juce / Blueprint** (`JoshMarler/react-juce`) — ran React.js inside
  JUCE via Duktape. Archived-feel: last meaningful activity ~4 years ago.
  **Not recommended for new projects** — toolchain rot risk is real.
- A scattering of newer one-off synths (`dannyblackman/anarack`,
  `ftrain/autosynth`, `refektor/house-stab-sampler`) use
  `juce::WebBrowserComponent` directly. None are production references.

Note: the WebBrowserComponent approach has gotten more viable since JUCE 8
ships first-class WebView2 (Windows) + WKWebView (macOS) + WebKitGTK
(Linux) support and a resource-serving API.

### 4.2 Native JUCE (everything else in this report)
All of Vital, Surge XT, Shortcircuit XT, Dexed, Helm, Odin 2, OB-Xf, Monique,
BYOD, ChowTape, AudiblePlanets, RipplerX, blocks, osci-render, ZLEqualizer,
and essentially every popular open-source JUCE synth uses native JUCE
rendering.

### 4.3 Tradeoffs

| Concern | Native JUCE | WebBrowserComponent |
|---|---|---|
| Designer iteration speed | Slow (recompile for visual changes) | Fast (hot-reload HTML/CSS) |
| Designer pool | Small (C++ + JUCE) | Huge (any web designer) |
| Startup latency | Fast (<50ms) | Slow (100-500ms to spin up WebView) |
| RAM footprint | Low (10-30MB) | High (WebView adds 50-200MB) |
| CPU while idle | ~0% | Non-zero (JS engine, compositor) |
| Platform bundle size | Small | Big (WebView2 runtime on Windows) |
| Host DAW compatibility | Universal (40+ years of JUCE-in-DAW polish) | Variable — some hosts still have issues with plugin-embedded WebView |
| Accessibility / screen readers | Works via JUCE's AX support | Works via WebView AX; generally better than JUCE for dense UIs |
| Animation fidelity | Excellent with OpenGL, painful without | Excellent (browser compositor) |
| Pixel-perfect design-to-implementation | Hard (manual painting) | Easy (Figma-to-CSS is routine) |
| Long-term maintenance | Very stable (JUCE 4→8 has been smooth) | WebView APIs churn; Duktape/V8 toolchains rot |
| License compatibility | Clean | Chromium/WebView2 licensing footnotes |
| Debugging | `melatonin_inspector` + debugger | DevTools (huge plus) |
| Right-click / context menus | Native OS menus "just work" | Need custom plumbing |
| File drag-and-drop | Clean via JUCE | Messier via WebView |

### 4.4 Recommendation for the skill

For a skill that teaches **pixel-perfect replication**, the native-JUCE
path is the one to lean into:
- The existing canonical references (Vital, Surge XT, Shortcircuit XT,
  Dexed, Helm, OB-Xf) all teach native techniques. A WebView-first skill
  would have very thin reference material.
- Pixel-perfect in native JUCE is a *C++ craft* — the lessons transfer across
  the entire ecosystem.
- However, the skill should still *mention* WebBrowserComponent as the right
  answer in two cases:
  1. When the user already has a polished web design and wants to lift it
     verbatim.
  2. When the UI has genuinely web-shaped interactions (rich text, complex
     tables, CSS-grid layouts).

A hybrid plugin (JUCE for animations + WebView for settings panels) is
perfectly defensible but rarely seen in open source — there is no canonical
open-source reference for this pattern today.

---

## 5. Must-Read Source Files (quick shortlist for the skill)

If the skill wants to cite or quote canonical code:

- **Vital** `src/interface/look_and_feel/shaders.h` — shader enum registry
- **Vital** `src/interface/editor_components/synth_slider.h` — the "how do I
  make an OpenGL rotary" canonical implementation
- **Surge XT** `src/surge-xt/gui/SkinSupport.h` — XML skin system
- **Surge XT** `src/surge-xt/gui/widgets/ModulatableSlider.cpp` — image-atlas
  indexing
- **Shortcircuit XT** `src/scxt-plugin/theme/ThemeApplier.h` /
  `ColorMap.h` — theme architecture
- **sst-jucegui** `include/sst/jucegui/components/Knob.h` — painter / consumer
  / style class separation
- **Dexed** `Source/DXLookNFeel.{h,cpp}` — LAF + image-based rotary
- **Helm** `src/look_and_feel/default_look_and_feel.cpp` — canonical hand-drawn
  `drawLinearSlider`
- **foleys_gui_magic** `DESIGNING.md` + `Examples/FoleysSynth/` — no-code
  GUI route
- **ChowKick** `res/gui.xml` — a production `gui_magic` XML in the wild
- **Odin 2** `Source/gui/DrawableSlider.cpp` — SVG-driven slider with
  `UIAssetManager` scaling

---

## Appendix: Starred metadata snapshot (2026-04-18)

Collected via `gh api`:

- surge-synthesizer/surge: 3802 stars, GPL-3.0
- mtytel/vital: 1992 stars, GPL-3.0
- asb2m10/dexed: 3319 stars, GPL-3.0
- mtytel/helm: 2487 stars, GPL-3.0
- TheWaveWarden/odin2: 765 stars, other
- surge-synthesizer/OB-Xf: 453 stars, GPL-3.0
- surge-synthesizer/shortcircuit-xt: 502 stars, MIT
- surge-synthesizer/monique-monosynth: 400 stars, other
- Chowdhury-DSP/BYOD: 547 stars, GPL-3.0
- Chowdhury-DSP/ChowMatrix: 327 stars, BSD-3-Clause
- Chowdhury-DSP/ChowKick: 188 stars, BSD-3-Clause
- jatinchowdhury18/AnalogTapeModel: 1338 stars, GPL-3.0
- jatinchowdhury18/ChowPhaser: 86 stars, BSD-3-Clause
- DISTRHO/Cardinal: 3006 stars, GPL-3.0 (DPF, not JUCE)
- quamplex/geonkick: (GPL-3.0, Redkite, not JUCE)
- Nexbit/tal-noisemaker: 27 stars, TAL EULA (GPL-incompatible)
- ffAudio/foleys_gui_magic: 542 stars
- sudara/pamplejuce: 701 stars, MIT
- ZL-Audio/ZLEqualizer: 830 stars, AGPL-3.0
- jameshball/osci-render: 686 stars, GPL-3.0
- tiagolr/ripplerx: 547 stars, GPL-3.0
- dan-german/blocks: 193 stars, GPL-3.0
- gregrecco67/AudiblePlanets: 159 stars, GPL-3.0
- JoshMarler/react-juce: 826 stars, MIT (effectively archived)
- sudara/melatonin_blur: 158 stars, MIT
- sudara/melatonin_inspector: 260 stars, MIT
- FigBug/Gin: 375 stars, BSD-3-Clause
- ImJimmi/JIVE: 185 stars, MIT
- JanosGit/Resvg4JUCE: 29 stars, MPL-2.0
- surge-synthesizer/sst-jucegui: 2 stars, MIT (companion, not a product)
