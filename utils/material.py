"""

Creation and setup of the material with a color attribute.

"""


import bpy

from ..constants import COLOR_ATTRIBUTE_NAME, MATERIAL_NAME


# helper for finding a socket by its name or its identifier
def _find_socket(sockets, name):
    socket = sockets.get(name)
    if socket is not None:
        return socket

    # fallback in case the sockets were renamed in a newer Blender version
    for candidate in sockets:
        if candidate.identifier == name:
            return candidate
    return None


# function that builds the material with a color attribute
def create_vtx_color_material():
    mat_name = MATERIAL_NAME
    material_created = False

    # check whether the material already exists
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

    base_color = _find_socket(principled.inputs, "Base Color")
    surface = _find_socket(output.inputs, "Surface")

    if base_color is not None:
        links.new(attrib.outputs["Color"], base_color)
    if surface is not None:
        links.new(principled.outputs["BSDF"], surface)

    return mat, material_created
