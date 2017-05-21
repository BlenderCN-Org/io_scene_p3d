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
from bpy_extras.io_utils import ExportHelper
import os
import math

def meshesAreEquals(mA, mB):

    ''' Compares vertices and polygons of two given meshes to determine if
        they are geometrically the same i.e. if they have both the same
        vertices and faces '''

    if mA == mB:
        return True

    if mA.vertices == mB.vertices and mA.polygons == mB.polygons:
        return True

    # Comparing the number of vertices
    if len(mA.vertices) != len(mB.vertices):
        return False

    # Comparing the number of faces
    if len(mA.polygons) != len(mB.polygons):
        return False

    # Comparing faces
    for i in range(len(mA.polygons)):
        vA = mA.polygons[i].vertices
        vB = mB.polygons[i].vertices
        if len(vA) != len(vB):
            return False
        for j in range(len(vA)):
            if vA[j] != vB[j]:
                return False

    # Comparing vertices
    for i in range(len(mA.vertices)):
        vA = mA.vertices[i]
        vB = mB.vertices[i]
        for j in range(3):
            if vA.co[j] != vB.co[j]:
                return False

    # Meshes are equal
    return True

def sortMeshes(bpy):

    ''' Return a dictionary with:
            keys: the p3d name of geometrically equals meshes
            values: a list of the geometrically equals meshes '''

    # Returns None if their are no meshes
    if not bpy.data.objects:
        return None

    # First mesh is obviously always exported
    name = bpy.data.meshes[0].name.lower().replace(" ","_").replace(".","_")
    sortedMeshes = {name: [bpy.data.meshes[0]]}

    # For every following mesh in the scene ...
    for i in range(1, len(bpy.data.meshes)):
        found = False
        name = bpy.data.meshes[i].name.lower().replace(" ","_").replace(".","_")
        # ... compare it to evey mesh we already stored ...
        for item in sortedMeshes:
            if meshesAreEquals(bpy.data.meshes[i], sortedMeshes[item][0]):
                # we have this one already
                if len(name) < len(item):
                    # if it has a shorter name we update the key
                    sortedMeshes[name] = sortedMeshes[item]
                    del sortedMesh[item]
                    # and we add it to sortedMeshes[name]
                    sortedMeshes[name].append(bpy.data.meshes[i])
                else:
                    # otherwise we add it to sortedMeshes[item]
                    sortedMeshes[item].append(bpy.data.meshes[i])
                found = True
                break
        #  ... and store it if need be in a new item
        if not found:
            sortedMeshes[name] = [bpy.data.meshes[i]]

    return sortedMeshes

def writeString(file, string):
    ''' Write string into a file opened in byte mode with UTF+8 encoding '''
    file.write(bytes(string,"UTF+8"))

def exportMeshes(meshes, macrosPath):
    ''' Export meshes as separate .macro files into the directory macrosPath '''
    if not meshes:
        return
    for item in meshes:
        try:
            file = open(os.path.join(macrosPath, item + '.macro'), 'wb')
        except IOError:
            file = None
        if file:
            if meshes[item] and meshes[item][0].vertices and meshes[item][0].polygons:
                writeString(file, 'p3d_add_desc_poly '+item+'\n')
                for v in meshes[item][0].vertices:
                    writeString(file, '   p3d_add_desc_vert {0:.6f} {1:.6f} {2:.6f}\n'.format(v.co[0],v.co[1],v.co[2]))
                writeString(file, '\n')
                for f in meshes[item][0].polygons:
                    if f.vertices:
                        writeString(file, '   p3d_add_desc_face ')
                        for i in f.vertices:
                            writeString(file, '{0} '.format(i+1))
                        writeString(file, '\n')
                writeString(file, 'p3d_end_desc_poly\n')

def addObject(ob, macroName, filepath):
    if not ob:
        return None
    try:
        file = open(filepath, 'ab')
    except IOError:
        file = None
    if file:
        obName = ob.name.lower().replace(" ","_").replace(".","_")
        writeString(file, 'p3d_read_macro ')
        writeString(file, macroName)
        writeString(file, '.macro ')
        writeString(file, obName)
        writeString(file, '\np3d_set_prim_pos ')
        writeString(file, obName)
        writeString(file, '.' + macroName)
        writeString(file, ' {0:.6f}'.format(ob.location[0]))
        writeString(file, ' {0:.6f}'.format(ob.location[1]))
        writeString(file, ' {0:.6f}'.format(ob.location[2]))
        ob.rotation_mode = 'XYZ'
        writeString(file, ' {0:.6f}'.format(math.degrees(ob.rotation_euler[0])))
        writeString(file, ' {0:.6f}'.format(math.degrees(ob.rotation_euler[1])))
        writeString(file, ' {0:.6f}'.format(math.degrees(ob.rotation_euler[2])))
        if ob.active_material and ob.active_material.diffuse_color:
            writeString(file, '\np3d_set_prim_color ')
            writeString(file, obName)
            writeString(file, '.' + macroName)
            writeString(file, ' Any {0:.6f}'.format(ob.active_material.diffuse_color[0]))
            writeString(file, ' {0:.6f}'.format(ob.active_material.diffuse_color[1]))
            writeString(file, ' {0:.6f}'.format(ob.active_material.diffuse_color[2]))
            writeString(file, '\n\n')
        else:
            writeString(file, '\n\n')

def exportObjects(bpy, meshes, filepath):
    ''' Assemble all objects in .macro file referencing the other .macro files '''
    if meshes:
        try:
            file = open(filepath, 'wb')
        except IOError:
            file = None
        if file:
            file.close()
            for item in meshes:
                for m in meshes[item]:
                    ob = bpy.data.objects[m.name]
                    if ob:
                        addObject(ob, item, filepath)

def exportScene(bpy, dirname, filename):
    meshes = sortMeshes(bpy)
    exportMeshes(meshes, dirname)
    exportObjects(bpy, meshes, os.path.join(dirname, filename))

class ExportP3D(bpy.types.Operator, ExportHelper):
    """Export scene or object to Move3D file(s)"""
    bl_idname = "export_scene.p3d"
    bl_label = "Export P3D"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".macro"
    filter_glob = StringProperty(
            default="*.macro",
            options={'HIDDEN'},
            )
    def execute(self, context):
        (dirname, filename) = os.path.split(self.properties.filepath)
        exportScene(bpy, dirname, filename)
        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(ExportP3D.bl_idname, text="Move3D (.p3d/.macro)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
