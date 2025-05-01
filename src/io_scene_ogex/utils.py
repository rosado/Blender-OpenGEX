import bpy

# LOG_FILE = "C:/Users/XXX/Downloads/BLENDER_GEX.log"


# def log_to_file(text: str, filename: str = LOG_FILE) -> None:
#     with open(filename, "a") as file:
#         file.write(text)
#         file.write("\n")


def uv_map_attributes(mesh: bpy.types.Mesh) -> list[bpy.types.Float2Attribute]:
    uv_attrs = []
    if mesh and mesh.id_type == 'MESH':
        for attribute in mesh.attributes:
            if attribute.domain == 'CORNER' and attribute.data_type == 'FLOAT2':
                uv_attrs.append(attribute)
    return uv_attrs

def uv_map_attributes_via_uv_layers(mesh: bpy.types.Mesh) ->list[bpy.types.Float2Attribute]:
    uv_attrs = []
    for uv_layer in mesh.uv_layers:
        attribute = mesh.attributes[uv_layer.name]
        if attribute.domain == 'CORNER' and attribute.data_type == 'FLOAT2':
            uv_attrs.append(attribute)
    return uv_attrs

def uv_map_coords(mesh: bpy.types.Mesh, uv_attribute) -> list[(int, any)]:
    uv_coords = []
    for loop_index, uv in enumerate(uv_attribute.data):
        vertex_index = mesh.loops[loop_index].vertex_index
        uv_coords.append((vertex_index, uv.vector))
    return uv_coords
