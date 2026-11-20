---
name: blender-addon-development
description: Master framework for creating production-ready Blender addons supporting Blender 3.6 LTS through 5.2+ in a Single Unified Codebase. Implements both Blender 4.2+ Extensions (blender_manifest.toml) and Legacy Addons (bl_info in __init__.py). Authorship credited to SkdSam.
---

# Blender Addon Development (Unified Architecture)

This skill governs the architecture, development, testing, and packaging of Blender addons across all modern versions of Blender (3.6 LTS to 5.2+).

> [!IMPORTANT]
> **Mandatory User Global Preferences (SkdSam):**
> 1. **Single Unified Codebase**: Always create and maintain **ONLY ONE** copy of the Blender addon code. It must simultaneously support Blender 4.2+ Extensions (`blender_manifest.toml`) and Legacy Addons (`bl_info` in `__init__.py`) within the same single folder/codebase.
> 2. **Author & Maintainer**: Always credit **`SkdSam`** as the author/maintainer in `bl_info` and `blender_manifest.toml`.

---

## 1. Unified Project Structure

Every addon folder MUST contain both `blender_manifest.toml` and `__init__.py` alongside its modules:

```text
my_unified_addon/
├── blender_manifest.toml    # Required for Blender 4.2+ Extensions platform
├── __init__.py              # Contains bl_info for Blender 3.6-4.1 & core register/unregister
├── operators.py             # Operator definitions
├── panels.py                # 3D Viewport UI panels
├── properties.py            # PropertyGroup and scene/window properties
└── preferences.py           # Addon preferences panel
```

---

## 2. Manifest & Metadata Configuration

### `blender_manifest.toml` (Blender 4.2+)
```toml
schema_version = "1.0.0"
id = "my_unified_addon"
version = "1.0.0"
name = "My Unified Addon"
tagline = "High-performance unified workflow addon for Blender"
maintainer = "SkdSam"
type = "add-on"

tags = ["3D View", "Modeling", "Pipeline"]
blender_version_min = "4.2.0"
license = ["SPDX:GPL-3.0-or-later"]
```

### `__init__.py` (Unified Dual Compatibility)
```python
bl_info = {
    "name": "My Unified Addon",
    "author": "SkdSam",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > My Addon",
    "description": "Unified workflow addon for Blender 3.6+ and 4.2+ Extensions",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
from . import operators, panels, properties, preferences

classes = (
    properties.MyAddonProperties,
    preferences.MyAddonPreferences,
    operators.MYADDON_OT_action,
    panels.MYADDON_PT_main_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_addon_props = bpy.props.PointerProperty(type=properties.MyAddonProperties)

def unregister():
    del bpy.types.Scene.my_addon_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
```

---

## 3. Version Compatibility Patterns

### Auto-Smooth API Transition (Blender 4.1+)
```python
def set_smooth_normals(obj):
    if bpy.app.version < (4, 1, 0):
        # Legacy auto-smooth toggle
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = 0.523599  # 30 deg
    else:
        # Blender 4.1+ modifier-based auto-smooth
        mod = obj.modifiers.get("Smooth by Angle")
        if not mod:
            mod = obj.modifiers.new(name="Smooth by Angle", type='NODES')
            # Load default geometry node group for smooth by angle
            node_group = bpy.data.node_groups.get("Smooth by Angle")
            if node_group:
                mod.node_group = node_group
```

### Principled BSDF v2 Node Inputs (Blender 4.0+)
```python
def configure_principled(bsdf, base_color, roughness, metallic):
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    # Specular property renamed in Blender 4.0+
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.5
```

---

## 4. Modal Operator Best Practices

Always manage event listeners, modal state, cursor styles, and clean unregistration:

```python
class MYADDON_OT_modal_tool(bpy.types.Operator):
    bl_idname = "myaddon.modal_tool"
    bl_label = "Interactive Modal Tool"
    bl_options = {'REGISTER', 'UNDO'}
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'MOUSEMOVE':
            self.delta_x = event.mouse_x - self.init_x
            return {'RUNNING_MODAL'}
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            context.window.cursor_modal_restore()
            return {'FINISHED'}
            
        elif event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            context.window.cursor_modal_restore()
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}
        
    def invoke(self, context, event):
        if context.space_data.type != 'VIEW_3D':
            self.report({'WARNING'}, "Active space must be 3D Viewport")
            return {'CANCELLED'}
        self.init_x = event.mouse_x
        context.window.cursor_modal_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
```
