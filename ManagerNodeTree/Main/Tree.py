import bpy
from .. import bl_info

class ManagerTree(bpy.types.NodeTree):
    bl_idname = 'ManagerNodeTree'
    bl_label = "Manager Node Tree"
    bl_icon = 'FILE_BLEND'
ManagerTree.__doc__ = bl_info['description']

Wh.Lc(ManagerTree)