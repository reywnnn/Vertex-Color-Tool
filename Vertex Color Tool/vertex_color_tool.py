"""

Vertex Color Tool Plugin For Blender 4.5.2

    - Previous versions not tested.
    - Tool for coloring vertices with vertex colors, includes material setup and viewport toggle.

"""


bl_info = {
    "name": "Vertex Color Tool",
    "author": "Pavel Círus, aka Reywn",
    "version": (1, 0, 3),
    "blender": (4, 5, 2),
    "location": "View3D > Sidebar > Vertex Color Tool",
    "description": "Tool for coloring vertices with vertex colors.",
    "category": "Vertex Color",
}


import bpy
import bmesh


COLOR_ATTRIBUTE_NAME = "colorset1"
MATERIAL_NAME = "vtx_color_material"
MESH_TYPE = 'MESH'
UI_SCALE_LARGE = 2.0
UI_SCALE_MEDIUM = 1.5
ERROR_MSG_MATERIAL = "Material not prepared! Click 'Prepare Material' first."
ERROR_MSG_ATTRIBUTE = "Color Attribute not found! Click 'Prepare Material' first."
DESC_PREPARE = "Create and assign vertex color material with color attribute to the active mesh object"
DESC_APPLY = "Apply selected color to selected vertices in Edit Mode"
DESC_BRIGHTNESS = "Adjust brightness of selected vertices (0.0 = black, 1.0 = original)."
DESC_TOGGLE = "Toggle between Solid shading mode and Vertex Color display"


# funkce pro vytvoření materiálu s color attribute
def create_vtx_color_material():
    mat_name = MATERIAL_NAME
    material_created = False

    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
        if mat.node_tree and "Attribute" in mat.node_tree.nodes:
            return mat, False
    else:
        mat = bpy.data.materials.new(name=mat_name)
        material_created = True

    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    output.location = (400, 0)

    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    principled.location = (0, 0)

    attrib = nodes.new(type="ShaderNodeAttribute")
    attrib.attribute_name = COLOR_ATTRIBUTE_NAME
    attrib.location = (-300, 0)

    links.new(attrib.outputs["Color"], principled.inputs["Base Color"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    return mat, material_created


# pomocná funkce pro práci s vertex colors
def apply_vertex_color_operation(context, operation_callback, operation_name):
    obj = context.active_object
    
    if not obj or obj.type != MESH_TYPE:
        return ('CANCELLED', 'ERROR', "No active mesh object.")
    
    mesh = obj.data
    
    if not validate_color_attribute(mesh):
        return ('CANCELLED', 'ERROR', ERROR_MSG_ATTRIBUTE)
    
    if obj.mode != 'EDIT':
        return ('CANCELLED', 'ERROR', f"Must be in Edit Mode to apply {operation_name}.")
    
    original_mode = obj.mode
    
    if obj.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        
        if COLOR_ATTRIBUTE_NAME not in mesh.color_attributes:
            return ('CANCELLED', 'ERROR', ERROR_MSG_ATTRIBUTE)
        color_layer = mesh.color_attributes[COLOR_ATTRIBUTE_NAME]
    except Exception as e:
        bm.free()
        return ('CANCELLED', 'ERROR', f"Failed to access mesh data: {str(e)}")
    
    modified_count = 0
    
    try:
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.select:
                    loop_index = loop.index
                    current_color = color_layer.data[loop_index].color

                    new_color = operation_callback(current_color, loop_index, context)
                    
                    color_layer.data[loop_index].color = new_color
                    modified_count += 1
    finally:
        bm.free()
        
        mesh.update()
        
        try:
            if obj and obj.mode != original_mode:
                bpy.ops.object.mode_set(mode=original_mode)
        except Exception as e:
            print(f"Warning: Could not restore mode: {str(e)}")
    
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
    
    if modified_count > 0:
        return ('FINISHED', 'INFO', f"{operation_name} applied to {modified_count} vertices.")
    else:
        return ('FINISHED', 'WARNING', "No vertices selected.")
    

# pomocná funkce pro získání 3D viewport shadingu
def get_viewport_shading(context):
    """získá shading objekt z aktivního 3D viewportu"""
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    return space.shading
    return None


# pomocná funkce pro získání shading typu
def get_viewport_shading_type(context, property_name, default_value):
    shading = get_viewport_shading(context)
    if shading and hasattr(shading, property_name):
        return getattr(shading, property_name, default_value)
    return default_value


# pomocná funkce pro kontrolu zda je vertex color toggle dostupný
def is_vertex_toggle_enabled(context):
    return get_viewport_shading_type(context, 'type', 'SOLID') == 'SOLID'


# pomocná funkce pro validaci aktivního mesh objektu
def validate_active_mesh_object(context):
    obj = context.active_object
    if not obj or obj.type != MESH_TYPE:
        return None, "No active mesh object."
    return obj, None


# pomocná funkce pro kontrolu color attribute
def validate_color_attribute(mesh):
    return COLOR_ATTRIBUTE_NAME in mesh.color_attributes


# pomocná funkce pro kontrolu, zda je materiál připraven
def validate_material_prepared(mesh):

    mat_name = MATERIAL_NAME
    for mat in mesh.materials:
        if mat and mat.name == mat_name:
            return True
    return False


# pomocná funkce pro kompletní validaci před aplikací vertex operací
def validate_for_vertex_operation(context):

    obj, error = validate_active_mesh_object(context)
    if error:
        return False, 'ERROR', error
    
    mesh = obj.data
    
    if not validate_material_prepared(mesh):
        return False, 'ERROR', ERROR_MSG_MATERIAL
    
    return True, None, None


# třída operátoru pro přípravu materiálu a color attribute
class VTXCOLOR_prepare(bpy.types.Operator):
    bl_idname = "material.prepare_vtx_color"
    bl_label = "Prepare Material"
    bl_description = DESC_PREPARE
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj, error = validate_active_mesh_object(context)
        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        mat, material_created = create_vtx_color_material()
        mesh = obj.data

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

        if COLOR_ATTRIBUTE_NAME in mesh.color_attributes:
            self.report({'WARNING'}, f"Color Attribute: '{mesh.color_attributes[COLOR_ATTRIBUTE_NAME].name}' already exists.")
        else:
            color_attr = mesh.color_attributes.new(
                name=COLOR_ATTRIBUTE_NAME,
                type='FLOAT_COLOR',
                domain='CORNER'
            )
            mesh.color_attributes.active_color = color_attr
            self.report({'INFO'}, "Color Attribute created and set as default for rendering.")

        return {'FINISHED'}


# třída operátoru pro aplikaci barvy na vybrané vertices
class VTXCOLOR_apply(bpy.types.Operator):
    bl_idname = "mesh.apply_vertex_color"
    bl_label = "Apply Color"
    bl_description = DESC_APPLY
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        success, error_type, error_message = validate_for_vertex_operation(context)
        if not success:
            self.report({error_type}, error_message)
            return {'CANCELLED'}
        
        def apply_color_callback(current_color, loop_index, context):
            color = context.scene.vtx_color_picker
            return (color[0], color[1], color[2], 1.0)
        
        status, msg_type, message = apply_vertex_color_operation(
            context, apply_color_callback, "Color"
        )
        
        self.report({msg_type}, message)
        return {status}


# třída operátoru pro aplikaci jasu na vybrané vertices
class VTXCOLOR_brightness(bpy.types.Operator):
    bl_idname = "mesh.apply_vertex_brightness"
    bl_label = "Apply Brightness"
    bl_description = DESC_BRIGHTNESS
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import json

        success, error_type, error_message = validate_for_vertex_operation(context)
        if not success:
            self.report({error_type}, error_message)
            return {'CANCELLED'}
        
        obj = context.active_object
        mesh = obj.data
        
        if COLOR_ATTRIBUTE_NAME not in mesh.color_attributes:
            self.report({'ERROR'}, ERROR_MSG_ATTRIBUTE)
            return {'CANCELLED'}
        
        original_mode = obj.mode
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        color_layer = mesh.color_attributes[COLOR_ATTRIBUTE_NAME]
        
        if not context.scene.vtx_original_colors:
            original_colors = {}
            bm = bmesh.new()
            try:
                bm.from_mesh(mesh)
                bm.verts.ensure_lookup_table()
                
                for face in bm.faces:
                    for loop in face.loops:
                        if loop.vert.select:
                            loop_idx = loop.index
                            current_color = color_layer.data[loop_idx].color
                            original_colors[str(loop_idx)] = [
                                current_color[0],
                                current_color[1], 
                                current_color[2]
                            ]
            finally:
                bm.free()
            
            if not original_colors:
                if obj.mode != original_mode:
                    bpy.ops.object.mode_set(mode=original_mode)
                self.report({'WARNING'}, "No vertices selected.")
                return {'CANCELLED'}
            
            context.scene.vtx_original_colors = json.dumps(original_colors)
            self.report({'INFO'}, f"Original colors stored for {len(original_colors)} vertex loops.")
        
        if obj.mode != original_mode:
            bpy.ops.object.mode_set(mode=original_mode)
        
        def apply_brightness_callback(current_color, loop_index, context):
            try:
                original_colors = json.loads(context.scene.vtx_original_colors)
            except:
                return current_color
            
            loop_key = str(loop_index)
            
            if loop_key in original_colors:
                orig_color = original_colors[loop_key]
                brightness = context.scene.vtx_brightness_slider
                return (
                    orig_color[0] * brightness,
                    orig_color[1] * brightness,
                    orig_color[2] * brightness,
                    1.0
                )
            return current_color
        
        status, msg_type, message = apply_vertex_color_operation(
            context, apply_brightness_callback, "Brightness"
        )
        
        self.report({msg_type}, message)
        return {status}


# třída operátoru pro přepínání zobrazení vertex colors
class VTXCOLOR_toggle(bpy.types.Operator):
    bl_idname = "view3d.vtxcolor_toggle"
    bl_label = "Toggle Vertex Color View"
    bl_description = DESC_TOGGLE
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        current_type = get_viewport_shading_type(context, 'color_type', 'MATERIAL')
    
        shading = get_viewport_shading(context)
        if shading:
            if current_type == 'VERTEX':
                shading.color_type = 'MATERIAL'
                shading_name = 'Solid'
            else:
                shading.color_type = 'VERTEX'
                shading_name = 'Vertex Color'
            self.report({'INFO'}, f"Shading Type set to {shading_name}")

        return {'FINISHED'}


# třída panelu pro uživatelské rozhraní
class VTXCOLOR_panel(bpy.types.Panel):
    bl_label = "Vertex Color Tool"
    bl_idname = "MATERIAL_PT_vtx_color_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Vertex Color Tool"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        row = layout.row()
        row.scale_y = UI_SCALE_LARGE
        row.operator("material.prepare_vtx_color", text="Prepare Material", icon='MATERIAL')
        
        shading_color_type = get_viewport_shading_type(context, 'color_type', 'MATERIAL')

        row = layout.row()
        row.scale_y = UI_SCALE_LARGE
        row.enabled = is_vertex_toggle_enabled(context)
        
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

        if not is_vertex_toggle_enabled(context):
            info_row = layout.row()
            info_row.label(text="Switch to Solid Shading Type", icon='INFO')

        box = layout.box()
        
        row = box.row()
        row.scale_y = UI_SCALE_MEDIUM
        row.label(text="Vertex Color Painter", icon='COLOR')
        row.alignment = 'RIGHT'
        row.prop(context.scene, "vtx_color_picker_expand", 
                 icon="TRIA_DOWN" if context.scene.vtx_color_picker_expand else "TRIA_RIGHT",
                 icon_only=True, emboss=False)
        
        if context.scene.vtx_color_picker_expand:
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
            
            row = box.row()
            row.prop(context.scene, "vtx_color_picker", text="")

            row = box.row()
            row.prop(context.scene, "vtx_brightness_slider", slider=True)
            
            can_apply = is_prepared and obj and obj.mode == 'EDIT'

            row = box.row()
            row.scale_y = UI_SCALE_MEDIUM
            row.enabled = can_apply
            row.operator("mesh.apply_vertex_color", text="Apply to Selected", icon='BRUSH_DATA')

            row = box.row()
            row.scale_y = UI_SCALE_MEDIUM
            row.enabled = can_apply
            row.operator("mesh.apply_vertex_brightness", text="Apply Brightness", icon='LIGHT_SUN')
            
            if warning_msg:
                for msg in warning_msg:
                    row = box.row()
                    row.alert = True
                    row.label(text=msg, icon='ERROR')
            
            if obj and obj.mode != 'EDIT':
                row = box.row()
                row.label(text="Switch to Edit Mode", icon='INFO')


# tuple všech tříd pro registraci
classes = (
    VTXCOLOR_prepare,
    VTXCOLOR_apply,
    VTXCOLOR_brightness,
    VTXCOLOR_toggle,
    VTXCOLOR_panel,
)


# funkce pro registraci pluginu a properties
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.vtx_color_picker = bpy.props.FloatVectorProperty(
        name="Vertex Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        description="Color to apply to selected vertices"
    )
    
    bpy.types.Scene.vtx_color_picker_expand = bpy.props.BoolProperty(
        name="Expand Vertex Color Painter",
        default=True,
        description="Expand or collapse the Vertex Color Painter section"
    )

    bpy.types.Scene.vtx_original_colors = bpy.props.StringProperty(
        name="Original Colors Cache",
        default="",
        description="Cache for storing original vertex colors before brightness adjustment"
    )

    bpy.types.Scene.vtx_brightness_slider = bpy.props.FloatProperty(
        name="Brightness",
        default=1.0,
        min=0.0,
        max=1.0,
        precision=2,
        description="Adjust brightness of selected vertices (0.0 = black, 1.0 = original)"
    )


# funkce pro odregistraci pluginu a properties
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    for prop in ['vtx_color_picker', 
                 'vtx_color_picker_expand',
                 'vtx_original_colors',
                 'vtx_brightness_slider']:
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
