"""

Scene properties of the add-on.

"""


import bpy

from .constants import DESC_BRIGHTNESS


# list of property names used when unregistering
_SCENE_PROPERTIES = (
    "vtx_color_picker",
    "vtx_color_picker_expand",
    "vtx_original_colors",
    "vtx_brightness_slider",
)


# register the properties
def register():
    # register the color picker property
    bpy.types.Scene.vtx_color_picker = bpy.props.FloatVectorProperty(
        name="Vertex Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        description="Color to apply to selected vertices",
    )

    # register the expand property of the collapsible section
    bpy.types.Scene.vtx_color_picker_expand = bpy.props.BoolProperty(
        name="Expand Vertex Color Painter",
        default=True,
        description="Expand or collapse the Vertex Color Painter section",
    )

    # register the property that caches the original colors
    bpy.types.Scene.vtx_original_colors = bpy.props.StringProperty(
        name="Original Colors Cache",
        default="",
        description="Cache for storing original vertex colors before brightness adjustment",
    )

    # register the brightness slider property
    bpy.types.Scene.vtx_brightness_slider = bpy.props.FloatProperty(
        name="Brightness",
        default=1.0,
        min=0.0,
        max=1.0,
        precision=2,
        description=DESC_BRIGHTNESS,
    )


# unregister the properties
def unregister():
    for prop in _SCENE_PROPERTIES:
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
