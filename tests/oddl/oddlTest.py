import unittest
from unittest import TestCase
from .oddl import (
    DataArrayList,
    DataList,
    DataType, 
    Identifier, 
    NumericLiteral, 
    Reference, 
    StringLiteral, 
    parse_as_stream, 
    Properties, 
    Children, 
    ParseContext, 
    Structure, 
    Name, 
    NULL
)
from . import oddl
from .examples import (
    METRIC_STRUCTS, 
    GEOMETRY_STRUCT, 
    GEOMETRY_OBJECT_STRUCT, 
    REFERENCE_1, 
    VERT_ARRAY_POS,
    VERT_ARRAY_NORMAL,
    VERT_ARRAY_TEXCOORD,
    INDEX_ARRAY,
    FIND_BY_REF
)
import re

def data_list_contents(s) -> list[list[NumericLiteral]]:
    pattern = r"\{([^}]+)\}"
    matches = re.findall(pattern, s)
    tuples = [[NumericLiteral(elem.strip()) for elem in match.split(',')] for match in matches]
    return tuples


class ParserTest(TestCase):
    def test_parse_identifier(self):
        ctx = ParseContext('foobar')
        name = oddl.parse_identifier_str(ctx)
        self.assertEqual(name, 'foobar')

        ctx = ParseContext('foobar{}')
        name = oddl.parse_identifier_str(ctx)
        self.assertEqual(name, 'foobar')
        self.assertEqual(ctx.current_char(), '{')

    def test_parse_comment(self):
        ctx = ParseContext("""// the comment
                           bar""")
        comment = oddl.parse_comment(ctx)
        self.assertEqual(comment, 'the comment')

        ctx = ParseContext("""/* a b c * d */ X Y Z""")
        comment = oddl.parse_comment(ctx)
        self.assertEqual(comment, 'a b c * d ')

    def test_parse_string(self):
        ctx = ParseContext('"foo bar baz"')
        s = oddl.parse_string(ctx)
        self.assertTrue(isinstance(s, oddl.StringLiteral))
        self.assertEqual(s.value, "foo bar baz")

        ctx = ParseContext("\"foo bar\\\" baz\"")
        s = oddl.parse_string(ctx)
        self.assertTrue(isinstance(s, oddl.StringLiteral))
        self.assertEqual(s.value, 'foo bar\\" baz')


class OGEXTests(TestCase):
    maxDiff = None
    
    def test_parse_metric_structs(self):
        ctx = ParseContext(METRIC_STRUCTS)
        nodes = list(parse_as_stream(ctx))
        self.assertEqual(len(nodes), 12)

        children = nodes[2]
        self.assertEqual(len(children.content), 2)
        self.assertEqual(list(map(lambda n: type(n), children.content)), [DataType, Children])

        expected = [
            Structure.from_identifier(
                identifier=Identifier('Metric'), 
                properties=Properties(props=[(Identifier(name="key"), StringLiteral("distance"))]),
                content=Children([
                    Structure(data_type=DataType("float"), content=DataList([NumericLiteral("1")]))])
                ),
            Structure.from_identifier(
                identifier=Identifier('Metric'), 
                properties=Properties(props=[(Identifier(name="key"), StringLiteral("angle"))]),
                content=Children(content=[
                    Structure(data_type=DataType("float"), content=DataList([NumericLiteral("1")]))
                ])),
            Structure.from_identifier(
                identifier=Identifier('Metric'), 
                properties=Properties(props=[(Identifier(name="key"), StringLiteral("time"))]),
                content=Children(content=[
                    Structure(data_type=DataType("float"), content=DataList([NumericLiteral("1")]))
                ])),
            Structure.from_identifier(
                identifier=Identifier('Metric'), 
                properties=Properties(props=[(Identifier(name="key"), StringLiteral("up"))]),
                content=Children(content=[
                    Structure(data_type=DataType("string"), content=DataList([StringLiteral("z")]))
                ]))]
      
        self.assertEqual(oddl.parse_stream(nodes), expected)


    def test_parse_as_stream_geometry_struct(self):
        ctx = ParseContext(GEOMETRY_STRUCT)
        nodes = list(parse_as_stream(ctx))
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0], Identifier(name="GeometryNode"))
        self.assertEqual(nodes[1], Name("node1", scope="global"))


    def test_parse_as_stream_geometry_object_struct(self):
        ctx = ParseContext(GEOMETRY_OBJECT_STRUCT)
        nodes = list(parse_as_stream(ctx))
        types = list(map(lambda n: type(n), nodes))
        self.assertEqual(types, [Identifier, Name, Children])


    def test_parse_stream_geometry_struct(self):
        ctx = ParseContext(GEOMETRY_STRUCT)
        nodes = list(parse_as_stream(ctx))
        parsed = oddl.parse_stream(nodes)
        self.assertEqual(len(parsed), 1)


    def test_parse_stream_geometry_object(self):
        ctx = ParseContext(GEOMETRY_OBJECT_STRUCT)
        nodes = list(parse_as_stream(ctx))
        parsed = oddl.parse_stream(nodes)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].identifier.name, 'GeometryObject') 

        position_data_list = DataArrayList(list=[
            Children(content=vert) for vert in data_list_contents(VERT_ARRAY_POS)
        ], array_size=3)

        normal_data_list = DataArrayList(list=[
            Children(content=vert) for vert in data_list_contents(VERT_ARRAY_NORMAL)
        ], array_size=3)

        texcoord_data_list = DataArrayList(list=[
            Children(content=vert) for vert in data_list_contents(VERT_ARRAY_TEXCOORD)
        ], array_size=2)

        index_data_list = DataArrayList(list=[
            Children(content=vert) for vert in data_list_contents(INDEX_ARRAY)
        ], array_size=3)

        position_vert_array = Structure.from_identifier(
            identifier=Identifier('VertexArray'),
            properties=Properties(props=[
                (Identifier(name="attrib"), StringLiteral("position")),
            ]),
            content=Children([
                Structure.from_data_type(DataType("float", element_size=3),
                content=position_data_list)
            ])
        )

        normal_vert_array = Structure.from_identifier(
            identifier=Identifier('VertexArray'),
            properties=Properties(props=[
                (Identifier(name="attrib"), StringLiteral("normal")),
            ]),
            content=Children([
                Structure.from_data_type(DataType("float", element_size=3),
                content=normal_data_list)
            ])
        )

        texcoord_vert_array = Structure.from_identifier(
            identifier=Identifier('VertexArray'),
            properties=Properties(props=[
                (Identifier(name="attrib"), StringLiteral("texcoord")),
            ]),
            content=Children([
                Structure.from_data_type(DataType("float", element_size=2),
                content=texcoord_data_list)
            ])
        )

        index_array = Structure.from_identifier(
            identifier=Identifier('IndexArray'),
            content=Children([
                Structure.from_data_type(DataType("uint32", element_size=3),
                content=index_data_list)
            ])
        )

        mesh_node = Structure.from_identifier(
            identifier=Identifier('Mesh'),
            properties=Properties(props=[
                (Identifier(name="primitive"), StringLiteral("triangles"))
            ]),
            content=Children([
                position_vert_array, 
                normal_vert_array,
                texcoord_vert_array,
                index_array
                ])
        )

        expected = Structure.from_identifier(
            identifier=Identifier('GeometryObject'),
            name=Name('geometry1', 'global'),
            content=Children([mesh_node])
        )
        self.assertEqual(parsed[0], expected)
    
    def test_parse_reference_1(self):
        ctx = ParseContext(REFERENCE_1)
        nodes = list(parse_as_stream(ctx))
        parsed = oddl.parse_stream(nodes)
        self.assertEqual(len(parsed), 2)

        expected = [
            Structure.from_identifier(Identifier("SomeNode"), properties=Properties(props=[
                (Identifier(name="prop1"), Reference([Name("ref1", 'global')])),
                (Identifier(name="prop2"), Reference([Name("ref2", 'local'), Name("someRef", 'local')])),
            ]),
            content=Children([])),
            Structure.from_identifier(Identifier("SomeNode"), properties=Properties(props=[
                (Identifier(name="prop"), NULL)
            ]),
            content=Children([]))
        ]

        self.assertEqual(parsed, expected)

    def test_find_by_ref(self):
        ctx = ParseContext(FIND_BY_REF)
        nodes = list(parse_as_stream(ctx))
        parsed = oddl.parse_stream(nodes)[0]

        found = oddl.find_by_ref(parsed, Reference([
            Name("node1", 'global'), 
            Name("node2", 'global'), 
            Name("bar1", 'local')
        ]))
        
        self.assertEqual(found.name, Name("bar1", 'local'))



        
        


        