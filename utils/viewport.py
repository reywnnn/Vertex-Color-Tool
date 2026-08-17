"""

Helper functions for working with the 3D viewport and its shading.

"""


# helper for getting the shading object of the active 3D viewport
def get_viewport_shading(context):
    screen = getattr(context, "screen", None)
    if screen is None:
        return None

    for area in screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    return space.shading
    return None


# helper for reading a single shading property
def get_viewport_shading_type(context, property_name, default_value):
    shading = get_viewport_shading(context)
    if shading and hasattr(shading, property_name):
        return getattr(shading, property_name, default_value)
    return default_value


# helper for checking whether the vertex color toggle is available
def is_vertex_toggle_enabled(context):
    return get_viewport_shading_type(context, 'type', 'SOLID') == 'SOLID'


# helper for redrawing every 3D viewport
def tag_redraw_view3d(context):
    screen = getattr(context, "screen", None)
    if screen is None:
        return

    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
