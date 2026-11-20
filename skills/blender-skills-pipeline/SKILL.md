---
name: blender-skills-pipeline
description: Production-grade 3D art and scene pipeline in Blender (inspired by arjun988/blender-skills and SOTA technical art workflows). Covers hard-surface modeling, non-destructive modifier stacks, procedural Geometry Nodes, camera composition, cinematic 3-point & HDRI studio lighting, PBR materials (Principled BSDF v2), EEVEE Next & Cycles rendering, and game-ready asset export (glTF/FBX).
---

# Blender 3D Skills Pipeline

An expert production pipeline for generating, staging, and refining 3D models and scenes in Blender (3.6 through 5.0+). Based on proven studio technical art workflows and top agent skill patterns.

## Core Directives

1. **Think Non-Destructively**: Never apply modifiers until final export. Keep base meshes clean and topology subdivision-friendly.
2. **Reference-First Calibration**: Before placing geometry, establish scene units (Metric, millimeters/meters), reference silhouette, and primary/secondary/tertiary form hierarchy.
3. **PBR Material Accuracy**: Use Principled BSDF v2 with physically accurate IOR, metallic values (binary 0 or 1 for standard dielectrics/metals), roughness contrast, and normal mapping.
4. **Cinematic Staging**: Avoid default 50mm flat perspective cameras. Use intentional focal lengths (28mm for grand scale/environmental shots, 85mm for hero assets, 135mm for isometric/product rendering).
5. **Lighting Hierarchy**: Key light (dominant shadow caster, 60-70% intensity), Fill light (soft contrast fill, 20-30% intensity, cool/warm complementary tone), Rim/Back light (edge definition, separates subject from background).

---

## 1. Hard-Surface & Architectural Modeling

### Form Hierarchy Rule
- **Primary Forms (70%)**: Overall silhouette and bounding proportions (cubes, cylinders, silhouettes).
- **Secondary Forms (20%)**: Bevels, cutouts, panel insets, major functional extrusions.
- **Tertiary Details (10%)**: Screws, seams, ventilation grills, surface micro-roughness (prefer normal/bump maps over dense geometry).

### Modifier Stack Order
1. **Mirror** (Merge enabled, small threshold 0.001m)
2. **Solidify** (Even thickness enabled, High quality normals)
3. **Bevel** (Limit Method: Weight or Angle ~30°, Profile 0.5, Segments 2-3, Harden Normals enabled)
4. **Weighted Normal** (Keep sharp enabled — ensures razor-clean flat surfaces with smooth beveled edges)
5. **Subdivision Surface** (Render 2, Viewport 1 — only if organic/curved surface)

```python
import bpy

def setup_hardsurface_modifiers(obj, bevel_width=0.015):
    # Ensure smooth shading with auto-smooth/weighted normals
    obj.data.use_auto_smooth = True
    
    # Bevel Modifier
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = bevel_width
    bev.segments = 3
    bev.limit_method = 'ANGLE'
    bev.angle_limit = 0.523599  # 30 degrees in radians
    bev.harden_normals = True
    
    # Weighted Normal Modifier
    wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    wn.keep_sharp = True
```

---

## 2. Procedural Geometry Nodes

Use Geometry Nodes for procedural arrays, cables, scattering, foliage distribution, and parametric architecture:

```python
import bpy

def create_curve_cable(name="ProceduralCable", radius=0.01):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 4
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    spline.bezier_points[0].co = (0, 0, 0)
    spline.bezier_points[1].co = (2, 0, 1)
    
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    return obj
```

---

## 3. PBR Materials & Shaders (Principled BSDF v2)

Always build shader networks with proper node math:

```python
import bpy

def create_pbr_material(name, base_color=(0.1, 0.1, 0.12, 1.0), roughness=0.35, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    # Blender 4.0+ Principled BSDF v2 compatibility
    if 'IOR' in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = 1.45
        
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat
```

---

## 4. Studio Lighting & Camera Rig

### 3-Point Studio Rig Blueprint
- **Key Light**: Area light (Power: 250W, Size: 1.2m, Position: 45° off-axis, elevated 45°).
- **Fill Light**: Area or Sun light (Power: 60W, Size: 2.0m, Position: -60° off-axis, neutral cool).
- **Rim Light**: Area or Spot light (Power: 180W, Position: behind subject angled toward camera edge).
- **World Lighting**: Low intensity HDRI or dark gradient background (`Color: (0.02, 0.02, 0.03)`).

### Camera Setup
```python
def setup_cinematic_camera(target_loc=(0, 0, 0.5), focal_length=85):
    cam_data = bpy.data.cameras.new("HeroCamera")
    cam_data.lens = focal_length
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 3.5
    cam_data.dof.aperture_fstop = 2.8
    
    cam_obj = bpy.data.objects.new("HeroCamera", cam_data)
    cam_obj.location = (2.5, -2.5, 1.8)
    bpy.context.collection.objects.link(cam_obj)
    
    # Add Track-To constraint
    tt = cam_obj.constraints.new(type='TRACK_TO')
    empty = bpy.data.objects.new("CameraTarget", None)
    empty.location = target_loc
    bpy.context.collection.objects.link(empty)
    tt.target = empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    return cam_obj
```

---

## 5. Game-Ready Asset Optimization & Export

### Real-Time Validation Checklist
- **Origin & Transform**: Apply Scale (`Ctrl+A > Scale`), origin set to base/pivot.
- **Topology**: Zero non-manifold edges, zero isolated vertices, consistent face normals (`Shift+N`).
- **UV Coordinates**: Minimum 2px padding at 2048x2048 to prevent mipmap bleeding.
- **glTF 2.0 Export Settings**:
  - Format: `.glb` (self-contained binary)
  - Transforms: `+Y Up`
  - Geometry: Apply Modifiers, Include Normals, Include UVs
  - Materials: Export Principled BSDF materials with PBR textures.
