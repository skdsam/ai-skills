# Blender Python API Quick Reference
**Version-Aware Development for Blender 3.6 to 5.0+**

## Version Detection

```python
import bpy

# Get version as tuple
version = bpy.app.version  # e.g., (4, 2, 0)

# Check version
if version >= (4, 0, 0):
    print("Blender 4.0 or higher")

# Check specific feature
if hasattr(bpy.types, 'AssetShelf'):  # Blender 4.1+
    print("Asset Shelf API available")
```

## Common Patterns by Version

### Blender 3.6 LTS
```python
# Light linking (3.6+)
light = bpy.data.lights['Light']
light.use_shadow = True

# Legacy addon structure
bl_info = {
    "blender": (3, 6, 0),
    # ... other fields
}
```

### Blender 4.0
```python
# Principled BSDF v2
bsdf = nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.5

# EEVEE Next settings
scene.eevee.use_soft_shadows = True
```

### Blender 4.1
```python
# Asset Shelf (4.1+)
if hasattr(bpy.types, 'AssetShelf'):
    # Use Asset Shelf API
    pass
```

### Blender 4.2 LTS
```python
# Extensions manifest (blender_manifest.toml)
# Place alongside your addon files
"""
schema_version = "1.0.0"
id = "my_extension"
version = "1.0.0"
name = "My Extension"
tagline = "Short description"
maintainer = "Your Name"
type = "add-on"

[permissions]
files = "Import/export files"
"""

# Realtime compositor (4.2+)
scene.use_nodes = True
scene.node_tree.nodes.new('CompositorNodeBlur')
```

## Essential Code Snippets

### Object Creation
```python
import bpy

# Create mesh
mesh = bpy.data.meshes.new(name="MyMesh")
obj = bpy.data.objects.new("MyObject", mesh)
bpy.context.collection.objects.link(obj)

# Add vertices and faces
mesh.from_pydata(vertices, edges, faces)
mesh.update()
```

### Material Creation (Version-Aware)
```python
def create_material(name, base_color=(0.8, 0.8, 0.8, 1.0)):
    """Create Principled material with version compatibility."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create nodes
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Version-aware setup
    if bpy.app.version >= (4, 0, 0):
        # Blender 4.0+ Principled BSDF v2
        bsdf.inputs['Base Color'].default_value = base_color
    else:
        # Blender 3.6 legacy
        bsdf.inputs['Base Color'].default_value = base_color
    
    # Link nodes
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat
```

### BMesh Operations (Fast Mesh Editing)
```python
import bmesh

def modify_mesh(obj):
    """Use BMesh for efficient mesh operations."""
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Perform operations
    for vert in bm.verts:
        vert.co.z += 1.0
    
    # Subdivide all faces
    bmesh.ops.subdivide_edges(
        bm,
        edges=bm.edges,
        cuts=1,
        use_grid_fill=True
    )
    
    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
```

### Custom Operator
```python
class OBJECT_OT_my_operator(bpy.types.Operator):
    """My Custom Operator"""
    bl_idname = "object.my_operator"
    bl_label = "My Operator"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        # Do something
        self.report({'INFO'}, "Operation completed")
        return {'FINISHED'}
```

### Custom Panel
```python
class VIEW3D_PT_my_panel(bpy.types.Panel):
    """My Custom Panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = "My Panel"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.my_operator")
```

### Animation (Keyframes)
```python
# Set keyframe
obj = bpy.context.active_object
obj.location.z = 0
obj.keyframe_insert(data_path="location", frame=1)

obj.location.z = 5
obj.keyframe_insert(data_path="location", frame=50)
```

### Rendering
```python
# Setup render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'  # or 'BLENDER_EEVEE' / 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.filepath = "/tmp/render.png"

# Render
bpy.ops.render.render(write_still=True)
```

### Import/Export
```python
# Export FBX
bpy.ops.export_scene.fbx(
    filepath="/path/to/file.fbx",
    use_selection=True,
    apply_scale_options='FBX_SCALE_ALL'
)

# Import OBJ
bpy.ops.import_scene.obj(filepath="/path/to/file.obj")

# Export USD (Blender 3.6+)
bpy.ops.wm.usd_export(filepath="/path/to/file.usd")
```

## Performance Tips

### ✅ DO: Use BMesh for batch operations
```python
import bmesh
bm = bmesh.new()
bm.from_mesh(mesh)
# Fast batch operations
bm.to_mesh(mesh)
bm.free()
```

### ❌ DON'T: Use operators in loops
```python
# SLOW - operators have overhead
for obj in objects:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.delete()
```

### ✅ DO: Direct data access
```python
# FAST - direct data manipulation
for obj in objects:
    bpy.data.objects.remove(obj, do_unlink=True)
```

## Error Handling

```python
def safe_operation(obj):
    """Example of safe Blender operation."""
    try:
        if obj is None:
            raise ValueError("Object is None")
        
        if not hasattr(obj.data, 'vertices'):
            raise TypeError(f"{obj.name} is not a mesh object")
        
        # Perform operation
        # ...
        
    except AttributeError as e:
        print(f"Attribute error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True
```

## Context Overrides

```python
# Override context for specific operations
with bpy.context.temp_override(active_object=obj):
    bpy.ops.object.mode_set(mode='EDIT')

# Or use context dictionary
override = bpy.context.copy()
override['active_object'] = obj
bpy.ops.object.mode_set(override, mode='EDIT')
```

## Handlers (Event Callbacks)

```python
from bpy.app.handlers import persistent

@persistent
def my_handler(scene):
    """Handler that survives file loads."""
    print(f"Frame changed: {scene.frame_current}")

# Register handler
bpy.app.handlers.frame_change_post.append(my_handler)

# Unregister handler
bpy.app.handlers.frame_change_post.remove(my_handler)
```

## Version Migration Checklist

### From 3.6 to 4.0+
- [ ] Update Principled BSDF socket names
- [ ] Check EEVEE settings (EEVEE vs EEVEE Next)
- [ ] Test material node connections
- [ ] Update Python version (3.10 → 3.11)

### From 4.0/4.1 to 4.2+
- [ ] Convert addon to extension format
- [ ] Create `blender_manifest.toml`
- [ ] Test with extensions platform
- [ ] Update installation instructions

### From 4.x to 5.0+ (Future)
- [ ] Monitor Blender DevTalk for API changes
- [ ] Test with alpha/beta builds
- [ ] Update Python version (likely 3.12+)
- [ ] Check for Vulkan-related changes

## Common Gotchas

1. **Context Issues**
   - Always check if context.active_object exists
   - Use context overrides when needed

2. **Edit Mode vs Object Mode**
   - Can't edit mesh data in edit mode
   - Use bmesh or switch modes

3. **Undo/Redo**
   - Use `bl_options = {'REGISTER', 'UNDO'}` in operators

4. **Depsgraph Updates**
   - Call `obj.update_tag()` or `bpy.context.view_layer.update()`

5. **Memory Leaks**
   - Always call `bm.free()` on BMesh objects
   - Remove unused data blocks

## Resources

- **API Docs:** https://docs.blender.org/api/current/
- **DevTalk:** https://devtalk.blender.org/
- **Source Code:** https://projects.blender.org/blender/blender
- **Release Notes:** https://wiki.blender.org/wiki/Reference/Release_Notes

---

**This guide is maintained by the Blender Dev Expert skill** 🎨
