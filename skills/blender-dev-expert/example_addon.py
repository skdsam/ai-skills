"""
Blender Development Expert Skill - Example Script
==================================================

This example demonstrates version-aware Blender Python development
across Blender 3.6 to 5.0+. It creates a custom addon with:
- Version detection
- Custom operator
- Custom panel
- Material creation with version-aware Principled BSDF

Compatible with Blender 3.6, 4.0, 4.1, 4.2, 5.0+
"""

bl_info = {
    "name": "Example: Version-Aware Material Creator",
    "author": "Blender Dev Expert Skill",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),  # Minimum version
    "location": "View3D > Sidebar > Materials Tab",
    "description": "Example addon showing version-aware Blender development",
    "warning": "",
    "doc_url": "",
    "category": "Material",
}

import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatVectorProperty, FloatProperty


# Utility function: Version detection
def get_blender_version():
    """Return Blender version as tuple (major, minor, patch)."""
    return bpy.app.version


def is_blender_4_plus():
    """Check if Blender 4.0 or higher."""
    return get_blender_version() >= (4, 0, 0)


def is_extensions_supported():
    """Check if Blender 4.2+ extensions are supported."""
    return get_blender_version() >= (4, 2, 0)


# Operator: Create version-aware material
class MATERIAL_OT_create_advanced(Operator):
    """Create a Principled material with version-aware setup"""
    bl_idname = "material.create_advanced"
    bl_label = "Create Advanced Material"
    bl_description = "Create a Principled BSDF material with version compatibility"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties
    base_color: FloatVectorProperty(
        name="Base Color",
        subtype='COLOR',
        default=(0.8, 0.2, 0.2, 1.0),
        min=0.0,
        max=1.0,
        size=4,
        description="Base color of the material"
    )
    
    metallic: FloatProperty(
        name="Metallic",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Metallic value"
    )
    
    roughness: FloatProperty(
        name="Roughness",
        default=0.5,
        min=0.0,
        max=1.0,
        description="Roughness value"
    )
    
    @classmethod
    def poll(cls, context):
        """Only enable if an object is selected."""
        return context.active_object is not None
    
    def execute(self, context):
        """Create and assign the material."""
        obj = context.active_object
        
        if obj is None:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        
        try:
            # Create material
            mat_name = f"AdvancedMat_{obj.name}"
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            
            # Get nodes
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Clear default nodes
            nodes.clear()
            
            # Create Principled BSDF
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
            
            # Version-aware BSDF setup
            version = get_blender_version()
            
            if version >= (4, 0, 0):
                # Blender 4.0+ with Principled BSDF v2
                bsdf.inputs['Base Color'].default_value = self.base_color
                bsdf.inputs['Metallic'].default_value = self.metallic
                bsdf.inputs['Roughness'].default_value = self.roughness
                
                # Blender 4.0+ specific features
                if 'Subsurface Weight' in bsdf.inputs:
                    bsdf.inputs['Subsurface Weight'].default_value = 0.0
                    
                version_info = "Blender 4.0+ (Principled BSDF v2)"
            else:
                # Blender 3.6 with legacy Principled BSDF
                bsdf.inputs['Base Color'].default_value = self.base_color
                bsdf.inputs['Metallic'].default_value = self.metallic
                bsdf.inputs['Roughness'].default_value = self.roughness
                
                # Blender 3.6 specific settings
                if 'Subsurface' in bsdf.inputs:
                    bsdf.inputs['Subsurface'].default_value = 0.0
                    
                version_info = "Blender 3.6 (Legacy Principled BSDF)"
            
            # Create Material Output
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (300, 0)
            
            # Link nodes
            links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
            
            # Assign material to object
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
            
            # Report success
            self.report(
                {'INFO'}, 
                f"Created material '{mat_name}' using {version_info}"
            )
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create material: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        """Show dialog before executing."""
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        """Draw the operator dialog."""
        layout = self.layout
        
        # Display Blender version
        version = get_blender_version()
        version_str = f"{version[0]}.{version[1]}.{version[2]}"
        
        box = layout.box()
        box.label(text=f"Blender Version: {version_str}", icon='INFO')
        
        if is_blender_4_plus():
            box.label(text="Using Principled BSDF v2", icon='CHECKMARK')
        else:
            box.label(text="Using Legacy Principled BSDF", icon='CHECKMARK')
        
        layout.separator()
        
        # Material properties
        layout.prop(self, "base_color")
        layout.prop(self, "metallic")
        layout.prop(self, "roughness")


# Panel: Display in 3D Viewport sidebar
class VIEW3D_PT_material_creator(Panel):
    """Panel in 3D Viewport sidebar"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Materials'  # Tab name
    bl_label = "Advanced Material Creator"
    bl_idname = "VIEW3D_PT_material_creator"
    
    def draw(self, context):
        """Draw the panel UI."""
        layout = self.layout
        
        # Version info
        version = get_blender_version()
        version_str = f"{version[0]}.{version[1]}.{version[2]}"
        
        box = layout.box()
        box.label(text="Version Information", icon='INFO')
        box.label(text=f"Blender: {version_str}")
        
        if is_blender_4_plus():
            box.label(text="✓ Blender 4.0+ Features", icon='CHECKMARK')
        
        if is_extensions_supported():
            box.label(text="✓ Extensions Supported", icon='CHECKMARK')
        
        layout.separator()
        
        # Active object info
        obj = context.active_object
        if obj:
            box = layout.box()
            box.label(text=f"Active: {obj.name}", icon='OBJECT_DATA')
            
            # Material count
            mat_count = len(obj.data.materials) if hasattr(obj.data, 'materials') else 0
            box.label(text=f"Materials: {mat_count}")
        else:
            layout.label(text="No object selected", icon='ERROR')
        
        layout.separator()
        
        # Operator button
        row = layout.row()
        row.scale_y = 2.0
        row.operator(
            "material.create_advanced",
            text="Create Material",
            icon='MATERIAL'
        )
        
        # Additional info
        layout.separator()
        box = layout.box()
        box.label(text="Features:", icon='PREFERENCES')
        box.label(text="• Version-aware BSDF")
        box.label(text="• Automatic compatibility")
        box.label(text="• Blender 3.6 to 5.0+ support")


# Registration
classes = (
    MATERIAL_OT_create_advanced,
    VIEW3D_PT_material_creator,
)


def register():
    """Register addon classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("=" * 60)
    print("Advanced Material Creator - Registered Successfully")
    print(f"Blender Version: {'.'.join(map(str, get_blender_version()))}")
    print(f"Blender 4.0+: {is_blender_4_plus()}")
    print(f"Extensions Support: {is_extensions_supported()}")
    print("Location: View3D > Sidebar > Materials Tab")
    print("=" * 60)


def unregister():
    """Unregister addon classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("Advanced Material Creator - Unregistered")


# For running as a script (not installed addon)
if __name__ == "__main__":
    register()
