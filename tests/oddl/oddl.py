# This module is supposed to be an aid in testing outputs of Blender-OpenGEX exporter.
# Having a complete Open DDL or OpenGEX parser implementation is not the aim,
# so I took a number of shortcuts, e.g. when parsing strings, escape chars are not handled, 
# you get the raw string in a StringLiteral. Similarly for numbers, you get a NumericLiteral
# containing the raw string.

from dataclasses import dataclass
from typing import Iterable, Optional
import io


data_types = set([
    'bool', 'b',
    'int8', 'i8',
    'int16', 'i16',
    'int32', 'i32',
    'int64', 'i64',
    'uint8', 'u8',
    'uint16', 'u16',
    'uint32', 'u32',
    'uint64', 'u64',
    'half', 'h', 'float16', 'f16',
    'float', 'f', 'float32', 'f32',
    'double', 'd', 'float64', 'f64',
    'string', 's',
    'ref', 'r',
    'type', 't',
    'base64', 'z'
    ])

class Marker:
    pass


@dataclass
class Name(Marker):
    name: str
    scope: str


@dataclass
class Identifier(Marker):
    name: str


@dataclass
class DataType:
    name: str
    element_size: Optional[int] = None
    asterisk: Optional[bool] = False


@dataclass
class StringLiteral(Marker):
    value: str


@dataclass
class NumericLiteral(Marker):
    value: str


@dataclass
class ElementSize(Marker):
    size: int


@dataclass 
class Properties(Marker):
    props: list[tuple[Identifier, any]]


@dataclass
class Children(Marker):
    content: list

    def __len__(self):
        return len(self.content)
    
    def __iter__(self):
        return iter(self.content)

@dataclass
class DataList(Marker):
    list: list

    def __len__(self):
        return len(self.list)
    
    def __iter__(self):
        return iter(self.list)

@dataclass
class DataArrayList(Marker):
    list: list
    array_size: int

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        return iter(self.list)

@dataclass
class Reference(Marker):
    refs: list[Name]


@dataclass
class Structure:
    data_type: Optional[DataType] = None
    identifier: Optional[Identifier] = None
    name: Optional[Name] = None
    properties: Optional[Properties] = None
    content: Optional[Children | DataArrayList | DataList] = None

    @staticmethod
    def from_identifier(identifier: Identifier, **kwargs):
        return Structure(identifier=identifier, data_type=None, **kwargs)
    
    @staticmethod
    def from_data_type(data_type: DataType, **kwargs):
        return Structure(data_type=data_type, identifier=None, **kwargs)
        

@dataclass
class CharacterLiteral(Marker):
    char: str


@dataclass
class NullLiteral(Marker):
    pass


@dataclass
class BooleanLiteral(Marker):
    value: bool

    @staticmethod
    def from_value(value: bool):
        if value:
            return BOOLEAN_TRUE
        else:
            return BOOLEAN_FALSE


NULL = NullLiteral()
BOOLEAN_TRUE = BooleanLiteral(True)
BOOLEAN_FALSE = BooleanLiteral(False)

CHARACTER_LITERALS = {
    '*': CharacterLiteral('*'),
}


@dataclass
class ParseContext:
    input: str
    position: int = 0

    def advance_position(self, by: int=1):
        self.position = self.position + by
    
    def current_char(self):
        if self.position < len(self.input):
            return self.input[self.position]
        return None


def skip_whitespace(ctx: ParseContext):
    c = ctx.current_char()
    while c and c.strip() == "":
        ctx.advance_position()
        c = ctx.current_char()
    return

def read_until(ctx: ParseContext, cs: set[str]) -> str:
    chars = []
    c = ctx.current_char()
    while c is not None and c not in cs:
        chars.append(c)
        ctx.advance_position()
        c = ctx.current_char()
    return ''.join(chars)

def parse_identifier_str(ctx: ParseContext):
    c = ctx.current_char()
    if not c.isalpha(): raise Exception(f"expected alpha character, got '{c}'")
    name = []
    while c and (c.isalnum() or c == '_'):
        name.append(c)
        ctx.advance_position()
        c = ctx.current_char()
    return ''.join(name)

def parse_string(ctx: ParseContext):
    """We're parsing the strings as they are, we're not interpreting escaped characters.
    
    After successfully parsing the string, position points to first char after 
    the closing double quote."""
    c = ctx.current_char()
    if c != '"': raise Exception(f"Expected start of string literal, got '{c}'")

    ctx.advance_position()
    c = ctx.current_char()
    text = io.StringIO()
    while c is not None:
        text.write(read_until(ctx, set(['"', '\\'])))
        c = ctx.current_char()
        if c == '\\':
            text.write(c)
            ctx.advance_position()
            c = ctx.current_char()
            if c == None:
                raise Exception("Unexpected end of text")
            else:
                text.write(c)
                ctx.advance_position()
        else: # end of string
            ctx.advance_position()
            break

    value = text.getvalue()
    text.close()
    return StringLiteral(value)

def parse_numeric_str(ctx: ParseContext) -> str:
    c = ctx.current_char()
    if not c.isnumeric(): raise Exception(f"expected numeric character, got '{c}'")
    txt = read_until(ctx, set([',', '\t', ' ', '\n', '\r', ']', ')', '}']))
    return txt

def parse_signed_numeric_str(ctx: ParseContext) -> NumericLiteral:
    c = ctx.current_char()
    sign = ''
    if c in ['+', '-']:
        sign = c
        ctx.advance_position()
    return NumericLiteral(sign + parse_numeric_str(ctx))


def parse_name(ctx: ParseContext):
    scope = None
    c = ctx.current_char()
    if c == '$':
        scope = 'global'
    elif c == '%':
        scope = 'local'
    ctx.advance_position()
    return Name(parse_identifier_str(ctx), scope)


def parse_reference(ctx: ParseContext) -> Reference:
    refs = []
    c = ctx.current_char()
    while c == '%' or c == '$':
        refs.append(parse_name(ctx))
        skip_whitespace(ctx)
        c = ctx.current_char()
    return Reference(refs)

def parse_properties(ctx: ParseContext) -> Properties:
    c = ctx.current_char()
    if c != '(': raise Exception(f"expected a property list starting with '(', but got '{c}'")
    ctx.advance_position()
    c = ctx.current_char()
    properties = []
    while c != ')':
        skip_whitespace(ctx)
        ident_txt = parse_identifier_str(ctx)
        skip_whitespace(ctx)
        c = ctx.current_char()
        if c  == ')' or c == ',':
            properties.append((Identifier(ident_txt), True))
            if c == ',': ctx.advance_position()
            else: break
        elif c == '=':
            ctx.advance_position()
            skip_whitespace(ctx)
            c = ctx.current_char()
            if c == '"':
                str = parse_string(ctx)
                properties.append((Identifier(ident_txt), str))
            elif c in ['+', '-']:
                properties.append((Identifier(ident_txt), parse_signed_numeric_str(ctx)))
            elif c.isnumeric():
                str = parse_numeric_str(ctx)
                properties.append((Identifier(ident_txt), NumericLiteral(str)))
            elif c == '%' or c == '$':
                properties.append((Identifier(ident_txt), parse_reference(ctx)))
            elif c.isalpha():
                val_str = parse_identifier_str(ctx)
                if val_str == 'null':
                    properties.append((Identifier(ident_txt), NULL))
                elif val_str in ['true', 'false']:
                    properties.append((Identifier(ident_txt), BooleanLiteral.from_value(val_str == 'true')))
                elif val_str in data_types:
                    properties.append((Identifier(ident_txt), DataType(val_str)))
                else:
                    properties.append((Identifier(ident_txt), Identifier(val_str)))
            else:
                raise Exception(f"expected a property value, got '{c}'")
        c = ctx.current_char()
        if c == ',':
            ctx.advance_position()
            c = ctx.current_char()

    ctx.advance_position()
    return Properties(properties)


def parse_comment(ctx: ParseContext):
    c = ctx.current_char()
    if c != '/': raise Exception(f"Expected a '/' char, got '{c}'")
    ctx.advance_position()
    c = ctx.current_char()
    comment = ''
    if c == '/':
        ctx.advance_position()
        skip_whitespace(ctx)
        comment = read_until(ctx, set(['\n']))
    elif c == '*':
        ctx.advance_position()
        skip_whitespace(ctx)
        comment = read_until(ctx, set(['*']))
        comment = comment + '*'
        ctx.advance_position()
        c = ctx.current_char()
        while c is not None and c != '/':
            comment = comment + read_until(ctx, set(['*']))
            ctx.advance_position()
            c = ctx.current_char()
    return comment


def parse_as_stream(ctx: ParseContext) -> Iterable:
    skip_whitespace(ctx)
    c = ctx.current_char()
    
    while c is not None:
        if c.isalpha():
            txt = parse_identifier_str(ctx)
            if txt in data_types:
                yield DataType(txt)
            else:
                yield Identifier(txt)
        elif c in ['%', '$']:
            name = parse_name(ctx)
            yield name
        elif c == '(': # properties
            props = parse_properties(ctx)
            yield props
        elif c == '{':
            ctx.advance_position()
            content = list(parse_as_stream(ctx))
            yield Children(content)
        elif c == '}':
            ctx.advance_position()
            return
        elif c == '[':
            ctx.advance_position()
            skip_whitespace(ctx)
            txt = parse_numeric_str(ctx)
            skip_whitespace(ctx)
            c = ctx.current_char()
            if c != ']': raise Exception(f"expected ']', got '{c}'")
            ctx.advance_position()
            yield ElementSize(int(txt))
        elif c == '"':
            yield parse_string(ctx)
        elif c in ['+', '-']:
            yield parse_signed_numeric_str(ctx)
        elif c.isnumeric():
            txt = parse_numeric_str(ctx)
            yield NumericLiteral(txt)
        elif c == '/':
            parse_comment(ctx)
        elif c == '*':
            yield CHARACTER_LITERALS['*']
        elif c == ',':
            ctx.advance_position()
        else:
            raise Exception(f"Unexpected character '{c}' at position {ctx.position}, context: <<{ctx.input[ctx.position-10:ctx.position+10]}>>")
        skip_whitespace(ctx)
        c = ctx.current_char()


def _max_len(patterns) -> int:
    return max([len(p) for p,l in patterns])        


def match_pattern(patterns, items):
    result = None
    elems_taken = 0

    prefix = items[1:_max_len(patterns)]       
    prefix_t = list(map(type, prefix))
    for pattern, ctor in patterns:
        if prefix_t[:len(pattern)] == pattern:
            result = ctor(prefix)
            elems_taken = 1 + len(pattern)
            break
    return (elems_taken, result)       


def parse_dt_struct(items):
    data_type = items[0]
    patterns = [
        ([Children], lambda prefix: Structure(data_type, content=prefix[0])),
        ([Name, Children], lambda prefix: Structure(data_type=data_type, name=prefix[0], content=prefix[1])),
        ([ElementSize, Children], lambda prefix: Structure(data_type=DataType(data_type.name, prefix[0].size), content=prefix[1])),
        ([ElementSize, Name, Children], lambda prefix: Structure(data_type=DataType(data_type.name, prefix[0].size), name=prefix[1], content=prefix[2])),
        ([ElementSize, CharacterLiteral, Children], lambda prefix: Structure(data_type=DataType(data_type.name, prefix[0].size, prefix[1] == CHARACTER_LITERALS['*']), content=prefix[2])),
        ([ElementSize, CharacterLiteral, Name, Children], lambda prefix: Structure(data_type=DataType(data_type.name, prefix[0].size, prefix[1] == CHARACTER_LITERALS['*']), name=prefix[2], content=prefix[3])),
    ]

    (elems_taken, result) = match_pattern(patterns, items)
    if result is not None:
        if result.data_type.element_size is not None:
            array_content = [DataList(children.content) for children in result.content.content]
            result.content = DataArrayList(array_content, result.data_type.element_size)
        else:
            result.content = DataList(result.content.content)
    return (elems_taken, result)

def parse_identifier_struct(items):
    identifier = items[0]
    patterns = [
        ([Children], lambda prefix: Structure(identifier=identifier, content=prefix[0])),
        ([Name, Children], lambda prefix: Structure(identifier=identifier, name=prefix[0], content=prefix[1])),
        ([Properties, Children], lambda prefix: Structure(identifier=identifier, properties=prefix[0], content=prefix[1])),
        ([Name, Properties, Children], lambda prefix: Structure(identifier=identifier, name=prefix[0], properties=prefix[1], content=prefix[2]))
    ]

    (elems_taken, result) = match_pattern(patterns, items)
    if result is not None:
        result.content = Children(parse_stream(result.content.content))
    return (elems_taken, result)

def parse_struct(items):
    if len(items) == 0: return (0, None)

    first_elem = items[0]
    if isinstance(first_elem, DataType):
        return parse_dt_struct(items)
    elif isinstance(first_elem, Identifier):
        return parse_identifier_struct(items)
    
def parse_stream(items) -> list[Structure]:
    result = []
    remaining = items
    while len(remaining) > 0:
        (taken, parsed) = parse_struct(remaining)
        if parsed is None and len(remaining) - taken > 0:
            raise Exception(f"Failed to parse a struct after consuming {len(result)} structs")
        result.append(parsed)
        remaining = remaining[taken:]
    
    return result


def find_by_name(struct: Structure | Children, name: Name) -> Structure | None:
    if struct.name == name:
        return struct
    elif isinstance(struct.content, Children):
        for child in struct.content:
            found = child if child.name == name else None
            if found is not None:
                return found
    return None


def find_by_ref(struct: Structure, ref: Reference) -> Structure | None:
    current = struct
    for index, ref_elem in enumerate(ref.refs):
        found = find_by_name(current, ref_elem)
        if found is None:
            return None
        elif index == len(ref.refs) - 1:
            return found
        else:
            current = found
