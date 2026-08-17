"""

User interface panel in the 3D View sidebar.

"""


import bpy

from ..constants import MESH_TYPE, UI_SCALE_LARGE, UI_SCALE_MEDIUM
from ..utils import (
    get_viewport_shading_type,
    is_vertex_toggle_enabled,
    validate_color_attribute,
    validate_material_prepared,
)


# panel class of the user interface
class VIEW3D_PT_vertex_color_tool(bpy.types.Panel):
    bl_label = "Vertex Color Tool"
    bl_idname = "VIEW3D_PT_vertex_color_tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Vertex Color Tool"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # button that prepares the material
        row = layout.row()
        row.scale_y = UI_SCALE_LARGE
        row.operator("material.prepare_vtx_color", text="Prepare Material", icon='MATERIAL')

        # dynamic vertex color toggle button with state detection
        shading_color_type = get_viewport_shading_type(context, 'color_type', 'MATERIAL')
        toggle_enabled = is_vertex_toggle_enabled(context)

        # set the icon and the state of the button according to the shading type
        row = layout.row()
        row.scale_y = UI_SCALE_LARGE
        row.enabled = toggle_enabled

        if shading_color_type == 'VERTEX':
            row.operator(
                "view3d.vtxcolor_toggle",
                text="Hide Vertex Colors",
                icon='HIDE_ON',
            )
        else:
            row.operator(
                "view3d.vtxcolor_toggle",
                text="Show Vertex Colors",
                icon='HIDE_OFF',
            )

        # info message shown when the button is disabled
        if not toggle_enabled:
            info_row = layout.row()
            info_row.label(text="Switch to Solid Shading Type", icon='INFO')

        # collapsible color picker section
        box = layout.box()

        # header with the expand arrow on the right
        row = box.row()
        row.scale_y = UI_SCALE_MEDIUM
        row.label(text="Vertex Color Painter", icon='COLOR')
        row.alignment = 'RIGHT'
        row.prop(
            context.scene, "vtx_color_picker_expand",
            icon="TRIA_DOWN" if context.scene.vtx_color_picker_expand else "TRIA_RIGHT",
            icon_only=True, emboss=False,
        )

        # the content is only drawn when the section is expanded
        if not context.scene.vtx_color_picker_expand:
            return

        # check the prepared state
        is_prepared = False
        warning_msg = []

        if obj and obj.type == MESH_TYPE:
            mesh = obj.data

            if not validate_material_prepared(mesh):
                warning_msg.append("Material not prepared")

            if not validate_color_attribute(mesh):
                warning_msg.append("Color attribute missing")

            if not warning_msg:
                is_prepared = True
        else:
            warning_msg.append("No mesh object selected")

        # color picker
        row = box.row()
        row.prop(context.scene, "vtx_color_picker", text="")

        # brightness slider
        row = box.row()
        row.prop(context.scene, "vtx_brightness_slider", slider=True)

        can_apply = is_prepared and obj and obj.mode == 'EDIT'

        # 'apply to selected' button
        row = box.row()
        row.scale_y = UI_SCALE_MEDIUM
        row.enabled = can_apply
        row.operator("mesh.apply_vertex_color", text="Apply to Selected", icon='BRUSH_DATA')

        # apply brightness button
        row = box.row()
        row.scale_y = UI_SCALE_MEDIUM
        row.enabled = can_apply
        row.operator("mesh.apply_vertex_brightness", text="Apply Brightness", icon='LIGHT_SUN')

        # warnings displayed at the end
        for msg in warning_msg:
            row = box.row()
            row.alert = True
            row.label(text=msg, icon='ERROR')

        # mode info
        if obj and obj.mode != 'EDIT':
            row = box.row()
            row.label(text="Switch to Edit Mode", icon='INFO')
