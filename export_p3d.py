bl_info = {
    "name": "Export Move3D files",
    "author": "Alexandre Boeuf",
    "version": (0, 9, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Export Move3D files (.p3d/.macro)",
    "category": "Import-Export"}

import bpy
from bpy.props import StringProperty


class ExportP3D(bpy.types.Operator):
    """Export scene or object to Move3D file(s)"""
    bl_idname = "export_scene.p3d"
    bl_label = "Export P3D"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob = StringProperty(
            default="*.p3d;*.macro",
            options={'HIDDEN'},
            )

    def execute(self, context):
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportP3D.bl_idname, text="Move3D (.p3d/.macro)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
