"""

Working with mesh data and color attributes.

"""


import bpy

from contextlib import contextmanager

from ..constants import COLOR_ATTRIBUTE_NAME, ERROR_MSG_ATTRIBUTE, ERROR_MSG_NO_MESH, MESH_TYPE
from .validation import validate_color_attribute
from .viewport import tag_redraw_view3d


# context manager that switches the object to object mode and restores the original mode afterwards
@contextmanager
def temporary_object_mode(obj):
    original_mode = obj.mode

    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    try:
        yield
    finally:
        if obj.mode != original_mode:
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except RuntimeError as e:
                print(f"Vertex Color Tool: could not restore mode: {e}")


# generator yielding the color attribute indices that belong to selected vertices
# - must be called in object mode, where the selection is flushed into the mesh data
# - respects the attribute domain ('POINT' = per vertex, 'CORNER' = per loop)
def iter_selected_color_indices(mesh, color_layer):
    if color_layer.domain == 'POINT':
        for index, vert in enumerate(mesh.vertices):
            if vert.select:
                yield index
    else:
        vertices = mesh.vertices
        for index, loop in enumerate(mesh.loops):
            if vertices[loop.vertex_index].select:
                yield index


# shared helper for every vertex color operation
def apply_vertex_color_operation(context, operation_callback, operation_name):
    obj = context.active_object

    # check the active object
    if not obj or obj.type != MESH_TYPE:
        return ('CANCELLED', 'ERROR', ERROR_MSG_NO_MESH)

    mesh = obj.data

    # check the color attribute
    if not validate_color_attribute(mesh):
        return ('CANCELLED', 'ERROR', ERROR_MSG_ATTRIBUTE)

    # check edit mode BEFORE switching
    if obj.mode != 'EDIT':
        return ('CANCELLED', 'ERROR', f"Must be in Edit Mode to apply {operation_name}.")

    # counter of the modified vertices
    modified_count = 0

    # switch to object mode to access the data, the mode is restored automatically
    with temporary_object_mode(obj):
        try:
            color_layer = mesh.color_attributes[COLOR_ATTRIBUTE_NAME]
            color_data = color_layer.data

            # apply the operation to the selected vertices
            for index in iter_selected_color_indices(mesh, color_layer):
                current_color = color_data[index].color

                # call the callback that computes the new color
                color_data[index].color = operation_callback(current_color, index, context)
                modified_count += 1
        except (KeyError, AttributeError, RuntimeError) as e:
            return ('CANCELLED', 'ERROR', f"Failed to access mesh data: {e}")
        finally:
            mesh.update()

    # refresh the 3D viewport
    tag_redraw_view3d(context)

    # report the result of the operation
    if modified_count > 0:
        return ('FINISHED', 'INFO', f"{operation_name} applied to {modified_count} vertices.")

    return ('FINISHED', 'WARNING', "No vertices selected.")
