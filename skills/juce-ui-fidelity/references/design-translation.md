# Design → JUCE translation reference

How to get from a design input (HTML/CSS mockup, Figma frame, screenshot, or
design-MCP generation) into JUCE C++ that renders the same pixels. This
reference is input-centric: start from the input type, follow the chain.

## 1. HTML / CSS mockup (Stitch, Figma code export, hand-coded)

### 1.1 Extract before you translate

Do not translate by eyeballing. Extract the numeric values from the running
page first — reading CSS source often misses cascades, defaults, and
inheritance.

Two reliable extraction paths:

**Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__evaluate_script`).
The one-liner below dumps the numbers you actually need for a single
element, as JSON:

```javascript
const el = document.querySelector('#knob-container');
const s = getComputedStyle(el);
const r = el.getBoundingClientRect();
JSON.stringify({
    w: r.width, h: r.height,
    background: s.background,
    color: s.color,
    fontFamily: s.fontFamily,
    fontSize: s.fontSize,
    fontWeight: s.fontWeight,
    letterSpacing: s.letterSpacing,
    borderRadius: s.borderRadius,
    borderTop: s.borderTopWidth + ' ' + s.borderTopStyle + ' ' + s.borderTopColor,
    padding: [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft],
    boxShadow: s.boxShadow,
    opacity: s.opacity,
    transform: s.transform,
}, null, 2);
```

**Playwright MCP** (`mcp__plugin_playwright_playwright__browser_evaluate`). Same
approach, same payload.

Run this for every distinct visual element — the knob container, the arc, the
label, the panel card. You'll end up with a small table of numbers that
feeds the JUCE code directly.

### 1.2 CSS to JUCE cheat-sheet

Values and units:

- `px` → raw float in `Graphics` calls. JUCE works in logical pixels; 1px CSS
  maps to 1 JUCE pixel.
- `rem`, `em` → resolve to px by computing `parseFloat(getComputedStyle(el).fontSize)`.
- `%` → compute against container size and hand in the resulting px.
- `rgb(r,g,b)` / `rgba(r,g,b,a)` → `juce::Colour::fromRGB(r,g,b)` /
  `juce::Colour::fromRGBA(r,g,b, (uint8)(a*255))`.
- `#rrggbb` → `juce::Colour::fromString("FFrrggbb")` or hex literal
  `juce::Colour(0xffRRGGBB)`.
- `hsl(h,s%,l%)` → `juce::Colour::fromHSL(h/360.0f, s/100.0f, l/100.0f, 1.0f)`.

Backgrounds:

- `background: #111;` — `g.setColour(...); g.fillRect/fillAll(bounds);`
- `background: linear-gradient(180deg, #333 0%, #111 100%);`
  ```cpp
  juce::ColourGradient grad (colour("#333"), cx, top,
                             colour("#111"), cx, bottom, false);
  g.setGradientFill(grad);
  g.fillRect(bounds);
  ```
  For angled gradients `90deg + n`, compute the endpoint vector manually:
  CSS 0deg points up, 90deg right. See `juce::ColourGradient::getGeometry`.
- `background: radial-gradient(circle at 50% 30%, #fff 0%, transparent 80%);`
  ```cpp
  juce::ColourGradient grad (colour("#fff"),
                             cx, top + h * 0.30f,
                             juce::Colours::transparentWhite,
                             cx + radius * 0.80f, top + h * 0.30f,
                             true /* isRadial */);
  grad.addColour (0.80, juce::Colours::transparentWhite);
  ```

Borders and radii:

- `border: 1px solid #333;` — `g.setColour(...); g.drawRect(bounds, 1.0f);`
- `border-radius: 8px;` — `g.drawRoundedRectangle(bounds, 8.0f, 1.0f);`
- Mixed radii (`border-radius: 8px 8px 0 0`) — there is no single `Graphics`
  call for this. Build a `juce::Path`:
  ```cpp
  juce::Path p;
  p.startNewSubPath (bounds.getX() + 8.0f, bounds.getY());
  p.lineTo (bounds.getRight() - 8.0f, bounds.getY());
  p.quadraticTo (bounds.getRight(), bounds.getY(),
                 bounds.getRight(), bounds.getY() + 8.0f);
  p.lineTo (bounds.getRight(), bounds.getBottom());
  p.lineTo (bounds.getX(), bounds.getBottom());
  p.lineTo (bounds.getX(), bounds.getY() + 8.0f);
  p.quadraticTo (bounds.getX(), bounds.getY(),
                 bounds.getX() + 8.0f, bounds.getY());
  p.closeSubPath();
  g.fillPath (p);
  ```

Shadows:

- `box-shadow: 0 4px 12px rgba(0,0,0,0.4);` — JUCE has no direct equivalent.
  Two practical approaches:
  1. **`melatonin_blur` (MIT)** — pull in as a JUCE module; one-liner
     `melatonin::DropShadow(colour, radius, offset).render(g, path);`.
  2. **Multi-pass stroke fake**: 3-4 passes of `strokePath` with increasing
     width + decreasing alpha, offset by the shadow delta. Cheap, works
     without modules:
     ```cpp
     for (int i = 0; i < 4; ++i) {
         float w = 2.0f + i * 3.0f;
         float a = 0.35f - i * 0.08f;
         g.setColour (shadowColour.withAlpha (a));
         g.strokePath (path, juce::PathStrokeType (w));
     }
     ```
  3. **For inset shadows** (`inset`), draw a radial gradient from the inner
     edge inward with `Path::setUsingNonZeroWinding(false)` to cut out the
     centre.

Opacity / blending:

- `opacity: 0.6` on an element: call every colour in that element's `paint()`
  with `.withAlpha(0.6f)`.
- For full-subtree opacity, `Graphics::beginTransparencyLayer(0.6f)` + matching
  `endTransparencyLayer()`. Expensive; use sparingly.
- `mix-blend-mode: screen` / `multiply`: use
  `g.setColour(c.with…); g.setFillType(FillType(colour).withTransform(...))` —
  JUCE has limited blend-mode support. For screen blending with a bright
  accent, stacking `colour.brighter(0.x)` on an alpha layer usually gets
  close enough.

Layout:

- `display: flex; flex-direction: row; justify-content: space-between;`
  ```cpp
  juce::FlexBox row;
  row.flexDirection = juce::FlexBox::Direction::row;
  row.justifyContent = juce::FlexBox::JustifyContent::spaceBetween;
  row.items.add (juce::FlexItem(child).withFlex(1));
  row.performLayout (getLocalBounds());
  ```
- `display: grid; grid-template-columns: 1fr 1fr 1fr;`
  ```cpp
  using Fr = juce::Grid::Fr;
  juce::Grid grid;
  grid.templateColumns = { Fr(1), Fr(1), Fr(1) };
  grid.items.add (juce::GridItem(a));
  grid.performLayout (getLocalBounds());
  ```
- `padding: 12px 16px;` — `bounds.reduced(16, 12)` (note JUCE uses (x, y) not
  (y, x)).

Text:

- `font-family: 'Space Grotesk';` → bundle the TTF via
  `juce_add_binary_data`, load with `Typeface::createSystemTypefaceFor`,
  expose through `LookAndFeel::getTypefaceForFont`. See
  `juce-ui-primitives.md §7`.
- `font-size: 12px;` → `Font(FontOptions(typeface)).withHeight(12.0f)`.
- `font-weight: 600;` → `Font(...).withStyle(Font::bold)` if the typeface
  carries a 600-weight face; otherwise ship the bold .ttf and select it by
  name.
- `letter-spacing: 0.04em;` → `Font(...).withExtraKerningFactor(0.04f)`.
- `text-transform: uppercase;` → `str.toUpperCase()` before drawing; there's
  no equivalent `Graphics` flag.

Transforms:

- `transform: rotate(45deg);` → `g.addTransform(AffineTransform::rotation(
  MathConstants<float>::pi * 0.25f, cx, cy));`
- `transform: scale(1.5);` → `g.addTransform(AffineTransform::scale(1.5f));`.

### 1.3 From HTML section to Component boundary

A mockup is usually one HTML document covering a whole editor. Don't make one
monster Component — match the DOM's logical groupings to JUCE Components:

| HTML                          | JUCE                         |
| ----------------------------- | ---------------------------- |
| A section/article card        | A Component subclass         |
| A grid/flex row of controls   | A sub-Component that owns a FlexBox |
| A knob with label             | A Component with a `Slider` + `Label` child |
| A tabbed panel                | `juce::TabbedComponent` or custom tabs + content-swap |
| The overall page frame        | The `AudioProcessorEditor`   |

Bound per logical block, then write one `REGISTER_COMPONENT_SIZED` story per
block per meaningful state (default, edge cases, disabled, etc.).

## 2. Image-only input (screenshot, PNG, nano-banana render)

When there's no HTML, the only source of truth is pixels. Workflow:

1. **Measure on the image.** Open in Preview/GIMP, use the inspector to get
   element sizes and colour samples. For a rotary knob: measure the knob
   diameter, the arc thickness, the tick-mark length, and the panel card
   bounds.
2. **Sample dominant colours.** Use `image_magick identify -format "%c" image.png`
   or a colour picker. Record hex values into a `ThemeData`-compatible palette.
3. **Guess proportions.** Knob body = 78% of the bounding square. Arc radius
   = half the bounding square minus arc thickness. Label height = 10-14% of
   total panel height. These are defaults that match most modern synth
   aesthetics.
4. **Round to sensible values.** 8px corner radii, 1.5px strokes, 12px font
   heights — designers round to common values; using nice round numbers
   looks sharper than exact measurements from a rasterised PNG.
5. **Build, render, diff, iterate.** Same loop as the HTML path.

If the image was generated by nano-banana with a specific style prompt,
preserve the prompt in a comment above the Component so future regenerations
can rhyme.

## 3. Figma frame (SVG or image export)

### 3.1 SVG path

Exporting as SVG gives you structured shapes.

- **For the overall frame**, rasterize to PNG at 2x for the diff target:
  `rsvg-convert -a -w 840 frame.svg > target.png` (then halve in JUCE).
- **For a specific icon or logo**, use it directly as a JUCE Drawable:
  ```cpp
  auto svg = juce::parseXML (juce::String::fromUTF8 (
      BinaryData::iconLogo_svg, BinaryData::iconLogo_svgSize));
  auto drawable = juce::Drawable::createFromSVG (*svg);
  drawable->drawWithin (g, bounds, juce::RectanglePlacement::centred, 1.0f);
  ```
- **For custom glyphs on knob bodies**, import as `Drawable` and rotate it
  with `AffineTransform::rotation(angle, cx, cy)` in `drawRotarySlider`.

### 3.2 Figma "Copy as CSS"

Figma produces usable CSS for individual elements. Treat it the same as a
CSS mockup (§1.2) but be aware Figma sometimes emits CSS that depends on
its flexbox-via-autolayout — read the generated CSS critically.

### 3.3 Figma plugin for colour tokens

If the design uses a design-token system, export via the "Design Tokens"
plugin → JSON, then code-gen a `ThemeData` struct that mirrors the token
names. Keeps colour IDs between design and code perfectly aligned.

## 4. PDF spec

For PDFs (typical for formal design specs / brand guidelines):

```sh
pdftoppm -png -r 288 spec.pdf page    # 288 dpi = 4x
```

This produces `page-1.png`, `page-2.png`, ... Use the page that contains the
frame you need. If the PDF has vector shapes, `pdf2svg page.pdf page.svg`
may preserve them, after which the Figma-SVG path applies.

## 5. Generated-from-scratch (Stitch or nano-banana first)

When no design exists yet:

1. Invoke **Stitch MCP** (`mcp__stitch__generate_screen_from_text` or
   `generate_design`) with a prompt that includes the constraints: target
   size, aesthetic, key elements, brand colours if any. Stitch returns HTML.
2. Rasterize: `render_html.py stitch_output.html --out target.png --size WxH`.
3. Inspect visually; iterate via `edit_screens` or `generate_variants`.
4. Once happy, extract numeric values (§1.1) and proceed with the normal
   translation.

Or:

1. Use **nano-banana** (`mcp__nano-banana-2__generate_image`) for a concept
   image that captures the aesthetic. Nano-banana gives you an image, not
   HTML, so skip to §2 (image-only).
2. Use `mcp__nano-banana-2__edit_image` to iterate on a specific element
   ("make the knob glow more", "darker panel").
3. When stable, extract colour palette + proportions and translate.

**Important**: generation tools give you a *direction*. Do not assume every
pixel of a generated design is intentional — grading at 0.01 threshold against
a Stitch or nano-banana output will chase noise. Treat the generation as a
high-resolution mood-board, relax the threshold (0.05-0.1), and focus the
objective on the elements you genuinely want to match.

## 6. Common translation pitfalls

- **Rendered DPR mismatch.** The mockup rendered at 2x but the JUCE snapshot
  at 1x. Diff shows halos everywhere. Fix: render both at the same DPR.
- **Font swap.** The HTML used a web font that isn't installed; the browser
  substituted. The "design" you captured is wrong before you even start.
  Confirm `document.fonts.ready` resolved before screenshotting.
- **SVG without viewBox.** `Drawable::createFromSVG` rasterizes at the intrinsic
  size; if the source SVG lacks `viewBox`, the Drawable renders at 0×0.
- **CSS `transform` on the parent is lost.** Computed styles include the
  element's own transform but not the parent's. When a container is
  `transform: rotate(2deg)`, read it from the parent too.
- **Sub-pixel rendering differences.** Chromium renders with anti-aliasing
  tuned for subpixel LCDs; JUCE's software rasteriser is slightly "softer".
  Keep odiff's `--antialiasing` flag on and threshold at 0.01 minimum.
- **Treating colour-pickers as authoritative.** On JPG or heavily-compressed
  PNG sources, sampled colours are approximate — round to the nearest 16 in
  each channel to recover the designer's intended value.
