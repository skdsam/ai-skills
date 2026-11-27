---
name: blender-addon-docs
description: Create gold-standard, 100% offline self-contained interactive HTML documentation (documentation.html) for Blender addons with a clickable N-Panel UI Explorer, live search, operator/option/preset catalogs, and an in-addon Docs launcher button. Strictly requires companion UI/UX skills from this library.
---

# Blender Addon Interactive Documentation (`blender-addon-docs`)

Create production-grade, **100% offline self-contained** interactive HTML documentation (`documentation.html`) for Blender addons, modeled on the gold-standard interactive N-Panel explorer pattern, and wire an in-addon **Docs** button so users can open it directly from Blender.

---

## 1. Mandatory Companion Skills (Strictly Required)

Before designing or refining the documentation UI, you **MUST** load and follow these companion skills from this library alongside `blender-addon-docs`:

| Skill ID | Mandatory Role |
| :--- | :--- |
| **`ui-ux-pro-max`** | Visual hierarchy, spacing rhythm, dark-surface contrast, component polish, and interaction quality |
| **`better-ui`** | Clean information architecture, scannable cards/tables, and uncluttered control density |
| **`better-accessibility`** | Semantic HTML, keyboard navigation, focus states, ARIA attributes (`role="tablist"`, `aria-selected`, `aria-pressed`), and WCAG AA contrast |
| **`frontend-design`** | Cohesive visual craft, typography scale, and responsive layout polish |
| **`blender-addon-development`** *(when editing addon Python)* | Single Unified Codebase rules (`blender_manifest.toml` + `bl_info`), `SkdSam` authorship, and safe operator/panel registration |

If a project does not yet have those companion UI/UX skills linked into `.agents/skills/`, link them using the project skill router before proceeding.

---

## 2. Core Requirements & Non-Negotiable Rules

1. **100% Offline Self-Contained HTML**:
   - Output a single `documentation.html` file with **all CSS embedded in `<style>`** and **all JS embedded in `<script>`**.
   - **Zero CDN links** (no Tailwind CDN, no external fonts, no external icon packs). It must render identically when opened offline via `file:///` from inside an installed Blender addon folder.
2. **100% Grounded in Real Addon Code**:
   - Audit the addon's actual source files (`blender_manifest.toml`, `__init__.py`, `properties.py`, `operators.py`, `ui_panels.py`, and core modules) before writing a single line of documentation.
   - Every button, `bl_idname`, RNA property name, default value, drawer/panel name, and preset in `documentation.html` must match the real codebase 1:1. Never invent placeholder controls or guessed property names.
3. **Clickable N-Panel Parity**:
   - The Interactive N-Panel UI Explorer must mirror the addon's real Blender UI layout (Quick/Advanced mode switches if present, button rows, toggles, sliders, and collapsible drawers).
   - Clicking **any** control in the replica updates the sticky **Live Inspector Card** on the right and highlights the selected control.
4. **Bundled & Launchable Inside Blender**:
   - Save `documentation.html` inside the addon package directory (e.g., `<addon_pkg>/documentation.html`) so it is automatically included in the distributable `.zip`, and optionally keep a synced copy at the repository root if the repo convention uses one.
   - Wire a `Docs` operator button (`icon="HELP"`) in the addon's main N-Panel header to open the bundled local file in the user's browser.

---

## 3. Gold-Standard 5-Tab Documentation Architecture

Use [references/template.html](references/template.html) as the structural and styling baseline.

### Persistent Sticky Header
- **Identity Block**: Monogram badge, Addon Name, module + version pill (e.g., `my_addon v1.0`), Blender version range pill (e.g., `Blender 3.6 LTS – 5.3+`), and render engine/category pill.
- **Global Live Search (`#globalSearch`)**: Filters Operators, Options/Sliders, and Presets simultaneously in real time, displaying a live match-count banner (`#searchBanner`) with a one-click Reset button.
- **Tab Bar (`role="tablist"`)**: Horizontally scrollable tabs with `aria-selected`:
  1. **How It Works & Architecture**
  2. **Interactive N-Panel UI Explorer**
  3. **All Buttons & Operators (`N`)**
  4. **All Options & Sliders (`M` Sections/Drawers)**
  5. **Styles & Presets Catalog** *(if the addon has no presets, adapt Tab 5 to Workflows / Examples / Troubleshooting or omit cleanly)*

### Tab 1: How It Works & Architecture
- **KPI Summary Bar**: 4–6 compact metric cards (e.g., Modes/Styles, Presets, Operators, Tunable Controls, Core Systems, Compatibility).
- **End-to-End Pipeline**: 3–4 step cards showing how UI state flows through logic/math into Blender data-blocks, shaders, or scene objects.
- **Core Subsystems / Node Groups**: Card grid explaining internal building blocks (shader node groups, Geometry Nodes rigs, background handlers, etc.).
- **Codebase Module Map**: Table mapping each `.py` / `.toml` file to its responsibility and key classes/functions.

### Tab 2: Interactive N-Panel UI Explorer
- **Left Column (`5/12` width)**: Faithful dark replica of Blender's 3D Viewport N-Panel (`N`), including:
  - Header bar with primary action button, mode switches (e.g., Quick / Advanced), and `Docs` button.
  - Sub-boxes and collapsible drawer buttons mirroring `ui_panels.py`.
  - Every interactive element carries `class="sim-ctrl"` and `data-inspect="<key>"`.
- **Right Column (`7/12` width, sticky)**: **Live Inspector Card** displaying:
  - Category Badge (`OPERATOR BUTTON`, `RNA PROPERTY`, `DRAWER`, `MODE`, `READOUT`)
  - Control Title + monospace `bl_idname` / RNA path
  - **What It Does** (plain-language artist explanation)
  - **How It Works Under the Hood** (exact functions, shader sockets, or Blender API calls)
  - **Source File & Handler** (`operators.py → MYADDON_OT_...`)
  - **Affected Data / Target** (scene props, node groups, lamps, objects)

### Tab 3: All Buttons & Operators
- Data-driven (`OPERATORS_DATA`) 2-column card grid.
- Each card shows: UI Label, `bl_idname`, UI Location, Python Class, What It Does, How It Works, and Operator Parameters.

### Tab 4: All Options & Sliders
- Data-driven (`OPTIONS_DATA`) grouped by UI drawer/section.
- Top **Drawer Filter Pills** (`aria-pressed="true|false"`) for `All` + each section/drawer.
- Each section renders a responsive table: `UI Label | RNA Property | Type & Default | What It Controls | How It Works`.

### Tab 5: Styles & Presets Catalog
- Data-driven (`PRESETS_DATA`) 3-column card grid (with optional style/category overview cards above).
- Each card shows: Number + Name, Category Badge, Description, and Key Parameter Highlights.

---

## 4. Wiring the In-Addon `Docs` Button

### Operator (`operators.py`)
Add an operator that resolves `documentation.html` relative to the addon package and opens it via Blender's native URL opener with a `webbrowser` fallback:

```python
import os
import webbrowser
from pathlib import Path
import bpy


class MYADDON_OT_open_documentation(bpy.types.Operator):
    bl_idname = "my_addon.open_documentation"
    bl_label = "Open Documentation"
    bl_description = "Open the interactive offline HTML documentation in your web browser"

    def execute(self, context):
        doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documentation.html")
        if not os.path.isfile(doc_path):
            self.report({"WARNING"}, f"Documentation file not found: {doc_path}")
            return {"CANCELLED"}
        doc_uri = Path(doc_path).as_uri()
        try:
            bpy.ops.wm.url_open(url=doc_uri)
        except Exception:
            webbrowser.open(doc_uri)
        return {"FINISHED"}
```

Register `MYADDON_OT_open_documentation` in the addon's `classes` tuple.

### N-Panel Button (`ui_panels.py`)
Place the button in the top header row of the main N-Panel:

```python
row.operator("my_addon.open_documentation", text="Docs", icon="HELP")
```

---

## 5. Step-by-Step Execution Workflow

1. **Load Companion Skills**: Read `ui-ux-pro-max`, `better-ui`, `better-accessibility`, and `frontend-design` (plus `blender-addon-development` if modifying Python).
2. **Audit the Addon**: Read `blender_manifest.toml`, `__init__.py`, `properties.py`, `operators.py`, `ui_panels.py`, and core modules to extract the exact inventory of operators, RNA properties, defaults, drawers, and presets.
3. **Generate `documentation.html`**: Start from [references/template.html](references/template.html), populate the HTML sections and JS data arrays (`INSPECTOR_DATA`, `OPERATORS_DATA`, `OPTIONS_DATA`, `PRESETS_DATA`), and refine styling/accessibility per the companion UI/UX skills.
4. **Wire the `Docs` Button**: Add the `open_documentation` operator and `ui_panels.py` button if not already present, and verify `documentation.html` is inside the addon package folder.
5. **Verify**:
   - Confirm zero external `http://` / `https://` `<script>`, `<link>`, or font URLs in `documentation.html`.
   - Confirm every `.sim-ctrl[data-inspect]` key exists in `INSPECTOR_DATA`.
   - Confirm tabs, Quick/Advanced toggle (if used), drawer filter pills, and global search all work with zero console errors.
   - If Python files were edited, run a headless Blender import/registration check to confirm clean `register()`/`unregister()`.
