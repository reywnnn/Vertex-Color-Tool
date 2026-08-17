"""

Operator that applies brightness to the selected vertices.

"""


import bpy
import json

from ..constants import COLOR_ATTRIBUTE_NAME, DESC_BRIGHTNESS, ERROR_MSG_ATTRIBUTE
from ..utils import (
    apply_vertex_color_operation,
    iter_selected_color_indices,
    temporary_object_mode,
    validate_for_vertex_operation,
)


# helper that returns a dict of {index: [r, g, b]} for the currently selected vertices
def _collect_original_colors(obj):
    mesh = obj.data
    original_colors = {}

    # the attribute data can only be accessed in object mode
    with temporary_object_mode(obj):
        color_layer = mesh.color_attributes[COLOR_ATTRIBUTE_NAME]
        color_data = color_layer.data

        for index in iter_selected_color_indices(mesh, color_layer):
            current_color = color_data[index].color
            original_colors[str(index)] = [
                current_color[0],
                current_color[1],
                current_color[2],
            ]

    return original_colors


# operator class that applies brightness to the selected vertices
class VTXCOLOR_OT_apply_brightness(bpy.types.Operator):
    bl_idname = "mesh.apply_vertex_brightness"
    bl_label = "Apply Brightness"
    bl_description = DESC_BRIGHTNESS
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # full validation of the object and the material
        success, error_type, error_message = validate_for_vertex_operation(context)
        if not success:
            self.report({error_type}, error_message)
            return {'CANCELLED'}

        obj = context.active_object
        mesh = obj.data

        if COLOR_ATTRIBUTE_NAME not in mesh.color_attributes:
            self.report({'ERROR'}, ERROR_MSG_ATTRIBUTE)
            return {'CANCELLED'}

        # check whether the original colors have already been stored
        if not context.scene.vtx_original_colors:
            original_colors = _collect_original_colors(obj)

            if not original_colors:
                self.report({'WARNING'}, "No vertices selected.")
                return {'CANCELLED'}

            # store the original colors in the cache
            context.scene.vtx_original_colors = json.dumps(original_colors)
            self.report({'INFO'}, f"Original colors stored for {len(original_colors)} vertex loops.")

        # load the cache once instead of once per vertex
        try:
            original_colors = json.loads(context.scene.vtx_original_colors)
        except ValueError:
            original_colors = {}

        # callback that returns the brightened color
        def apply_brightness_callback(current_color, index, context):
            orig_color = original_colors.get(str(index))
            if orig_color is None:
                return current_color

            brightness = context.scene.vtx_brightness_slider
            return (
                orig_color[0] * brightness,
                orig_color[1] * brightness,
                orig_color[2] * brightness,
                1.0,
            )

        # run the shared operation
        status, msg_type, message = apply_vertex_color_operation(
            context, apply_brightness_callback, "Brightness"
        )

        self.report({msg_type}, message)
        return {status}
