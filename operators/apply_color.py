"""

Operator that applies the picked color to the selected vertices.

"""


import bpy

from ..constants import DESC_APPLY
from ..utils import apply_vertex_color_operation, validate_for_vertex_operation


# operator class that applies the color to the selected vertices
class VTXCOLOR_OT_apply_color(bpy.types.Operator):
    bl_idname = "mesh.apply_vertex_color"
    bl_label = "Apply Color"
    bl_description = DESC_APPLY
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # full validation of the object and the material
        success, error_type, error_message = validate_for_vertex_operation(context)
        if not success:
            self.report({error_type}, error_message)
            return {'CANCELLED'}

        # callback that returns the color to apply
        def apply_color_callback(current_color, index, context):
            color = context.scene.vtx_color_picker
            return (color[0], color[1], color[2], 1.0)

        # run the shared operation
        status, msg_type, message = apply_vertex_color_operation(
            context, apply_color_callback, "Color"
        )

        self.report({msg_type}, message)
        return {status}
