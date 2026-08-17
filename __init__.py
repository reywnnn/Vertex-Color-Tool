"""

Vertex Color Tool - Blender extension

 - Tool for coloring vertices with vertex colors, includes material setup and viewport toggle.

"""


import importlib

from . import constants
from . import utils
from . import properties
from . import operators
from . import ui


_MODULES = (constants, utils, properties, operators, ui)

# support for 'Reload Scripts' during development
if "_ADDON_LOADED" in locals():
    for _module in _MODULES:
        importlib.reload(_module)
_ADDON_LOADED = True


# modules with their own registration, the order matters
_REGISTERED_MODULES = (properties, operators, ui)


# register the add-on
def register():
    for module in _REGISTERED_MODULES:
        module.register()


# unregister the add-on
def unregister():
    for module in reversed(_REGISTERED_MODULES):
        module.unregister()
