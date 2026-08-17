"""

Helper functions of the add-on (material, mesh data, validation, viewport).

"""


import importlib

from . import material
from . import mesh
from . import validation
from . import viewport


_MODULES = (material, mesh, validation, viewport)

# support for 'Reload Scripts' during development
if "_UTILS_LOADED" in locals():
    for _module in _MODULES:
        importlib.reload(_module)
_UTILS_LOADED = True


from .material import create_vtx_color_material
from .mesh import (
    apply_vertex_color_operation,
    iter_selected_color_indices,
    temporary_object_mode,
)
from .validation import (
    validate_active_mesh_object,
    validate_color_attribute,
    validate_for_vertex_operation,
    validate_material_prepared,
)
from .viewport import (
    get_viewport_shading,
    get_viewport_shading_type,
    is_vertex_toggle_enabled,
    tag_redraw_view3d,
)


__all__ = (
    "create_vtx_color_material",
    "apply_vertex_color_operation",
    "iter_selected_color_indices",
    "temporary_object_mode",
    "validate_active_mesh_object",
    "validate_color_attribute",
    "validate_for_vertex_operation",
    "validate_material_prepared",
    "get_viewport_shading",
    "get_viewport_shading_type",
    "is_vertex_toggle_enabled",
    "tag_redraw_view3d",
)
