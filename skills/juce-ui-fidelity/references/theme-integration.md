# Theme integration reference

How to plug new Components and LookAndFeel overrides into an existing theme
system without introducing ad-hoc colour state or breaking theme swaps.
Concrete examples use a generic `ProjectLookAndFeel` + `ThemeData` pairing,
which is representative of a mature JUCE theme architecture — adapt the names
to whatever your project calls its central LookAndFeel subclass.

## 1. The theme system in one paragraph

A well-formed JUCE theme system typically looks like:

- A `ThemeData` struct holds every colour, radius, border-width, and drawing
  style variant the UI reads. Themes are data, not classes.
- A `LookAndFeel_V4` subclass owns a pointer or reference to the active
  theme and copies colour values into JUCE's colour-ID system on theme
  change.
- Components never hardcode colours. They either use JUCE's standard colour
  IDs (`Slider::thumbColourId`, `TextButton::buttonColourId`) or read from
  the theme directly via a `LookAndFeel*` accessor.
- Swapping themes is one `setTheme(newTheme)` call plus a `repaint()`. The
  whole UI re-colours because the colour IDs refreshed and every Component
  reads from them.

Violating this — hardcoding `juce::Colour(0xff112233)` in a `paint()` — makes
that Component immune to theme changes and breaks the system. Don't do it,
even "temporarily".

## 2. Where to put colour for a new Component

### 2.1 Prefer standard JUCE colour IDs

Every `juce::Slider`, `juce::Button`, `juce::Label`, etc. already has colour
IDs the LookAndFeel sets. If your Component wraps one of these, the LookAndFeel
already drives its colours — you don't need to write any colour code:

```cpp
// No custom paint needed. The existing LookAndFeel_V4 subclass has already
// set Slider::rotarySliderFillColourId to theme.colors.knobArc via
// setColour() in applyThemeColours(). The slider picks it up.
slider.setSliderStyle (juce::Slider::RotaryVerticalDrag);
addAndMakeVisible (slider);
```

### 2.2 When the Component paints itself, read from the active theme

Custom Components that draw their own chrome should read from the LookAndFeel
rather than hardcoding. Two idioms:

**Via `findColour` on the Component** (preferred — no LookAndFeel coupling):

```cpp
class FilterCurveDisplay : public juce::Component
{
public:
    enum ColourIds
    {
        curveColourId    = 0x9a00001,
        gridColourId     = 0x9a00002,
        backgroundColourId = 0x9a00003,
    };

    void paint (juce::Graphics& g) override
    {
        g.fillAll (findColour (backgroundColourId));
        g.setColour (findColour (gridColourId));
        // ... draw grid ...
        g.setColour (findColour (curveColourId));
        // ... draw curve ...
    }
};
```

Then the LookAndFeel's `applyThemeColours()` pushes values in:

```cpp
setColour (FilterCurveDisplay::backgroundColourId, c.panelBg);
setColour (FilterCurveDisplay::gridColourId,       c.panelBorder.withAlpha(0.4f));
setColour (FilterCurveDisplay::curveColourId,      c.accent1);
```

**Via a typed cast of LookAndFeel** (when the Component needs non-colour theme
data like `cornerRadius` or `DrawingStyle`):

```cpp
void paint (juce::Graphics& g) override
{
    if (auto* lnf = dynamic_cast<ProjectLookAndFeel*> (&getLookAndFeel()))
    {
        const auto& c = lnf->getTheme().colors;
        const auto style = lnf->getTheme().style;
        // use c.knobBody, style, etc.
    }
}
```

The cast is acceptable when the Component is part of the same plugin as the
LookAndFeel (it's coupling to your own type). Don't write this pattern for
Components that might be reused across plugins with different LookAndFeels.

### 2.3 Don't introduce a "theme2" singleton

Resist adding a parallel colour system for a single component. If the current
`ThemeData` is missing a colour you need, **add it to `ThemeData`** and update
every theme to supply it. Single source of truth.

## 3. Drawing-style variants

Some theme systems carry a `DrawingStyle` enum (e.g.
`Beveled / Flat / Phosphor / Neon`) that switches the visual language — not
just colours, but whole stroke / gradient / fill strategies.

When adding a new Component or LookAndFeel override:

- **If the Component renders something new**, implement all style variants
  — a switch on `activeTheme->style` with a case per value. Match the
  aesthetic of each: Beveled gets bevel lines, Flat gets a flat fill, Phosphor
  gets faint glow, Neon gets the full multi-pass bloom.
- **If the Component defers to existing primitives** (e.g. uses `fillRoundedRectangle`
  with theme colours), the style difference is already captured by the
  theme's `cornerRadius`, `borderWidth`, etc. No variant code needed.
- **Test every variant.** The snapshot harness makes this cheap — add one
  `REGISTER_COMPONENT_SIZED(MyComponent_Beveled, ...)`,
  `REGISTER_COMPONENT_SIZED(MyComponent_Flat, ...)`, etc. per style:

```cpp
static auto makeFilterPanel (ThemeData::Style style)
{
    auto c = std::make_unique<FilterPanel>();
    // Each story instantiates a dedicated LookAndFeel with the target theme
    // pre-selected, so the snapshot reflects the style under test.
    static ProjectLookAndFeel lnf[4];
    static std::once_flag once;
    std::call_once (once, []{
        for (int i = 0; i < 4; ++i)
            lnf[i].setTheme (Themes::bundled()[i]);
    });
    c->setLookAndFeel (&lnf[(int) style]);
    return c;
}

REGISTER_COMPONENT_SIZED (FilterPanel_Beveled,  []{ return makeFilterPanel (ThemeData::Style::Beveled); }, 420, 240);
REGISTER_COMPONENT_SIZED (FilterPanel_Flat,     []{ return makeFilterPanel (ThemeData::Style::Flat); }, 420, 240);
REGISTER_COMPONENT_SIZED (FilterPanel_Phosphor, []{ return makeFilterPanel (ThemeData::Style::Phosphor); }, 420, 240);
REGISTER_COMPONENT_SIZED (FilterPanel_Neon,     []{ return makeFilterPanel (ThemeData::Style::Neon); }, 420, 240);
```

## 4. Fonts in a themed system

Bundled fonts are part of the theme, not free-floating assets. A
representative pattern:

- LookAndFeel owns `juce::Typeface::Ptr` for each bundled face.
- A `getActiveTypeface()` accessor returns the typeface named in
  `activeTheme->fontName`.
- `getTypefaceForFont()` is overridden to return the active face
  unconditionally (so JUCE's fallback path can't silently pick a platform
  default).
- `getThemeFont(height)` returns a `juce::Font` with the active typeface and
  the requested height.

When you add a Component that paints text, use the LookAndFeel's `getThemeFont`
helper — do not construct `juce::Font` directly with a face name. Two reasons:

1. The face-name string lookup can silently miss on machines where the font
   isn't installed. `getThemeFont` uses the in-memory bundled face.
2. Theme changes need to re-trigger font selection. If you construct Fonts
   inline with a hardcoded name, theme swaps leave old fonts alive until
   `repaint()`.

## 5. Adding a new theme colour

1. Add the field to `ThemeData::Colors`:
   ```cpp
   struct Colors {
       juce::Colour panelBg;
       juce::Colour panelBorder;
       // ...
       juce::Colour sequencerStepOn;    // new
       juce::Colour sequencerStepOff;   // new
   };
   ```

2. Populate it in every bundled theme in `Themes.cpp` / `Themes::createBundledThemes()`.
   Missing a theme means that theme renders your colour as default-initialised
   (typically transparent black).

3. Add a colour ID for any Component that uses it, and push it in
   `applyThemeColours()`:
   ```cpp
   setColour (SequencerPanel::stepOnColourId,  c.sequencerStepOn);
   setColour (SequencerPanel::stepOffColourId, c.sequencerStepOff);
   ```

4. Commit the colour across themes + the ID + the component edit in **one
   change**. Splitting them leaves the repo in a state where one theme
   renders correctly and others don't.

## 6. Respecting the project's naming rules

Most serious projects standardise on domain-specific UI terminology. Typical
examples to look out for in a synth/plugin repo:

- **Component labels**: a project may mandate `VCO`/`VCF` over
  `OSC`/`Filter`, `MIX` over `LEVEL`, etc. These appear in `drawText` calls,
  button labels, panel titles, and modulation destination names.
- **Per-control labels**: consistent short names for common parameters
  (`FREQ`, `FINE`, `PAN`, `VOL`, standard ADSR for envelopes).
- **ASCII-only C++ string literals**: em-dashes, en-dashes, arrows, emoji
  break font rendering on some platform/compiler combos. Use `-`, `->`, or
  wrap Unicode in `juce::String::fromUTF8(u8"...")`.

Check the project's `CLAUDE.md` / `AGENTS.md` / style guide for the specific
terminology. If the mockup disagrees with the project's convention, follow the
project's convention — the mockup's literal text is wrong and should be fixed
in the JUCE port.

## 7. Theme-aware snapshots — golden-per-theme

Visual regression tests are most useful when they cover every theme variant.
Strategy:

- Organise goldens as `tests/snapshots/golden/<ThemeName>/<Story>.png`.
- Extend the driver script to iterate themes and set the LookAndFeel before
  rendering each story. Or pass the theme name into the story factory via
  harness argv.
- CI gates on the default theme; treat other themes as "must-render-without-
  crashing" with a looser threshold (0.1), since a small cosmetic drift in
  a non-default theme is not ship-blocking.

## 8. Semantically-fixed colours (red meters, amber warnings, etc.)

Some UI elements are coloured by *meaning*, not by theme — a gain-reduction
meter is red because "red = reducing gain" is a conventional signal, a clip
indicator is always red, a warning label is amber. These don't need to
follow the theme's accent palette, but they still should not be raw hex
literals scattered through `paint()`.

Pattern: define a small co-located struct of semantic colours on the
Component itself, initialised with sensible defaults, settable for
customisation:

```cpp
class CompressorEditor : public juce::Component
{
public:
    struct MeterColours
    {
        juce::Colour high   { 0xffff5150 };  // saturated red
        juce::Colour mid    { 0xffff8080 };  // warm orange
        juce::Colour low    { 0xff801018 };  // deep red trough
        juce::Colour track  { 0xff101014 };
    };

    void setMeterColours (MeterColours c) { meterColours = c; repaint(); }

private:
    MeterColours meterColours;
};
```

Then `paint()` reads `meterColours.high`, not `juce::Colour(0xffff5150)`.
This keeps the "this is red because compressors are red" intent visible,
while still letting a theme or user preference swap in different red
shades (Phosphor theme might want a more phosphor-green "reducing"
indicator; Beveled theme might want muted burgundy).

Rule of thumb: **zero raw hex literals inside `paint()` / draw methods**,
even for semantically-fixed colours. Either push them to ThemeData (for
theme-aware colours) or to a local struct (for semantically-fixed).

## 9. Common mistakes

- **Hardcoding a "temporary" colour.** It will never get replaced. Add a
  ThemeData field even for one-off components.
- **Relying on `findColour` without a colour ID.** Returns
  `Colours::transparentBlack` — invisible. Always declare a `ColourIds` enum
  with a unique ID per colour.
- **Forgetting `setLookAndFeel(nullptr)` in the dtor.** If a child Component
  outlives the LookAndFeel, you get a use-after-free on the next repaint.
  JUCE's pattern is: set in ctor, clear in dtor. Always.
- **Using a theme colour directly, then brightening/alpha-ing it in one spot.**
  `c.accent1.withAlpha(0.4f)` in 30 places across the codebase means a theme
  tweak touches 30 files. Prefer exposing the computed variant as its own
  `ThemeData` field (`c.accent1Dim`).
- **Copying `drawRotarySlider` from another LookAndFeel wholesale.** Works
  for the moment, then diverges from the rest of the project's visual
  language. Extend the project's existing `drawRotarySlider` with new
  behaviour controlled by a `ThemeData` flag, not a parallel LookAndFeel.
