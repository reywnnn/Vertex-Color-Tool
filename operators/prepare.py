"""

Operator that prepares the material and the color attribute.

"""


import bpy

from ..constants import COLOR_ATTRIBUTE_NAME, DESC_PREPARE
from ..utils import create_vtx_color_material, validate_active_mesh_object


# helper that marks the attribute as the active one for rendering
def _set_as_active_color(mesh, color_attr):
    mesh.color_attributes.active_color = color_attr

    # explicitly set the names used by the renderer (Blender 3.2+)
    attributes = mesh.attributes
    if hasattr(attributes, "active_color_name"):
        attributes.active_color_name = color_attr.name
    if hasattr(attributes, "default_color_name"):
        attributes.default_color_name = color_attr.name


# operator class that prepares the material and the color attribute
class VTXCOLOR_OT_prepare_material(bpy.types.Operator):
    bl_idname = "material.prepare_vtx_color"
    bl_label = "Prepare Material"
    bl_description = DESC_PREPARE
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj, error = validate_active_mesh_object(context)
        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        # get or create the material
        mat, material_created = create_vtx_color_material()
        mesh = obj.data

        # assign the material to the object, checking whether it is already assigned
        if mat.name not in [m.name for m in mesh.materials if m is not None]:
            mesh.materials.append(mat)
            if material_created:
                self.report({'INFO'}, f"Material: '{mat.name}' created and assigned to object.")
            else:
                self.report({'INFO'}, f"Material: '{mat.name}' assigned to object.")
        else:
            if material_created:
                self.report({'WARNING'}, f"Material: '{mat.name}' created (already assigned).")
            else:
                self.report({'WARNING'}, f"Material: '{mat.name}' already assigned to object.")

        # create the color attribute, checking whether it already exists
        if COLOR_ATTRIBUTE_NAME in mesh.color_attributes:
            existing = mesh.color_attributes[COLOR_ATTRIBUTE_NAME]
            self.report({'WARNING'}, f"Color Attribute: '{existing.name}' already exists.")
        else:
            color_attr = mesh.color_attributes.new(
                name=COLOR_ATTRIBUTE_NAME,
                type='FLOAT_COLOR',
                domain='CORNER',
            )
            # set it as the active color attribute for rendering
            _set_as_active_color(mesh, color_attr)
            self.report({'INFO'}, "Color Attribute created and set as default for rendering.")

        return {'FINISHED'}
