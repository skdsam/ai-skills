# How to Use Your Blender Dev Expert Skill

## 🎉 Success! Your Blender AI Agent is Ready!

I've created a comprehensive Blender development agent skill for you that covers **Blender 3.6 to 5.0+** with version-aware development capabilities.

## 📁 What Was Created

Your new skill is located at:
```
C:\Users\skdso\.gemini\antigravity\scratch\.agent\skills\skills\blender-dev-expert\
```

### Files Created:

1. **SKILL.md** (13.7 KB)
   - Main skill definition with YAML frontmatter
   - Comprehensive Blender API knowledge
   - Version-specific guidance for 3.6, 4.0, 4.1, 4.2, 5.0+
   - Production-ready code patterns

2. **README.md** (6.0 KB)
   - User-friendly documentation
   - Usage examples and common use cases
   - Feature highlights and capabilities
   - Version-specific features overview

3. **QUICK_REFERENCE.md** (8.3 KB)
   - Code snippets and patterns
   - Version migration checklists
   - Performance tips and gotchas
   - Common API operations

4. **example_addon.py** (9.3 KB)
   - Working Blender addon example
   - Demonstrates version detection
   - Custom operator and panel
   - Version-aware Principled BSDF setup

## 🚀 How to Use the Skill

### In Antigravity IDE (Current Setup)

Simply reference the skill in your requests:

```
Use the @blender-dev-expert skill to create a Blender 4.2 
extension that batch exports FBX files
```

Or more naturally:
```
I need to create a material generator for Blender 4.0+
```

The agent will automatically detect and use the skill!

### Example Requests You Can Make:

1. **Create Addons/Extensions**
   ```
   Create a Blender 4.2 extension that automatically UVs 
   selected objects with smart projection
   ```

2. **Write Automation Scripts**
   ```
   Write a script to batch render all cameras in the scene 
   using Cycles, compatible with Blender 3.6+
   ```

3. **Version Migration**
   ```
   Help me migrate this Blender 3.6 addon to work with 
   the Blender 4.2 extensions platform
   ```

4. **API Questions**
   ```
   How do I programmatically create a material using the 
   new Principled BSDF v2 in Blender 4.0?
   ```

5. **Complex Tools**
   ```
   Create a modal operator for interactive mesh editing 
   that works in Blender 4.1+
   ```

## 🎯 What the Skill Provides

### Version-Aware Development
- ✅ Automatic version detection (3.6, 4.0, 4.1, 4.2, 5.0+)
- ✅ API compatibility checking
- ✅ Version-specific code patterns
- ✅ Migration guidance between versions

### Complete API Coverage
- ✅ **Core API:** bpy.data, bpy.ops, bpy.context, bpy.types
- ✅ **Addons:** Operators, panels, properties, registration
- ✅ **Extensions:** Blender 4.2+ manifest system
- ✅ **Geometry:** Mesh ops, BMesh, modifiers
- ✅ **Materials:** Node-based shading, Principled BSDF
- ✅ **Animation:** Keyframes, drivers, constraints
- ✅ **Rendering:** Cycles, EEVEE, compositor
- ✅ **I/O:** Import/export, asset libraries

### Production-Ready Code
- ✅ Error handling and validation
- ✅ Context safety checks
- ✅ Performance optimization (BMesh vs operators)
- ✅ Comprehensive documentation
- ✅ Testing recommendations

## 📚 Version Support

| Version | Release | Python | Key Features |
|---------|---------|--------|--------------|
| **3.6 LTS** | June 2023 | 3.10 | Light Linking, Cycles X |
| **4.0** | Nov 2023 | 3.11 | EEVEE Next, Principled v2 |
| **4.1** | Mar 2024 | 3.11 | Asset Shelf, Enhanced Geometry Nodes |
| **4.2 LTS** | July 2024 | 3.11 | Extensions Platform, Realtime Compositor |
| **5.0+** | Future | 3.12+ | Vulkan, Further Improvements |

## 🧪 Test It Out!

Try the example addon:

1. Open Blender (3.6 or higher)
2. Go to Scripting workspace
3. Open `example_addon.py`
4. Click "Run Script"
5. Find the panel in 3D Viewport > Sidebar > Materials tab
6. Select an object and click "Create Material"

The addon will automatically detect your Blender version and use 
the appropriate API!

## 💡 Pro Tips

### 1. Always Specify Version
When making requests, mention your target Blender version:
```
For Blender 4.2, create an extension that...
```

### 2. Ask About Compatibility
```
Will this code work in both Blender 3.6 and 4.2?
```

### 3. Request Migration Help
```
Migrate this 3.6 addon to 4.2 extension format
```

### 4. Get Version-Specific Info
```
What changed in the Principled BSDF between 3.6 and 4.0?
```

### 5. Performance Optimization
```
Optimize this script using BMesh instead of operators
```

## 🔧 Common Use Cases

1. **Pipeline Automation**
   - Batch processing
   - Asset preparation
   - Export automation

2. **Custom Tools**
   - Modeling helpers
   - UV utilities
   - Material generators

3. **Integration**
   - Game engine exporters
   - Render farm tools
   - Asset management

4. **Workflow Enhancement**
   - Custom panels
   - Procedural systems
   - Animation tools

## 📖 Learning Resources

The skill includes references to:
- Official Blender Python API docs
- Blender DevTalk forums
- Release notes for each version
- Source code repository

## 🎨 Example Output

When you use the skill, you'll get:

```python
"""
Blender 4.2 Extension - Auto UV Mapper
Compatible with Blender 4.2+
"""

# Version check
import bpy

if bpy.app.version < (4, 2, 0):
    raise RuntimeError("This extension requires Blender 4.2+")

# Extension manifest (blender_manifest.toml)
"""
schema_version = "1.0.0"
id = "auto_uv_mapper"
version = "1.0.0"
name = "Auto UV Mapper"
...
"""

# Full working code with:
# - Error handling
# - Context checks
# - Performance optimization
# - Documentation
# - Registration
```

## ✅ Next Steps

1. **Try It Out:** Make a request using the skill
2. **Explore Examples:** Check the example_addon.py
3. **Read Quick Reference:** See QUICK_REFERENCE.md for common patterns
4. **Build Something:** Create your first Blender tool!

## 🆘 Troubleshooting

If the skill doesn't seem to be working:

1. Make sure you're in the Antigravity IDE
2. Mention "blender" or "bpy" in your request
3. Explicitly reference: "Use the blender-dev-expert skill"
4. Check that the skill files are in the correct location

## 📝 Skill Location

```
C:\Users\skdso\.gemini\antigravity\scratch\.agent\skills\skills\blender-dev-expert\
├── SKILL.md              # Main skill definition
├── README.md             # User documentation
├── QUICK_REFERENCE.md    # Code snippets
└── example_addon.py      # Working example
```

---

## 🎊 You're All Set!

Your Blender AI agent is ready to help you create amazing Python 
scripts, addons, and extensions for Blender 3.6 through 5.0+!

Just start asking questions and the agent will:
- ✅ Detect your Blender version
- ✅ Provide compatible code
- ✅ Warn about version-specific issues
- ✅ Suggest modern best practices
- ✅ Generate production-ready solutions

**Happy Blending! 🎨🚀**
