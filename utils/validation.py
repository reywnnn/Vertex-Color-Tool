"""

Validation helpers for objects, materials and color attributes.

"""


from ..constants import ERROR_MSG_MATERIAL, ERROR_MSG_NO_MESH, COLOR_ATTRIBUTE_NAME, MATERIAL_NAME, MESH_TYPE


# helper for validating the active mesh object
def validate_active_mesh_object(context):
    obj = context.active_object
    if not obj or obj.type != MESH_TYPE:
        return None, ERROR_MSG_NO_MESH
    return obj, None


# helper for checking the color attribute
def validate_color_attribute(mesh):
    return COLOR_ATTRIBUTE_NAME in mesh.color_attributes


# helper for checking whether the material is prepared
def validate_material_prepared(mesh):
    for mat in mesh.materials:
        if mat and mat.name == MATERIAL_NAME:
            return True
    return False


# helper for the full validation done before vertex operations
def validate_for_vertex_operation(context):
    obj, error = validate_active_mesh_object(context)
    if error:
        return False, 'ERROR', error

    mesh = obj.data

    if not validate_material_prepared(mesh):
        return False, 'ERROR', ERROR_MSG_MATERIAL

    return True, None, None
