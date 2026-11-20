# JUCE UI Primitives: Reference for High-Fidelity Synth UIs

Dense reference for building custom JUCE (C++) audio plugin UIs that match a
designer's spec with pixel-level fidelity. Assumes JUCE 7/8, C++17+, and
familiarity with `juce::Component`, `AudioProcessorValueTreeState` (APVTS), and
the Projucer/CMake build flow.

## 1. Component Painting

Every `juce::Component` exposes `paint(Graphics&)` and `paintOverChildren`. The
lifecycle is: JUCE decides a region is dirty (from `repaint()` or a
parent/clip), calls `paint()` on the component, then recursively paints its
children on top, then finally `paintOverChildren()` — the only hook that draws
on top of the child subtree. Use it for badges, focus rings, drag-overlays,
scanlines/CRT overlays, and anything that must read as "foreground chrome".

```cpp
void MyPanel::paint (juce::Graphics& g)
{
    auto r = getLocalBounds().toFloat();
    g.fillAll (theme.panelBg);                 // background
    g.setColour (theme.panelBorder);
    g.drawRoundedRectangle (r.reduced (0.5f), 6.0f, 1.0f);
}

void MyPanel::paintOverChildren (juce::Graphics& g)
{
    if (hasFocus)
    {
        g.setColour (theme.focus.withAlpha (0.6f));
        g.drawRoundedRectangle (getLocalBounds().toFloat().reduced (1.0f), 6.0f, 2.0f);
    }
}
```

**Graphics API essentials.** `Graphics` is a state machine: set colour/gradient
/font/transform/clip, then issue draw calls. The most-used primitives:

- `fillAll`, `fillRect(Rectangle<float>)`, `fillRoundedRectangle`,
  `fillEllipse`, `fillPath` — solid fills (anti-aliased by default, except
  aligned integer `fillRect` which snaps to pixel edges).
- `drawLine(x1,y1,x2,y2,thickness)`, `drawRect`, `drawRoundedRectangle`,
  `drawEllipse`, `strokePath(path, PathStrokeType)`.
- `setGradientFill(ColourGradient)` — linear or radial, pass `true` for radial.
  Add stops via `addColour(proportion, colour)`.
- `drawImage`, `drawImageAt`, `drawImageTransformed`.
- `drawText`, `drawFittedText`, `drawMultiLineText`.

Gradient and path example (matte synth knob body, adapted from a real product
LookAndFeel):

```cpp
juce::ColourGradient dome (knobBodyLight,  cx, cy - r * 0.55f,
                           knobBodyDark,   cx, cy + r * 0.20f, false);
dome.addColour (0.55, knobBodyMid);
g.setGradientFill (dome);
g.fillEllipse (cx - r, cy - r, r * 2, r * 2);
```

**Paths.** `juce::Path` is the workhorse for resolution-independent shapes.
Always start with `startNewSubPath` (or `addRectangle/addEllipse/etc.`), build
with `lineTo`, `cubicTo`, `quadraticTo`, `addCentredArc`, then either
`g.fillPath(p)` or `g.strokePath(p, PathStrokeType(width, curved, rounded))`.
`PathStrokeType::JointStyle::curved` and `EndCapStyle::rounded` give the
clean, modern cap/joint look designers expect from Figma strokes.

**Anti-aliasing.** JUCE AA is on by default for paths and fills. Disable per
call with `g.setImageResamplingQuality(Graphics::lowResamplingQuality)` for
images; for crisp 1-pixel lines on integer bounds, offset by 0.5f (`bounds
.reduced(0.5f)`) or use `g.fillRect(Rectangle<int>)` instead of float. Use
`Graphics::getInternalContext().fillRectList(...)` for large batched rect
fills (meters, step grids).

**Fonts.** `juce::Font` is specified via `FontOptions` since JUCE 8:
`Font(FontOptions(typeface)).withHeight(12.0f)`. Always call `g.setFont(f)`
before `drawText`. For small UI text, clamp the computed height
(`jlimit(9.0f, 18.0f, ...)`) so labels stay legible across resize.

## 2. Custom Knobs

Three approaches, picked by target aesthetic:

**A. Image-filmstrip rotary knobs (classic).** A single PNG is a vertical strip
of N pre-rendered frames from min to max. Cheap to paint, pixel-perfect, zero
math, but resolution-locked and painful to re-skin.

```cpp
class FilmstripKnob : public juce::Slider
{
public:
    FilmstripKnob (juce::Image strip, int frameCount)
      : filmstrip (std::move (strip)), frames (frameCount)
    { setSliderStyle (RotaryVerticalDrag); setTextBoxStyle (NoTextBox, false, 0, 0); }

    void paint (juce::Graphics& g) override
    {
        const int fw = filmstrip.getWidth();
        const int fh = filmstrip.getHeight() / frames;
        const int idx = juce::jlimit (0, frames - 1,
            (int) std::floor (valueToProportionOfLength (getValue()) * (frames - 1)));
        g.drawImage (filmstrip, 0, 0, getWidth(), getHeight(),
                     0, idx * fh, fw, fh);
    }
private:
    juce::Image filmstrip;
    int frames { 127 };
};
```

Tradeoffs: ship 1×/2× filmstrips side by side and pick via
`Desktop::getDisplays().getDisplayContaining(...)->scale`. 65–127 frames hits
the sweet spot of file size vs. rotation smoothness.

**B. Vector-drawn (modern, resolution-independent).** Override `drawRotarySlider`
on a `LookAndFeel_V4` subclass. Use `addCentredArc` for the track/value arcs,
a line or dot for the pointer. Stack multiple strokes of decreasing width /
increasing alpha for "neon bloom" glow effects.

```cpp
void MyLnF::drawRotarySlider (juce::Graphics& g, int x, int y, int w, int h,
                              float sliderPos, float rStart, float rEnd,
                              juce::Slider&)
{
    auto bounds = juce::Rectangle<int> (x, y, w, h).toFloat().reduced (4.0f);
    auto radius = juce::jmin (bounds.getWidth(), bounds.getHeight()) * 0.5f;
    auto cx = bounds.getCentreX(), cy = bounds.getCentreY();
    auto angle = rStart + sliderPos * (rEnd - rStart);

    // body
    g.setColour (theme.knobBody);
    g.fillEllipse (cx - radius, cy - radius, radius * 2, radius * 2);

    // track
    juce::Path track, value;
    track.addCentredArc (cx, cy, radius - 3, radius - 3, 0.0f, rStart, rEnd, true);
    value.addCentredArc (cx, cy, radius - 3, radius - 3, 0.0f, rStart, angle, true);

    g.setColour (theme.knobTrack);
    g.strokePath (track, juce::PathStrokeType (3.0f, juce::PathStrokeType::curved,
                                                     juce::PathStrokeType::rounded));

    // multi-pass glow
    for (auto [w, a] : { std::pair{12.0f, 0.08f}, {6.5f, 0.18f}, {3.5f, 0.35f} })
    {
        g.setColour (theme.knobArc.withAlpha (a));
        g.strokePath (value, juce::PathStrokeType (w, juce::PathStrokeType::curved,
                                                      juce::PathStrokeType::rounded));
    }
    g.setColour (theme.knobArc);
    g.strokePath (value, juce::PathStrokeType (2.0f));

    // pointer
    auto sinA = std::sin (angle), cosA = std::cos (angle);
    g.setColour (theme.knobDot);
    g.drawLine (cx + radius * 0.22f * sinA, cy - radius * 0.22f * cosA,
                cx + radius * 0.86f * sinA, cy - radius * 0.86f * cosA, 1.6f);
}
```

Apply with `slider.setLookAndFeel(&lnf)`, or per-instance via a child
`LookAndFeel`. Use `slider.setRotaryParameters({..})` to control start/end
angle and whether the arc stops at extremes.

**C. Hybrid / Drawable-based.** `juce::Drawable::createFromSVG(xmlDoc)` parses
an SVG path; rotate with `setTransform(AffineTransform::rotation(angle, cx,
cy))`. Good for bespoke brand glyphs on the knob body (logo dots, tick marks)
layered over a vector-drawn shell.

**LookAndFeel vs. fully custom Component.** Prefer a LookAndFeel override when
the behaviour is a standard `juce::Slider` / `Button` / `ComboBox` and you
want keyboard, accessibility, APVTS attachment, and popup editors for free.
Reach for a full `Component` subclass when the widget has custom hit regions
(multi-value XY pads, drag-to-reorder mod slots, zoomable filter curves),
gesture state beyond drag, or touch semantics.

## 3. Custom LookAndFeel

Subclass `juce::LookAndFeel_V4` (not V1/V2/V3 — V4 is the current baseline and
handles dark mode, scroll bars, tab buttons consistently). Key override points
for a synth UI:

```cpp
class MyLookAndFeel : public juce::LookAndFeel_V4
{
public:
    MyLookAndFeel();
    juce::Typeface::Ptr getTypefaceForFont (const juce::Font&) override;

    void drawRotarySlider (juce::Graphics&, int, int, int, int,
                           float, float, float, juce::Slider&) override;
    void drawLinearSlider (juce::Graphics&, int, int, int, int,
                           float, float, float,
                           juce::Slider::SliderStyle, juce::Slider&) override;

    void drawButtonBackground (juce::Graphics&, juce::Button&,
                               const juce::Colour&, bool, bool) override;
    void drawButtonText       (juce::Graphics&, juce::TextButton&, bool, bool) override;
    void drawToggleButton     (juce::Graphics&, juce::ToggleButton&, bool, bool) override;

    void drawComboBox         (juce::Graphics&, int, int, bool, int, int, int, int,
                               juce::ComboBox&) override;
    void positionComboBoxText (juce::ComboBox&, juce::Label&) override;
    juce::Font getComboBoxFont (juce::ComboBox&) override;

    void drawPopupMenuItem (juce::Graphics&, const juce::Rectangle<int>&, bool, bool,
                            bool, bool, bool, const juce::String&, const juce::String&,
                            const juce::Drawable*, const juce::Colour*) override;

    void drawLabel (juce::Graphics&, juce::Label&) override;
    juce::Font getLabelFont (juce::Label&) override;
};
```

Install once on the editor and propagate downward: `setLookAndFeel(&lnf)` in
the top-level editor ctor, `setLookAndFeel(nullptr)` in its dtor to avoid
dangling pointers if children outlive it. Colour IDs (`Slider::thumbColourId`,
`TextButton::buttonColourId`, etc.) are the ergonomic way to push theme
colours down without rewriting all draw code.

**Reference implementations worth reading**

- **Surge XT — `SkinSupport` / `SurgeLookAndFeel`** (GPL-3.0). Full theming
  pipeline with XML-described skins, colour tokens, image resource packs, and
  a live reloader. Strong reference for how to build a *data-driven* theme
  rather than hard-coding colours into the LnF.
- **Vital — skin system** (GPL-3.0). OpenGL-rendered UI with a JSON skin
  definition and shader-based knob rendering. Reference for high-framerate
  modulation visualisation and GL shader usage.
- **JUCE DemoRunner — `LookAndFeelDemo.cpp`**. Minimal, canonical LnF
  subclass showing how to swap between V1/V2/V3/V4.
- **ffAudio `foleys_gui_magic`** (BSD). Declarative XML-driven UI with live
  editor; useful for data-binding patterns even if you don't adopt the
  editor itself.

For GPL references, *read the patterns, do not copy source* unless your
plugin is GPL-compatible.

## 4. Asset Pipeline

Binary resources are compiled into the plugin via `juce_add_binary_data`
(CMake) or the Projucer "Binary Data" section. Assets appear as
`BinaryData::myLogo_png` / `BinaryData::myLogo_pngSize` and a helper
`BinaryData::getNamedResource(name, sizeOut)`.

```cmake
juce_add_binary_data (PluginAssets
    HEADER_NAME  BinaryData.h
    NAMESPACE    BinaryData
    SOURCES
        resources/fonts/SpaceGroteskMedium.ttf
        resources/knobs/big-knob.png
        resources/icons/logo.svg)
target_link_libraries (MyPlugin PRIVATE PluginAssets)
```

**Images.**

```cpp
auto img = juce::ImageCache::getFromMemory (BinaryData::bigknob_png,
                                            BinaryData::bigknob_pngSize);
```

`ImageCache` dedupes by pointer so repeated calls are free. For PNG
filmstrips and texture atlases, cache once in a static/singleton and reuse.

**Drawables / SVG.**

```cpp
auto svg = juce::parseXML (juce::String::fromUTF8 (BinaryData::logo_svg,
                                                    BinaryData::logo_svgSize));
auto drawable = juce::Drawable::createFromSVG (*svg);
drawable->drawWithin (g, bounds, juce::RectanglePlacement::centred, 1.0f);
```

`DrawableButton` gives you states (normal / over / down / on) with four
Drawables and automatic hit-testing. Good for transport buttons.

**PNG vs. SVG for rotary controls.**

- PNG filmstrip: lowest CPU paint cost, pixel-perfect at a single size, big
  binary if 2x/3x variants are bundled, impossible to re-colour at runtime.
- Vector (Path/Drawable): trivial re-skinning, resolution-independent, scales
  cleanly to any DPI, paint cost grows with stroke count + glow passes.
  Usually wins for modern synth UIs.
- Hybrid: vector body + PNG engraved tick-ring for a premium screened-metal
  look. Bake the metal texture as an image, draw the arc/pointer on top.

## 5. Hi-DPI and Scaling

JUCE auto-manages backbuffer DPI on macOS (Retina) and Windows (per-monitor
v2) as long as `juce_gui_basics` is configured correctly. What you control:

```cpp
// Physical/logical scale of the display the editor is currently on
auto* display = juce::Desktop::getInstance().getDisplays()
                    .getDisplayForRect (editor.getScreenBounds());
const float scale = display != nullptr ? (float) display->scale : 1.0f;
```

Pick filmstrips (@1x, @2x) based on `scale`. For images embedded in larger
compositions, prefer `juce::ScaledImage { img, scale }` which holds the
source alongside its logical scale so AA stays correct across DPI changes.

**Pixel-exact rendering.** On 1× displays, offset integer bounds by 0.5 for
strokes (`drawRect(r.toFloat().reduced(0.5f), 1.0f)`) so 1 px lines don't
blur. On 2× displays the AA is transparent. Use
`Component::setBufferedToImage(true)` on heavy static chrome, or
`setOpaque(true)` if a component fully fills its bounds — JUCE will skip
painting parents behind it.

**Window-level zoom.** Expose a user-preference "UI scale" via
`setTransform(AffineTransform::scale(userScale))` on the top-level editor,
then call `setSize(baseW * userScale, baseH * userScale)`. Children
automatically lay out in logical pixels.

## 6. OpenGL Acceleration

Attach a `juce::OpenGLContext` to the editor to route all painting through
GL.

```cpp
class MyEditor : public juce::AudioProcessorEditor
{
    juce::OpenGLContext openGL;
public:
    MyEditor (...) { openGL.attachTo (*this); }
    ~MyEditor() override { openGL.detach(); }
};
```

Wins: massively faster for heavy transparent layering, animated spectrum /
scope / waveform components, and full-editor 60 Hz repaints. Reduces CPU
spikes on compositor-heavy macOS windows.

Costs: **font rendering differs** (subpixel behaviour and hinting change on
macOS vs. Windows), so type can look subtly worse on Windows and subtly
softer on macOS. Startup latency +50-200 ms. Intermittent GL context loss on
DAWs that detach/reattach windows (Pro Tools, some Live builds) — be ready
to tear down and rebuild components. Prefer attaching only on the components
that need it (individual scopes) rather than the whole editor, unless
animation is pervasive.

Rule of thumb: ship without GL first; profile; add GL selectively if the
main editor loop exceeds ~8 ms on mid-range hardware.

## 7. Fonts

Bundle TTFs/OTFs via BinaryData, then construct a Typeface once and hand it
out through the LookAndFeel:

```cpp
typeface = juce::Typeface::createSystemTypefaceFor (
    BinaryData::SpaceGroteskMedium_ttf,
    BinaryData::SpaceGroteskMedium_ttfSize);

juce::Font MyLnF::getFont (float h) const {
    return juce::Font (juce::FontOptions (typeface)).withHeight (h);
}

juce::Typeface::Ptr MyLnF::getTypefaceForFont (const juce::Font&) override {
    return typeface;  // force the custom face everywhere
}
```

**Rendering quality.** `setImageResamplingQuality` affects images, not text.
For text quality, the levers are: typeface choice (monospace + hinting-friendly
fonts for small UI like `ShareTechMono`, `JetBrainsMono`), font height
(avoid fractional pixel heights — round to integers), and baseline. Set
`g.setImageResamplingQuality(Graphics::highResamplingQuality)` for scaled
raster assets *around* text, not for text itself.

**Subpixel / kerning.** JUCE uses its own font engine by default. On macOS
with GL detached, text uses CoreText; on Windows, DirectWrite. Subpixel
positioning is controlled by JUCE's internal shaper — disable with
`Font::setDefaultMinimumHorizontalScaleFactor(1.0f)` if you see unexpected
letter-spacing fluctuation.

**Emoji / fallback.** Custom bundled fonts typically lack emoji glyphs. For
icon toggles that use emoji or system symbols, fall back to the platform
default: `Font(FontOptions(Font::getDefaultSansSerifFontName(), h, plain))`.
A lightweight pattern: check a component property flag and switch fonts
inside `drawButtonText`.

## 8. Animation

**Timers.** `juce::Timer` is the canonical clock. Inherit and call
`startTimerHz(60)` (or `startTimer(16)` for ms). Keep timer callbacks
cheap — update state, call `repaint()`, return.

```cpp
class Scope : public juce::Component, private juce::Timer
{
public:
    Scope()  { startTimerHz (30); }
    ~Scope() override { stopTimer(); }
    void timerCallback() override
    {
        ring[writePos] = source.getLatest();
        writePos = (writePos + 1) % ring.size();
        repaint();
    }
};
```

30 Hz is usually enough for modulation scopes and meters; 60 Hz for pointers
on knobs being swept, XY pads, and waveform displays; avoid > 60 Hz unless
you have a specific need and a GL context.

**Per-component animation.** `juce::Desktop::getAnimator()` returns a
shared `ComponentAnimator`. Use
`animator.animateComponent(&comp, targetBounds, endAlpha, durationMs, ...)`
for slide/fade transitions when opening panels or swapping views. Easing is
controlled by `proportionalSpeed` and two Bezier-curve knobs; for more
explicit control, roll your own `Timer` that LERPs on an easing curve
(`std::pow(t, 2.7f)` for ease-in, `1 - std::pow(1 - t, 2.7f)` for ease-out).

**Repaint strategies.** Always `repaint(affectedRegion)` instead of whole
component when possible. For meters that change every timer tick, restrict
to the meter subrect. Use `Component::setBufferedToImage(true)` for heavy
static backgrounds; it caches a rasterised copy and only redraws on resize.

**60 fps discipline.** Budget ≈ 6 ms/frame for paint to leave headroom.
Profile with JUCE's built-in `Graphics::beginTransparencyLayer` only for
short-lived effects — transparency layers allocate; high-frequency use
thrashes the GPU.

## 9. Layout

**FlexBox.** JUCE ports a subset of CSS FlexBox:

```cpp
void MyPanel::resized() {
    juce::FlexBox row;
    row.flexDirection = juce::FlexBox::Direction::row;
    row.justifyContent = juce::FlexBox::JustifyContent::spaceBetween;
    for (auto* k : knobs)
        row.items.add (juce::FlexItem (*k).withMinWidth (56).withFlex (1.0f));
    row.performLayout (getLocalBounds().reduced (8));
}
```

Use FlexBox for one-axis rows (knob strips, transport toolbars).

**Grid.** `juce::Grid` is 2D CSS-grid-like with `templateColumns`, `templateRows`,
`items`, `rowGap`, `columnGap`. Preferred for synth panels (voice mixer, ADSR
grids, mod matrix).

```cpp
juce::Grid g;
using Track = juce::Grid::TrackInfo;
using Fr = juce::Grid::Fr;
g.templateColumns = { Track (Fr(1)), Track (Fr(1)), Track (Fr(1)) };
g.templateRows    = { Track (Fr(1)), Track (Fr(1)) };
g.rowGap = juce::Grid::Px (6);  g.columnGap = juce::Grid::Px (8);
g.items.addArray ({ juce::GridItem (a), juce::GridItem (b), juce::GridItem (c),
                    juce::GridItem (d), juce::GridItem (e), juce::GridItem (f) });
g.performLayout (getLocalBounds());
```

**Constrained bounds.** `Component::setBounds` is authoritative. For responsive
behaviour, always recompute layout in `resized()`. Avoid stashing pixel values
in fields — recompute from `getLocalBounds().reduced(margin)` so a user-zoom
transform flows through.

**Hierarchy tips.** Group related widgets into sub-panels that own their own
`resized()` — keeps each layer tight and makes visual regression localised.

## 10. Cross-Platform Pitfalls

- **Subpixel text rendering.** Windows (DirectWrite) tends toward sharper,
  more contrasty glyph outlines than macOS (CoreText, darker/heavier). Linux
  FreeType is closer to Windows but with coarser hinting. To neutralise:
  render text on integer baselines, avoid small italic faces, and test on
  all three before shipping. Use JUCE's internal rasteriser (no GL) for the
  most consistent cross-platform text; accept it looks slightly softer on
  macOS than CoreText does natively.
- **Stroke anti-aliasing at integer offsets.** macOS/Quartz blurs 1-px lines
  less than JUCE's software renderer; offset by 0.5 consistently. Test at
  1× DPI explicitly (Retina displays will mask issues).
- **Font loading path.** Bundled TTFs render identically everywhere *only if*
  you force `getTypefaceForFont` to return your loaded face. Without that
  hook, JUCE may fall back to the platform default for certain FontOptions
  flags (italic/bold variants you didn't bundle).
- **Emoji and Unicode escapes.** Avoid non-ASCII in `const char*` literals
  — em-dashes, en-dashes, and arrows render as mojibake with some compiler/
  font combinations. Use ASCII (`-`, `->`) or explicit
  `String::fromUTF8(u8"…")`. Never put emoji in files saved as non-UTF-8.
- **GL text.** As noted, text via OpenGLContext is rasterised differently
  on Windows vs. macOS. If you attach GL editor-wide and ship a "text-heavy
  look", plan a QA pass on Windows specifically.
- **DPI transitions.** When a user drags the window between displays of
  different scales, JUCE sends `parentHierarchyChanged` + a repaint. Cache
  any DPI-dependent data (filmstrip variant choice, prebaked backgrounds)
  keyed on the current scale and refresh on this event.
- **Host DAW quirks.** Some hosts resize editors aggressively (Ableton Live
  grid snap, Studio One auto-fit). Implement `AudioProcessorEditor::
  setResizeLimits` and a `ComponentBoundsConstrainer` so proportions hold.
  Pro Tools can detach/reattach the editor window — avoid keeping raw
  native-handle pointers and tear down GL context cleanly in the dtor.

## Quick Checklist for Figma → JUCE Fidelity

1. Export SVG for shapes; use vector `drawRotarySlider` rather than filmstrip
   unless the design has photographic textures.
2. Bundle the exact brand typeface as TTF/OTF via BinaryData; force it
   through `getTypefaceForFont`.
3. Pin colour values into a `ThemeData` struct once; push them into LnF
   colour IDs so Slider/Button/ComboBox inherit automatically.
4. Verify at 1× and 2× DPI on both macOS and Windows before calling it done.
5. Use Grid for panel layout, FlexBox for strips. Recompute in `resized()`
   from `getLocalBounds()` — never cache pixels.
6. Timer at 30 Hz for most scopes/meters; 60 Hz only where visibly needed.
7. GL attachment is a late-stage optimisation, not a default. Measure first.
8. Study Surge XT `SkinSupport`, Vital's skin loader, and `foleys_gui_magic`
   for patterns; write your own code.
