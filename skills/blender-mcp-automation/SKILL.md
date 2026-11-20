---
name: blender-mcp-automation
description: Real-time automation and bidirectional bridge between AI agents and Blender via Model Context Protocol (MCP) and local WebSocket servers. Enables live scene querying, programmatic bpy execution, viewport snapshot verification, iterative 3D asset generation, and headless rendering.
---

# Blender MCP Automation & Live Bridge

This skill defines the operational protocol for AI agents driving Blender in real-time through Model Context Protocol (MCP) servers or local WebSocket sockets.

## Architecture Overview

```text
[ AI Agent / Assistant ]
         │
         ▼ (JSON-RPC / MCP Messages)
[ Blender MCP Server Bridge ]
         │
         ▼ (Local TCP Socket / IPC: e.g. localhost:9876)
[ Blender Embedded Python Session (bpy) ]
         │
         ├── Scene Graph & Data-Blocks (bpy.data)
         ├── Context & Active Selections (bpy.context)
         └── Viewport Snapshots (bpy.ops.render.opengl)
```

---

## 1. Live Scene Discovery & State Interrogation

Always query the current scene context before issuing mutation commands:

```python
import bpy

def get_scene_summary():
    """Returns a lightweight JSON-compatible snapshot of active scene state."""
    scene = bpy.context.scene
    return {
        "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
        "selected_objects": [obj.name for obj in bpy.context.selected_objects],
        "total_objects": len(scene.objects),
        "render_engine": scene.render.engine,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "frame_current": scene.frame_current,
        "collections": [c.name for c in bpy.data.collections]
    }
```

---

## 2. Safe Operator & Script Execution Protocol

When sending execution payloads from the agent into Blender:

1. **Context Override Hygiene**:
   In Blender 3.2+, always use `temp_override` instead of mutating global context:
   ```python
   # Modern Context Override (Blender 3.2 - 5.0+)
   with bpy.context.temp_override(active_object=target_obj, selected_objects=[target_obj]):
       bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
   ```

2. **Atomic Undo Blocks**:
   Group multi-step agent actions into single undo steps so the user can easily revert:
   ```python
   bpy.ops.ed.undo_push(message="Agent Action: Generate Lighting Rig")
   ```

3. **Exception Trapping & Diagnostic Reporting**:
   Wrap execution blocks to return clean tracebacks over the MCP channel:
   ```python
   import traceback, json

   def execute_agent_command(code_str):
       try:
           exec_locals = {}
           exec(code_str, {"bpy": bpy}, exec_locals)
           return {"status": "success", "result": exec_locals.get("result", None)}
       except Exception as e:
           return {
               "status": "error",
               "error_type": type(e).__name__,
               "message": str(e),
               "traceback": traceback.format_exc()
           }
   ```

---

## 3. Visual Verification Snapshots

To visually verify generated geometry, materials, and lighting without waiting for heavy Cycles offline renders:

```python
import bpy, os

def capture_viewport_verification(output_path, width=960, height=540):
    """Captures OpenGL viewport render for immediate visual confirmation."""
    scene = bpy.context.scene
    old_x, old_y = scene.render.resolution_x, scene.render.resolution_y
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.filepath = output_path
    
    # Use OpenGL render for instantaneous capture
    bpy.ops.render.opengl(write_still=True)
    
    scene.render.resolution_x = old_x
    scene.render.resolution_y = old_y
    return os.path.exists(output_path)
```

---

## 4. Headless Batch & Background Automation

When running Blender from terminal/CLI as an agent task:
```bash
# Run script headlessly on background Blender instance
blender -b -P run_pipeline.py -- --output-dir ./renders --samples 128

# Open existing blend file and export assets
blender asset.blend -b -P export_gltf.py
```
