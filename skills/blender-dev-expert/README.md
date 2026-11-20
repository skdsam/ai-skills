# Blender Development Expert Skill

A comprehensive AI agent skill for Blender Python development across versions 3.6 to 5.0+.

## Overview

This skill provides expert-level assistance for:
- Blender Python API (bpy) development
- Addon and extension creation
- Version-aware code generation
- Cross-version compatibility
- Production-ready Blender automation

## Supported Blender Versions

- ✅ **Blender 3.6 LTS** (June 2023) - Python 3.10
- ✅ **Blender 4.0** (November 2023) - Python 3.11, EEVEE Next
- ✅ **Blender 4.1** (March 2024) - Python 3.11, Asset Shelf
- ✅ **Blender 4.2 LTS** (July 2024) - Python 3.11, Extensions Platform
- ✅ **Blender 5.0+** (Future) - Expected Python 3.12+

## Features

### Version-Aware Development
- Automatic version detection and compatibility checking
- Version-specific API guidance
- Migration support between Blender versions
- Deprecation warnings and modern alternatives

### Complete API Coverage
- **Core API:** bpy.data, bpy.ops, bpy.context, bpy.types
- **Addon System:** Registration, operators, panels, properties
- **Extensions:** Blender 4.2+ extension manifest system
- **Geometry:** Mesh operations, modifiers, BMesh
- **Materials:** Node-based shading, Principled BSDF v2
- **Animation:** Keyframes, F-Curves, drivers, constraints
- **Rendering:** Cycles, EEVEE, compositor
- **File I/O:** Import/export, asset libraries

### Best Practices
- Performance optimization (BMesh vs bpy.ops)
- Error handling and context safety
- Clean code following Blender conventions
- Production-ready patterns
- Testing strategies

## Usage

### In Antigravity IDE
Simply mention the skill in your request:

```
Use the @blender-dev-expert skill to create a Blender 4.2 extension 
that automatically UVs selected objects.
```

### In Other AI Assistants
Reference the skill file when asking Blender development questions:

```
Using the blender-dev-expert skill, write a script to batch export 
FBX files compatible with Blender 3.6+
```

## Example Requests

1. **Addon Creation**
   - "Create a Blender 4.2 extension with custom operators and panels"
   - "Build an addon for batch material creation in Blender 3.6+"

2. **Automation Scripts**
   - "Write a script to automate rendering with Cycles for Blender 4.0"
   - "Create a batch export script for FBX files"

3. **Version Migration**
   - "Migrate my Blender 3.6 addon to the 4.2 extensions system"
   - "Update this code to work with Principled BSDF v2 in Blender 4.0"

4. **API Questions**
   - "How do I access the realtime compositor API in Blender 4.2?"
   - "What's the best way to create geometry programmatically in Blender 4.1?"

5. **Cross-Version Compatibility**
   - "Create an operator that works in both Blender 3.6 and 4.2"
   - "Write version-aware code for the new light linking API"

## Key Capabilities

### Version Detection
Automatically includes version checking code:
```python
import bpy

version = bpy.app.version
if version >= (4, 2, 0):
    # Use Blender 4.2+ features
    pass
```

### Principled BSDF Compatibility
Handles shader changes across versions:
```python
# Works across Blender 3.6 to 5.0+
def setup_material(material):
    # Version-aware implementation
    pass
```

### Extension Manifest
Generates proper `blender_manifest.toml` for Blender 4.2+:
```toml
schema_version = "1.0.0"
id = "my_extension"
version = "1.0.0"
name = "My Extension"
```

### Performance Optimization
Recommends BMesh for batch operations:
```python
import bmesh

# Fast batch mesh editing
bm = bmesh.new()
bm.from_mesh(mesh)
# Operations here
bm.to_mesh(mesh)
bm.free()
```

## Common Use Cases

1. **Custom Tools & Operators**
   - Interactive 3D tools
   - Batch processing operations
   - Pipeline automation

2. **UI Extensions**
   - Custom panels and menus
   - Property editors
   - Addon preferences

3. **Geometry Processing**
   - Procedural modeling
   - Mesh analysis
   - Geometry nodes integration

4. **Material Systems**
   - Automated material creation
   - Shader network generation
   - Texture management

5. **Animation Tools**
   - Keyframe automation
   - Rig generation
   - Motion graphics

6. **Rendering Automation**
   - Batch rendering
   - Render farm integration
   - Output management

## Version-Specific Features

### Blender 3.6 LTS
- Light linking and shadow linking
- Cycles X improvements
- Legacy addon support

### Blender 4.0
- EEVEE Next renderer
- Principled BSDF v2
- Python 3.11 support

### Blender 4.1
- Asset Shelf system
- Enhanced Geometry Nodes
- New modifier types

### Blender 4.2 LTS
- Extensions platform
- Realtime compositor
- `blender_manifest.toml`

### Blender 5.0+ (Expected)
- Vulkan backend
- Further EEVEE improvements
- Python 3.12+ support

## Resources

- **Official API Documentation:** https://docs.blender.org/api/current/
- **Blender Extensions:** https://docs.blender.org/manual/en/latest/advanced/extensions/
- **Blender DevTalk:** https://devtalk.blender.org/
- **Release Notes:** https://wiki.blender.org/wiki/Reference/Release_Notes
- **Source Code:** https://projects.blender.org/blender/blender

## Best Practices Enforced

1. ✅ Version compatibility checks
2. ✅ Proper error handling
3. ✅ Context safety validation
4. ✅ Performance optimization
5. ✅ Clean registration patterns
6. ✅ Comprehensive documentation
7. ✅ Testing recommendations
8. ✅ Modern API usage

## Installation

This skill is already installed in your `.agent/skills/skills` directory. Just reference it in your prompts!

## Contributing

To improve this skill:
1. Test with different Blender versions
2. Report any API inconsistencies
3. Suggest additional version-specific features
4. Share real-world use cases

## License

MIT License - Use freely in your projects

---

**Ready to create amazing Blender Python code!** 🚀
