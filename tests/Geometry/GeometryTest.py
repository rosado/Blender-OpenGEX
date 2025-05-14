import bpy
import os
import unittest
import pathlib
import tests.oddl.oddl as oddl
from tests.oddl.oddl import (
    Structure, 
    Name, 
    Identifier, 
    Properties, 
    StringLiteral,
    NumericLiteral, 
    DataType, 
    DataList, 
    DataArrayList, 
    Children, 
)
from tests.oddl.oddlTest import dump_for_comparison

from tests import TestUtils

__author__ = 'Jonathan Hale'


def struct_metric(key: str, value: NumericLiteral | StringLiteral):
    typ = "float" if isinstance(value, NumericLiteral) else "string"
    return Structure.from_identifier(
        Identifier("Metric"), 
        properties=Properties([(Identifier("key"), StringLiteral(key))]),
        content=Children([
            Structure.from_data_type(data_type=DataType(typ), 
                                     content=DataList([value]))]))

transform = [1.0, 0.0, 0.0, 0.0,
             0.0, 1.0, 0.0, 0.0,
             0.0, 0.0, 1.0, 0.0,
             0.0, 0.0, 0.0, 1.0]

geometry_node = Structure.from_identifier(
            Identifier("GeometryNode"),
            name=Name("node1", scope="global"),
            content=Children([
                Structure.from_identifier(Identifier("Name"),
                                          content=Children([Structure(data_type=DataType("string"), content=DataList([StringLiteral("Suzanne")]))])),
                Structure.from_identifier(Identifier("ObjectRef"),
                                          content=Children([Structure(data_type=DataType("ref"), content=DataList([Name("geometry1", "global")]))])),
                Structure.from_identifier(Identifier("Transform"),
                                          content=Children([Structure(data_type=DataType("float", element_size=16), 
                                                                      content=DataArrayList([DataList([NumericLiteral(str(n)) for n in transform])], 
                                                                                            array_size=len(transform)))]))
]))



class GeometryTest(TestUtils.OgexExporterTest):
    # TODO(rosado): more thorough verification of output needed (see below)
    # - we need to be able to export the texture
    # - decide on how to handle subdiv modifier

    output_file_name = "output-suzanne-4.4.ogex"
    base_dir = TestUtils.OgexExporterTest.base_dir_for(__file__)
    
    def test_suzanne_export(self):
        gex_file = self.file_path(self.output_file_name)
        
        bpy.ops.wm.open_mainfile(filepath=str(self.file_path("suzanne-4.4.blend")))
        bpy.ops.export_scene.ogex(filepath=str(gex_file), rounding=3)

        exported = self.parse_ogex_file(gex_file)
        
        metric_structs = [
            struct_metric("distance", NumericLiteral("1.0")),
            struct_metric("angle", NumericLiteral("1.0")),
            struct_metric("time", NumericLiteral("1.0")),
            struct_metric("up", StringLiteral("z")),
        ]
        self.assertEqual(exported[:4], metric_structs)

        self.assertEqual(geometry_node, exported[4])
        
        geometry_object = exported[5]
        self.assertEqual(geometry_object.identifier, Identifier("GeometryObject"))
        self.assertEqual(geometry_object.name, Name("geometry1", scope="global"))
        mesh: Structure = geometry_object.content.content[0]
        self.assertEqual(mesh.identifier, Identifier("Mesh"))
        self.assertEqual(mesh.properties, Properties([(Identifier("primitive"), StringLiteral("triangles"))]))

        mesh_children = mesh.content.content
        va_position, va_normal, va_texcoord, index_array = mesh_children

        self.assertEqual(va_position.properties, Properties([(Identifier("attrib"), StringLiteral("position"))]))
        array_position: DataArrayList = va_position.content.content[0].content
        self.assertEqual(type(array_position), DataArrayList)
        self.assertEqual(array_position.array_size, 3)
        self.assertEqual(len(array_position.list), 2874)
        
        self.assertEqual(va_normal.properties, Properties([(Identifier("attrib"), StringLiteral("normal"))]))
        self.assertEqual(va_texcoord.properties, Properties([(Identifier("attrib"), StringLiteral("texcoord"))]))


if __name__ == '__main__':
    unittest.main()
