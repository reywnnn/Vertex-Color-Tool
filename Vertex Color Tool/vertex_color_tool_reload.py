"""

Development Reload Button

    - Not tested with previous Blender versions.
    - Development tool for reloading this plugin via the Blender API.

"""


import bpy
import importlib
import importlib.util
import sys


bl_info = {
    "name": "Vertex Color Tool Reloader",
    "author": "Pavel Círus, aka Reywn",
    "version": (1, 0, 5),
    "blender": (4, 5, 2),
    "location": "View3D > Sidebar > Reloader",
    "description": "Vertex Color Tool reload button",
    "category": "Reloader",
}


# třída operátoru pro načtení addonu z konkrétní cesty
class DEV_RELOAD_base(bpy.types.Operator):
    bl_idname = "dev.reload_vertex_addon"
    bl_label = "Reload Vertex Color Tool"
    bl_description = "Reloads vertex_color_tool.py from specific path"

    def execute(self, context):
        addon_name = "Vertex Color Tool"
        addon_path = "C:/Users/pavel/AppData/Roaming/Blender Foundation/Blender/4.5/scripts/addons/vertex_color_tool.py"

        try:
            if addon_name in sys.modules:
                del sys.modules[addon_name]
                self.report({'INFO'}, f"Addon: '{addon_name}' removed from cache")

            spec = importlib.util.spec_from_file_location(addon_name, addon_path)
            if spec is None:
                raise Exception(f"Cannot load spec from addon: '{addon_path}'")
            
            module = importlib.util.module_from_spec(spec)
            if module is None:
                raise Exception(f"Cannot create addon from spec")

            sys.modules[addon_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                module.register()
                self.report({'INFO'}, f"Addon: '{addon_name}' reloaded successfully")
            else:
                self.report({'WARNING'}, f"Addon: '{addon_name}' has no register function()")

        except FileNotFoundError:
            self.report({'ERROR'}, f"File not found: '{addon_path}'")
        except Exception as e:
            self.report({'ERROR'}, f"Error reloading: {str(e)}")
            if addon_name in sys.modules:
                del sys.modules[addon_name]
            
        return {'FINISHED'}


# třída panelu pro uživatelské rozhraní
class DEV_RELOAD_panel(bpy.types.Panel):
    bl_label = "Vertex Color Tool Reloader"
    bl_idname = "DEV_RELOAD_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Reloader"

    def draw(self, context):
        layout = self.layout
        layout.operator("dev.reload_vertex_addon")
        layout.scale_x = 1.0 
        layout.scale_y = 2.0


# tuple všech tříd pro registraci
classes = (
    DEV_RELOAD_base, 
    DEV_RELOAD_panel
)


# funkce pro registraci pluginu a properties
def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# funkce pro odregistraci pluginu a properties
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
