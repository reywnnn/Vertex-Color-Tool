"""

Operator that toggles the vertex color display in the viewport.

"""


import bpy

from ..constants import DESC_TOGGLE
from ..utils import get_viewport_shading, get_viewport_shading_type


# operator class that toggles the vertex color display
class VTXCOLOR_OT_toggle_display(bpy.types.Operator):
    bl_idname = "view3d.vtxcolor_toggle"
    bl_label = "Toggle Vertex Color View"
    bl_description = DESC_TOGGLE
    bl_options = {'REGISTER', 'UNDO'}

    # switch between material (solid) and vertex color
    def execute(self, context):
        current_type = get_viewport_shading_type(context, 'color_type', 'MATERIAL')

        shading = get_viewport_shading(context)
        if shading is None:
            self.report({'WARNING'}, "No 3D Viewport found.")
            return {'CANCELLED'}

        if current_type == 'VERTEX':
            shading.color_type = 'MATERIAL'
            shading_name = 'Solid'
        else:
            shading.color_type = 'VERTEX'
            shading_name = 'Vertex Color'

        self.report({'INFO'}, f"Shading Type set to {shading_name}")
        return {'FINISHED'}
