"""

Operators of the add-on.

"""


import bpy
import importlib

from . import apply_color
from . import brightness
from . import prepare
from . import toggle


_MODULES = (apply_color, brightness, prepare, toggle)

# support for 'Reload Scripts' during development
if "_OPERATORS_LOADED" in locals():
    for _module in _MODULES:
        importlib.reload(_module)
_OPERATORS_LOADED = True


from .apply_color import VTXCOLOR_OT_apply_color
from .brightness import VTXCOLOR_OT_apply_brightness
from .prepare import VTXCOLOR_OT_prepare_material
from .toggle import VTXCOLOR_OT_toggle_display


# tuple of every class to register
classes = (
    VTXCOLOR_OT_prepare_material,
    VTXCOLOR_OT_apply_color,
    VTXCOLOR_OT_apply_brightness,
    VTXCOLOR_OT_toggle_display,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
