// snapshot_main.cpp
//
// Headless harness: renders any registered juce::Component into a PNG.
// Drop this into <plugin>/tests/snapshots/main.cpp and wire it up via the
// CMake snippet bundled with this skill (see scripts/snapshot_CMakeLists.snippet).
//
// Invocation:
//   ./snapshot --list                      # print registered stories, one per line
//   ./snapshot <name> <w> <h> <out.png>    # render a story
//
// Components register themselves from "story" TUs next to the code they test:
//
//   // MyKnob_stories.cpp
//   #include "MyKnob.h"
//   REGISTER_COMPONENT (MyKnob_Default, []{
//       auto c = std::make_unique<MyKnob>();
//       c->setValue (0.7f);
//       return c;
//   });
//
// The key determinism levers are:
//   - SoftwareImageType{} forces the same rasterizer on macOS/Windows/Linux
//     (default NativeImageType is CoreGraphics / Direct2D / software respectively
//     and produces three different pixel outputs for the same paint() code).
//   - JUCE_DISABLE_COREGRAPHICS_FONT_SMOOTHING=1 (set in the CMake target) kills
//     macOS subpixel AA, which is otherwise nondeterministic across machines.
//   - runDispatchLoopUntil(16) gives Components that kick off async layout or
//     timers in their ctor one pump before we rasterize.

#include <juce_gui_basics/juce_gui_basics.h>

#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>

namespace snap
{
    struct Story
    {
        using Factory = std::function<std::unique_ptr<juce::Component>()>;
        Factory make;
        int defaultWidth  = 0;  // 0 = let the caller decide
        int defaultHeight = 0;
    };

    inline std::unordered_map<std::string, Story>& registry()
    {
        static std::unordered_map<std::string, Story> r;
        return r;
    }

    struct Register
    {
        Register (const char* name, Story::Factory factory,
                  int w = 0, int h = 0)
        {
            registry().emplace (name, Story { std::move (factory), w, h });
        }
    };

    inline int renderToFile (const std::string& name, int w, int h,
                             const juce::File& out)
    {
        auto it = registry().find (name);
        if (it == registry().end())
        {
            std::cerr << "unknown component: " << name << "\n";
            std::cerr << "run with --list to see registered stories\n";
            return 2;
        }

        const auto& story = it->second;
        if (w <= 0) w = story.defaultWidth  > 0 ? story.defaultWidth  : 400;
        if (h <= 0) h = story.defaultHeight > 0 ? story.defaultHeight : 300;

        auto component = story.make();
        component->setSize (w, h);

        // One message-thread pump so ctors that schedule layout/timers settle.
        juce::MessageManager::getInstance()->runDispatchLoopUntil (16);

        // Force SoftwareImageType for cross-platform byte-level reproducibility.
        juce::Image img (juce::Image::ARGB, w, h, /*clearImage*/ true,
                         juce::SoftwareImageType {});
        {
            juce::Graphics g (img);
            component->paintEntireComponent (g, /*ignoreAlphaLevel*/ true);
        }

        out.getParentDirectory().createDirectory();
        out.deleteFile();

        juce::FileOutputStream fs (out);
        if (! fs.openedOk())
        {
            std::cerr << "cannot open " << out.getFullPathName() << "\n";
            return 3;
        }

        juce::PNGImageFormat png;
        return png.writeImageToStream (img, fs) ? 0 : 4;
    }

    inline void printList()
    {
        // Format: "name|defaultW|defaultH" per line. The driver script parses
        // this to discover stories without hard-coding a list.
        for (const auto& [name, story] : registry())
            std::cout << name << '|'
                      << story.defaultWidth  << '|'
                      << story.defaultHeight << '\n';
    }
}

// Macro so stories can declare themselves in a single line next to the
// component they exercise. Width/height are optional; omit them to pick a
// size at the CLI.
#define REGISTER_COMPONENT(id, factory)                                     \
    static ::snap::Register reg_##id { #id, factory }

#define REGISTER_COMPONENT_SIZED(id, factory, w, h)                         \
    static ::snap::Register reg_##id { #id, factory, (w), (h) }

int main (int argc, char** argv)
{
    // Brings up MessageManager + platform GUI infrastructure (fonts,
    // LookAndFeel_V4). Required even for offscreen rendering; without it,
    // many paint paths assert.
    juce::ScopedJuceInitialiser_GUI initialiser;
    juce::MessageManagerLock lock;

    if (argc >= 2 && std::string (argv[1]) == "--list")
    {
        ::snap::printList();
        return 0;
    }

    if (argc < 5)
    {
        std::cerr << "usage:\n"
                     "  " << (argc > 0 ? argv[0] : "snapshot")
                  << " <name> <width> <height> <out.png>\n"
                     "  " << (argc > 0 ? argv[0] : "snapshot")
                  << " --list\n\n"
                     "registered stories:\n";
        for (const auto& [k, s] : ::snap::registry())
            std::cerr << "  " << k
                      << " (default " << s.defaultWidth << "x"
                      << s.defaultHeight << ")\n";
        return 1;
    }

    return ::snap::renderToFile (
        argv[1],
        std::atoi (argv[2]),
        std::atoi (argv[3]),
        juce::File::getCurrentWorkingDirectory().getChildFile (argv[4]));
}
