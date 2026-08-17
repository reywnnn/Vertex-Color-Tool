"""

User interface of the add-on.

"""


import bpy
import importlib

from . import panel


_MODULES = (panel,)

# support for 'Reload Scripts' during development
if "_UI_LOADED" in locals():
    for _module in _MODULES:
        importlib.reload(_module)
_UI_LOADED = True


from .panel import VIEW3D_PT_vertex_color_tool


# tuple of every class to register
classes = (
    VIEW3D_PT_vertex_color_tool,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
