# Fast screenshot-based testing loop for JUCE UI components

A practitioner's reference for building a PNG-snapshot / design-diff testing
workflow for `juce::Component` in C++. Scope: the "I designed this in Figma /
Stitch, now prove my Component matches" loop, plus visual regression against
a frozen golden.

Line references below point to JUCE 8.0.6 sources (typically vendored under
`build/_deps/juce-src/modules/...` by CMake's FetchContent). Sanity-check
anything in this doc against the actual source in your own project.

---

## 1. Rendering a `Component` to an image headlessly

### 1.1 The two APIs you actually need

From `juce_gui_basics/components/juce_Component.h`:

```cpp
/** Generates a snapshot of part of this component. */
juce::Image createComponentSnapshot (juce::Rectangle<int> areaToGrab,
                                     bool clipImageToComponentBounds = true,
                                     float scaleFactor = 1.0f);

/** Draws this component and all its subcomponents onto the specified graphics
    context. */
void paintEntireComponent (juce::Graphics& context, bool ignoreAlphaLevel);
```

The one-line recipe is literally what JUCE itself does internally
(`juce_Component.cpp:1790`):

```cpp
juce::Image Component::createComponentSnapshot (Rectangle<int> r, bool clip, float scale)
{
    // clip, compute w/h, allocate image (ARGB or RGB depending on opaqueFlag)
    juce::Image image (flags.opaqueFlag ? Image::RGB : Image::ARGB, w, h, true);
    juce::Graphics g (image);
    if (w != getWidth() || h != getHeight())
        g.addTransform (AffineTransform::scale (...));
    g.setOrigin (-r.getPosition());
    paintEntireComponent (g, true);
    return image;
}
```

So `createComponentSnapshot` is a ~20-line wrapper around `paintEntireComponent`
into a `juce::Image`. There is no Peer, no HWND/NSView/X11 window — the image is
purely an offscreen pixel buffer. Which is what makes a headless CI snapshot
workflow viable at all.

### 1.2 Does it work without a display?

Short answer: yes on Linux and Windows; mostly yes on macOS with caveats.

You still have to:

1. Construct a `juce::ScopedJuceInitialiser_GUI` (from
   `juce_events/messages/juce_Initialisation.h:81`). This brings up the
   `MessageManager` and platform-specific GUI infrastructure JUCE needs to
   initialise fonts, `LookAndFeel_V4`, etc. Without it, a lot of `paint()` code
   paths assert or crash.
2. Hold the message thread lock while you drive Component code, because some
   internals (async repaint coalescing, timers the Component starts in its
   constructor, etc.) assume MM-thread identity. Idiomatic pattern:
   `juce::MessageManagerLock` on the stack.
3. Never add the component to a `DocumentWindow` or request a `ComponentPeer` —
   that's what actually tries to talk to the windowing system. `paintEntireComponent`
   / `createComponentSnapshot` do not.

Platform gotchas worth being concrete about:

- **macOS**: `ScopedJuceInitialiser_GUI` creates an `NSApplication` singleton and
  expects to run as a GUI process. On a CI runner with no GUI session at all
  (e.g. a Mac mini that auto-boots to LoginWindow), things that only require
  `NSApplication` work, but anything that touches `WindowServer` does not. The
  canonical JUCE forum symptom is "pluginval fails on macOS if screen sharing
  not connected"
  (<https://forum.juce.com/t/pluginval-fails-on-macos-if-screen-sharing-not-connected/55557>)
  — that's pluginval instantiating an editor (peer + window), which we do NOT
  do in the snapshot harness, so we sidestep that failure mode. GitHub's
  `macos-14` hosted runners do have a WindowServer (auto-login user),
  so Pamplejuce's CI works out-of-the-box for this reason.
- **macOS font smoothing**: `CoreGraphicsContext_mac.mm:233` references
  `JUCE_DISABLE_COREGRAPHICS_FONT_SMOOTHING` (config flag in
  `juce_graphics.h:81`). Set this to **1** in snapshot builds or you will get
  nondeterministic subpixel AA depending on LCD orientation, Retina scale, and
  even the macOS point release. This is probably the single most important
  knob for cross-machine snapshot stability.
- **Linux**: `juce_Image.cpp:383` shows `NativeImageType::create` on Linux
  returns a `SoftwarePixelData` — exactly the same rasterizer JUCE uses
  everywhere, with no GPU path. No display needed to allocate or draw into it.
  BUT `initialiseJuce_GUI` on Linux opens an X11 display connection for font
  enumeration and clipboard initialisation — so you still need `xvfb`
  (virtual framebuffer) or a real `$DISPLAY`. In practice just run under
  `xvfb-run` or `Xvfb :99 -screen 0 1024x768x24 &; export DISPLAY=:99`.
  Pamplejuce does exactly this
  (`.github/workflows/build_and_test.yml`: `sudo /usr/bin/Xvfb $DISPLAY &`).
- **Windows**: `NativeImageType::create` on Windows is in
  `juce_Direct2DImage_windows.cpp:656` and it tries to create a
  Direct2D-backed pixel buffer. If the DXGI factory isn't available (which
  happens inside DllMain or, importantly, inside CI session-0 services) it
  falls back to `SoftwarePixelData`. For snapshot tests you explicitly want
  the software fallback so your Windows CI byte-matches developer machines.
  You get that for free by forcing the image type (see next point).

### 1.3 Determinism: force `SoftwareImageType`

This is the second critical lever for cross-platform/cross-machine stability.

`createComponentSnapshot` internally allocates `juce::Image (ARGB, w, h, true)`
which uses `NativeImageType` — CoreGraphics on macOS, Direct2D on Windows,
software on Linux/Android. Three different rasterizers → three different
pixel outputs for the exact same `paint()` code. Instead, do the 5-line
equivalent yourself and force software:

```cpp
juce::Image img (juce::Image::ARGB, w, h, true, juce::SoftwareImageType{});
juce::Graphics g (img);
component.paintEntireComponent (g, true);
```

(`SoftwareImageType` is declared in `juce_Image.h:563`, implementation
in `juce_Image.cpp:364`.)

Caveats:

- `juce::Typeface` / text rasterization still goes through the platform font
  engine even when you're drawing into a software image. On macOS that's
  CoreText, on Windows DirectWrite, on Linux FreeType. If you want bit-identical
  text across OSes, ship a custom `Typeface` loaded from a known `.ttf` /
  `.otf` in your test resources and install it as the default via
  `LookAndFeel::setDefaultLookAndFeel` + `Font::setDefaultMinimumHorizontalScaleFactor`.
  Realistically most teams don't go this far; they accept per-OS goldens and
  run the test suite on one reference OS for PR gating.
- Gradients, blurs, and anti-aliased curves are platform-independent in
  software rasterization, so even without custom fonts you'll get ~99.9% pixel
  equivalence across machines for anything that isn't text.

### 1.4 OpenGL / accelerated renderer interaction

If your Component attaches a `juce::OpenGLContext` for its own rendering, the
snapshot will NOT capture that GL-drawn content, because there's no Peer →
no context actually attached. Two options:

- For tests, detect `JUCE_VISUAL_TEST_HARNESS=1` via a preprocessor define and
  skip the `openGLContext.attachTo(...)` call. The Component then falls back
  to the software painter you already implemented in `paint()`.
- Or render a still frame of the GL content into a `juce::OpenGLFrameBuffer`
  offscreen, then `g.drawImage()` it during `paint()`. Harder; only worth it
  if the GL view is the thing you're testing.

---

## 2. Minimal test harness

### 2.1 The reference 90-line harness

Self-contained, no test framework, no external deps, just `juce_gui_basics`:

```cpp
// snapshot_main.cpp — build this as a juce_add_console_app or juce_add_gui_app
// target that links juce::juce_gui_basics + juce::juce_graphics.
// Invoke: ./snapshot <component_name> <width> <height> <out.png>

#include <juce_gui_basics/juce_gui_basics.h>
#include <functional>
#include <unordered_map>
#include <iostream>

namespace snap
{
    using Factory = std::function<std::unique_ptr<juce::Component>()>;

    inline std::unordered_map<std::string, Factory>& registry()
    {
        static std::unordered_map<std::string, Factory> r;
        return r;
    }

    struct Register
    {
        Register (const char* name, Factory f) { registry().emplace (name, std::move (f)); }
    };

    // REGISTER_COMPONENT(MyKnob, []{ return std::make_unique<MyKnob>(); });
    #define REGISTER_COMPONENT(id, factory) \
        static ::snap::Register reg_##id { #id, factory }

    inline int renderToFile (const std::string& name, int w, int h, const juce::File& out)
    {
        auto it = registry().find (name);
        if (it == registry().end())
        {
            std::cerr << "unknown component: " << name << "\n";
            return 2;
        }

        auto component = it->second();
        component->setSize (w, h);
        // Give async timers / layout one pump. A real editor often needs this.
        juce::MessageManager::getInstance()->runDispatchLoopUntil (16);

        // Force SoftwareImageType for reproducibility across platforms.
        juce::Image img (juce::Image::ARGB, w, h, /*clear*/true, juce::SoftwareImageType{});
        {
            juce::Graphics g (img);
            component->paintEntireComponent (g, true);
        }

        juce::PNGImageFormat png;
        out.deleteFile();
        juce::FileOutputStream fs (out);
        if (! fs.openedOk()) { std::cerr << "cannot open " << out.getFullPathName() << "\n"; return 3; }
        return png.writeImageToStream (img, fs) ? 0 : 4;
    }
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI initialiser; // MM + LookAndFeel + fonts

    if (argc < 5)
    {
        std::cerr << "usage: snapshot <name> <w> <h> <out.png>\n";
        for (auto& [k, _] : snap::registry())
            std::cerr << "  registered: " << k << "\n";
        return 1;
    }

    return snap::renderToFile (argv[1],
                                          std::atoi (argv[2]),
                                          std::atoi (argv[3]),
                                          juce::File::getCurrentWorkingDirectory()
                                              .getChildFile (argv[4]));
}
```

And one-line-per-component registration next to each component:

```cpp
// in MyKnob.cpp (guarded so plugin builds don't pull it in)
#if JUCE_SNAPSHOT_HARNESS
  REGISTER_COMPONENT (MyKnob_Default, []{
      auto c = std::make_unique<MyKnob>();
      c->setValue (0.7f);
      return c;
  });
  REGISTER_COMPONENT (MyKnob_AtZero, []{
      auto c = std::make_unique<MyKnob>();
      c->setValue (0.0f);
      return c;
  });
#endif
```

Build the harness once as a target with `-DJUCE_SNAPSHOT_HARNESS=1`. From then
on, developers write a new component + one REGISTER_COMPONENT call to get a
`./snapshot MyKnob_Default 200 200 out.png` invocation.

### 2.2 Keeping the rebuild fast

Three tiers of pain, pick based on how often you iterate:

1. **Share an OBJECT library**. Instead of rebuilding all your UI code twice
   (once in the plugin, once in the harness), factor UI code into an
   `add_library(plugin_ui OBJECT ...)`, link that into both `juce_add_plugin`
   and the harness executable. Second compilation vanishes.
2. **ccache + sccache**. Pamplejuce uses sccache on CI for the same effect.
   Nothing special needed — set `CMAKE_CXX_COMPILER_LAUNCHER=ccache` at the
   top of your `CMakeLists.txt`.
3. **One target per story, with PCH**. If a single `libplugin_ui.a` is too big
   and you find yourself rebuilding 3000 translation units whenever you touch
   one component, shard the library: `add_library(plugin_ui_knob OBJECT
   MyKnob.cpp)` and link each into its own harness-per-component. Combine with
   `target_precompile_headers (plugin_ui_knob PRIVATE <juce_gui_basics/juce_gui_basics.h>)`
   to kill the 2-3 s of JUCE header parse time each TU. Overkill until you
   have 30+ Components. Don't premature-optimise.

Concrete numbers from real JUCE projects: ccache cold build of a mid-sized
plugin (~150 TU) is 3-5 minutes, warm `edit-one-file` is 3-10 s, and the
harness incremental link is usually the dominant term. Ninja does not make
the individual compiles faster but it saturates cores better than Make or
Xcode's build system, so prefer `-G Ninja`.

---

## 3. Headless CI — what each platform actually needs

### 3.1 Linux (GitHub `ubuntu-22.04` / `ubuntu-latest`)

Exactly what Pamplejuce does. From its workflow:

```yaml
- name: Install deps
  run: |
    sudo apt-get install libasound2-dev libx11-dev libxinerama-dev \
        libxext-dev libfreetype6-dev libwebkit2gtk-4.1-dev \
        libglu1-mesa-dev xvfb ninja-build
    sudo /usr/bin/Xvfb :0 -screen 0 1920x1080x24 &
env:
  DISPLAY: :0
```

That is the whole story for Linux. `xvfb` creates a 1920×1080 virtual X
display into memory, JUCE connects to it for font enumeration, and
`SoftwareImageType` renders into a regular `juce::Image` buffer with no GPU
involvement.

### 3.2 macOS (GitHub `macos-14`, `macos-15`)

GitHub's hosted macOS runners auto-login a user and run a full WindowServer,
so `NSApplication`, CoreText, and offscreen `CGContext` rendering all work. No
special setup needed. Just build, run, diff.

If you ever need to run snapshot tests on a **self-hosted headless Mac mini**:
the failure mode is the one Roland Rabien ran into —
pluginval / any code that tries to create a real window will time out after
30 s. Fix by:

1. Enable "Automatic Login" in System Settings so WindowServer starts at boot.
2. Or add `caffeinate` + unlock keychain at session start.

Snapshot tests that use only `paintEntireComponent` (no Peer) work on a
lidded MacBook without screen sharing; they only start failing when you add
a `juce::DocumentWindow`.

### 3.3 Windows (GitHub `windows-latest`)

No special work needed for the snapshot harness. `NativeImageType::create`
detects a missing DXGI factory and falls back to software
(`juce_Direct2DImage_windows.cpp:656-671`). You should still explicitly
construct images with `SoftwareImageType{}` so the developer machine's GPU
path doesn't diverge from CI's software path.

### 3.4 Standard practice summary

| Platform | Needs display? | Recommended runner | Extra setup |
| --- | --- | --- | --- |
| Linux | Virtual only | `ubuntu-22.04` + `xvfb` | `DISPLAY=:0`, `xvfb-run` |
| macOS | Auto-login user session | `macos-14` | none on hosted runners |
| Windows | No | `windows-latest` | `SoftwareImageType` explicit |

---

## 4. Visual diff tools — actionable comparison

Goals: get a pixel diff ratio you can gate CI on, and a visual overlay image
you can look at in the PR.

| Tool | Language / install | Speed | Anti-aliasing | Output | Fit for JUCE UI |
| --- | --- | --- | --- | --- | --- |
| **odiff** (`odiff-bin`) | Zig/SIMD, `brew install odiff` or `npm i -g odiff-bin` | 6× faster than pixelmatch on large screenshots | YIQ + AA detection, explicit `--antialiasing` | PNG diff + JSON `{match, diffPercentage}` | **Best default for JUCE UIs.** AA-aware diff is what you want for sub-pixel text on retina snapshots. |
| **pixelmatch** | JS, `npm i -g pixelmatch` | Fast on small, doesn't scale | YIQ + explicit `includeAA` flag | PNG diff, ratio via JSON wrapper | Good. More common in web tooling but works fine here. |
| **ImageMagick `compare`** | C, `brew install imagemagick` | Slowest on large screenshots | `-metric AE -fuzz 2%` gives pixel count w/ tolerance | PNG overlay (`-compose src-over`) + numeric metric | Use if you already have IM and don't want another dep. Not AA-smart. |
| **perceptualdiff** (`perceptual-diff`) | C++, `brew install perceptualdiff` | Medium | Perceptual luminance model (Yee et al.) | Diff PNG, pass/fail | Was popular in 2010s; largely superseded by odiff. |
| **resemblejs** / **reg-cli** | JS | Medium | Yes | HTML report | Best when you want a browsable gallery on PRs. reg-suit = GitHub bot. |
| **Built-in pixel compare** (in `juce-visual-regressions`) | C++ in-process | Slow (single-threaded naive loop) | No | Diff image + ratio | Fine for tiny tests, don't scale past 100 snapshots. |

#### Recommendation: odiff

```bash
odiff --antialiasing --threshold 0.05 \
      --diff-color "#ff00ff" \
      test/snapshots/golden/MyKnob_Default.png \
      test/snapshots/current/MyKnob_Default.png \
      test/snapshots/diff/MyKnob_Default.png
# exit 0 = match, exit 21 = layout mismatch, exit 22 = pixel diff
# stdout: `{"match":false, "reason":"pixel-diff", "diffCount":..., "diffPercentage":...}`
```

That's all. Exit code drives CI gating, the diff PNG is what you put in the PR
comment. `--threshold 0.05` is pretty lax; start at 0.1 and tighten as your
snapshots stabilise.

#### Invocation pattern with JSON output

```bash
result=$(odiff --antialiasing \
  "$GOLDEN/MyKnob.png" "$CURRENT/MyKnob.png" "$DIFF/MyKnob.png" \
  --output-format json)
pct=$(jq '.diffPercentage // 0' <<< "$result")
awk "BEGIN { exit ($pct > 1.0) ? 1 : 0 }" || {
    echo "snapshot diff $pct% exceeded threshold"; exit 1;
}
```

---

## 5. Prior art in the JUCE ecosystem

- **`yamadapc/juce-visual-regressions`** (MIT,
  <https://github.com/yamadapc/juce-visual-regressions>). Explicitly the
  closest prior art. Ships two features:
  - `runComponentSnapshotTest(name, factory)` — wraps
    `createComponentSnapshot` → PNG → built-in naive pixel compare with 15%
    threshold (!), writes diff overlay. Organised as `test/visual-regression/{current,stable,diff}/`.
  - A "Storybook" app target where you register Components at compile time
    with `STORY("name"){ return new MyComponent(); }` and get a sidebar
    tree to click through. Similar idea to the registration pattern I
    describe in §2.1.
  - Pre-alpha and hasn't been updated since mid-2024, but the core file
    `src/juce_visual_regressions/SnapshotTester.cpp` is ~100 lines and a
    very readable reference. MIT-licensed so you can vendor it if you like.

- **Pamplejuce** (<https://github.com/sudara/pamplejuce>). The de-facto JUCE
  plugin template. Does **not** ship visual regression out of the box, but its
  CI template (`.github/workflows/build_and_test.yml`) is the template for any
  JUCE CI: sccache, xvfb, pluginval, Catch2, macOS/Linux/Windows matrix. If
  you bolt a snapshot harness onto Pamplejuce you get CI for free.

- **Melatonin Inspector** (<https://github.com/sudara/melatonin_inspector>).
  Runtime dev tool — click components, see bounds, edit colours, overlay an
  FPS meter and per-component paint timings. Not a visual regression tool,
  but it's the Chrome DevTools of JUCE and belongs in your iteration loop
  anyway (see §7).

- **Surge XT** uses Catch2 for its unit tests and runs pluginval on CI, but
  as of mid-2026 it has no published visual regression framework — most of
  their UI testing is manual + community-driven. Don't expect a borrowable
  pattern there.

- **Tracktion Engine** / **CHOC** (choc::gui). Out of scope; neither ships
  visual regression helpers.

Bottom line: the space is sparse. Expect to build it yourself from the
~100-line `SnapshotTester.cpp` pattern, wire up odiff, and call it done.

---

## 6. Alternative: screenshot a real plugin editor via OS automation

A different axis of trade-offs. Instead of rendering a headless `Component`,
load the plugin into a host (AudioPluginHost, pluginval, Reaper) and
screenshot the editor window via the OS.

#### macOS

```bash
# Launch the standalone build, give it time to open, grab the window.
open ./Builds/MyPlugin_artefacts/Standalone/MyPlugin.app
sleep 2
# by window id (most reliable):
win=$(osascript -e 'tell application "System Events" to get id of first window of process "MyPlugin"')
screencapture -l "$win" -o -x /tmp/mac_editor.png
# or by screen region if you know the layout:
screencapture -R0,0,800,600 -x /tmp/editor.png
```

#### Linux

```bash
Xvfb :0 -screen 0 1920x1080x24 &
DISPLAY=:0 ./MyPlugin &
sleep 2
DISPLAY=:0 import -window root /tmp/linux_editor.png   # ImageMagick
# or xdotool + scrot/gnome-screenshot
```

#### Windows

```powershell
Start-Process .\Builds\MyPlugin_artefacts\Release\Standalone\MyPlugin.exe
Start-Sleep -s 2
# Use nircmd (nirsoft.net, MIT) or PowerShell + System.Drawing
nircmd.exe savescreenshotwin "/tmp/win_editor.png"
```

#### When this approach is better

- You're testing **the full plugin surface** — editor instantiation,
  parameter <-> UI binding, async preset loading. Things a pure
  Component snapshot misses.
- You need to test host-integration behaviour (resizing, close/reopen).

#### When it's worse

- **2-4× slower per test** than the in-process Component snapshot
  (spawn a process, wait for the window, sync to a known state, grab pixels,
  tear down).
- **Flaky**. Anything involving `sleep` and window managers has a non-trivial
  false-positive rate. Async parameter-driven repaints complicate "steady
  state" detection.
- **Harder to iterate on**. A failing snapshot requires you to reproduce
  DAW/window state, not just "call `setValue(0.7)`".
- **Not composable**. You can't snapshot only `MyKnob` in isolation; you
  always get the whole editor, which means adding an unrelated button
  invalidates every golden.

Use it for one or two **end-to-end smoke tests** per plugin. Use the
in-process harness for everything else.

---

## 7. Fast iteration — making the edit-compile-look loop tolerable

JUCE's long compile times are the real enemy. Ordered by ROI:

1. **Standalone target, not VST3/AU, for dev.** Per Melatonin: "The standalone
   is the fastest plugin format to iterate on, in part because it doesn't have
   to be started up within a host." In CMake, add `Standalone` to `FORMATS`.
2. **`ccache`.** Cache compiled object files keyed on source + flags. 10-20×
   speedup on the second build. Cost: one line in CMake.
3. **`-G Ninja`.** Better parallelism than Make / Xcode, cleaner dep graph,
   faster null builds. Cost: `brew install ninja` + CMake flag.
4. **`sccache` on CI.** ccache's distributed cousin, backed by S3 or GitHub
   Actions cache. What Pamplejuce uses. Cost: `mozilla-actions/sccache-action@v0.0.9`
   + `CMAKE_CXX_COMPILER_LAUNCHER=sccache`.
5. **PCH on the snapshot harness.** `target_precompile_headers(snapshot PRIVATE
   <juce_gui_basics/juce_gui_basics.h>)`. Saves ~2 s per TU you touch. Cost: one
   CMake line.
6. **`JUCE_LIVE_CONSTANT` for values in-flight.** Wrap magic numbers in
   `JUCE_LIVE_CONSTANT (value)` — you get a live UI for tuning them without
   rebuilding. Melatonin swears by it. Cost: one macro.
7. **Melatonin Inspector for layout.** Point-n-click component introspection,
   padding visualisation, per-component paint timing. This is the "Chrome
   DevTools" loop — much faster than rebuild-and-look when you're
   dialing in geometry. Cost: FetchContent one CMake module.
8. **Component playground.** A GUI-app target that shows a grid of all
   registered components (same registry as §2.1) with a search box. Press `R`
   to reload one. Combined with a file watcher that triggers
   `cmake --build . --target snapshot_MyKnob` on save, you get 1-3 s round
   trips for "tweak paint() → see result".
9. **Unity builds (`CMAKE_UNITY_BUILD=ON`).** Large wins on clean builds
   (smash 10 TUs into one, save on header re-parsing). Zero effect on
   incremental builds because editing any file in a unity batch invalidates
   the whole batch. Use only for CI clean builds, never for dev. Cost: one
   CMake flag, some one-time fixups for ODR violations.
10. **Split into CMake sub-libraries**. At scale, group UI by panel
    (`plugin_ui_synth`, `plugin_ui_fx`) so rebuilding one panel doesn't
    relink your entire editor. Cost: CMake restructuring, non-trivial.

---

## 8. Recommended concrete workflow

Here's "the right default" — everything above distilled into one opinionated
setup.

### Layout

```
product/myplugin/
  source/ui/...                 # your Components
  tests/snapshots/
    CMakeLists.txt
    main.cpp                    # the 90-line harness from §2.1
    stories/
      MyKnob_stories.cpp        # REGISTER_COMPONENT calls
    golden/                     # checked into git (or git-lfs)
      MyKnob_Default.png
      ...
    current/                    # .gitignore'd, written on each test run
    diff/                       # .gitignore'd, written on fail
    run_snapshots.sh            # driver below
```

### CMake (add to existing plugin build)

```cmake
if (PROJECT_ENABLE_SNAPSHOT_TESTS)
    add_executable(snapshot
        tests/snapshots/main.cpp
        tests/snapshots/stories/MyKnob_stories.cpp
        # ...one file per panel
    )
    target_compile_definitions(snapshot PRIVATE JUCE_SNAPSHOT_HARNESS=1)
    target_link_libraries(snapshot PRIVATE
        plugin_ui_objects        # your OBJECT library
        juce::juce_gui_basics
        juce::juce_graphics
    )
    # Determinism knob.
    target_compile_definitions(snapshot PRIVATE
        JUCE_DISABLE_COREGRAPHICS_FONT_SMOOTHING=1)
    target_precompile_headers(snapshot PRIVATE
        <juce_gui_basics/juce_gui_basics.h>)
endif()
```

### Driver script

```sh
#!/usr/bin/env bash
# tests/snapshots/run_snapshots.sh
set -eu
HARNESS=${1:-build/snapshot}
ROOT=$(git rev-parse --show-toplevel)
SNAP=$ROOT/tests/snapshots
CUR=$SNAP/current
DIFF=$SNAP/diff
mkdir -p "$CUR" "$DIFF"

# Discover stories by asking the binary for its registry.
mapfile -t stories < <("$HARNESS" --list)

fail=0
for story in "${stories[@]}"; do
    IFS='|' read -r name w h <<< "$story"  # harness prints "name|w|h"
    out="$CUR/$name.png"
    "$HARNESS" "$name" "$w" "$h" "$out"

    gold="$SNAP/golden/$name.png"
    if [[ ! -f "$gold" ]]; then
        echo "[new]  $name  (copy $out to golden/ to accept)"
        continue
    fi

    if odiff --antialiasing --threshold 0.05 \
             --diff-color "#ff00ff" \
             "$gold" "$out" "$DIFF/$name.png" > /dev/null; then
        echo "[pass] $name"
    else
        echo "[FAIL] $name  diff -> $DIFF/$name.png"
        fail=$((fail+1))
    fi
done

exit $fail
```

Add `--list` to the harness (6 lines: iterate the registry, print
`name|w|h` per line, exit 0).

### Local iteration loop

```
# On first save of a new MyKnob component:
REGISTER_COMPONENT (MyKnob_Default, []{ return std::make_unique<MyKnob>(); });
cmake --build build --target snapshot
./tests/snapshots/run_snapshots.sh build/snapshot
# review tests/snapshots/current/MyKnob_Default.png vs your Figma/Stitch target
# when it's right: cp tests/snapshots/current/MyKnob_Default.png tests/snapshots/golden/
# commit both the code and the golden, done.
```

Watch mode:

```
# with entr
find source/ui tests/snapshots -name '*.cpp' -o -name '*.h' | \
    entr -c sh -c 'cmake --build build --target snapshot && \
                   ./tests/snapshots/run_snapshots.sh build/snapshot'
```

Typical tight loop: edit `paint()`, save, 3-5 s of ccache-accelerated rebuild,
1 s for all 20 snapshots, diff images open in VS Code preview. Total ~5-10 s
per iteration.

### CI gating

One job in `.github/workflows/*.yml`, reusing Pamplejuce's template:

```yaml
snapshots:
  runs-on: ubuntu-22.04
  steps:
    - uses: actions/checkout@v6
      with: { lfs: true }            # if goldens are in LFS
    - run: |
        sudo apt-get install -y libasound2-dev libx11-dev libxinerama-dev \
            libxext-dev libfreetype6-dev libwebkit2gtk-4.1-dev \
            libglu1-mesa-dev xvfb ninja-build
        sudo /usr/bin/Xvfb :0 -screen 0 1920x1080x24 &
        npm i -g odiff-bin
    - uses: mozilla-actions/sccache-action@v0.0.9
    - env: { DISPLAY: ':0', CMAKE_CXX_COMPILER_LAUNCHER: sccache }
      run: |
        cmake -B build -G Ninja -DPROJECT_ENABLE_SNAPSHOT_TESTS=ON .
        cmake --build build --target snapshot
        ./tests/snapshots/run_snapshots.sh build/snapshot
    - if: failure()
      uses: actions/upload-artifact@v7
      with: { name: snapshot-diffs, path: tests/snapshots/diff/ }
```

Failed PR → the diff PNGs are uploaded as artifacts, reviewer downloads and
inspects. (If you want them inline in the PR: wire up reg-suit or argos-ci,
both support odiff as the backend.)

### Cross-platform goldens?

Strong recommendation: pick **one reference OS (Linux) for gating** and treat
macOS / Windows snapshot differences as informational. `SoftwareImageType` +
`JUCE_DISABLE_COREGRAPHICS_FONT_SMOOTHING=1` gets you 95-99% pixel equivalence;
the remaining difference is CoreText vs DirectWrite vs FreeType kerning. You
CAN maintain per-OS goldens (`golden/linux/`, `golden/macos/`, `golden/win/`),
but the ongoing tax of keeping three sets in sync is steep. Most teams go
Linux-only for gating.

### Where to start in one sitting

1. Copy the harness in §2.1 into `tests/snapshots/main.cpp`.
2. Add `REGISTER_COMPONENT` to one component.
3. Wire the CMake snippet in §8, build, run.
4. `brew install odiff`.
5. Run once, commit `golden/MyKnob.png`.
6. Everything else (watch mode, CI, more components) is incremental.

You'll have a working loop in about an hour. The ongoing cost per new
Component is one `REGISTER_COMPONENT` line plus one golden PNG commit.
