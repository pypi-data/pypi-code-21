import psycopg2
import re
import json

_v_matcher = re.compile(r'(.+)\[(\d+)\.(\d+)\](.+)')
_e_matcher = re.compile(r'(.+)\[(\d+)\.(\d+)\]\[(\d+)\.(\d+),(\d+)\.(\d+)\](.*)')
_e_array_matcher = re.compile(r'([a-zA-Z_]+\[[0-9.]*\]\[[0-9,.]*\]{[w]*})')

def vertex_parser(value, cur=None):

    if value is None:
        return None
    try:
        match = _v_matcher.match(value)
        if not match:
            return {}

        result = {}
        result["label"] = match.group(1)
        result["vid"] = "{}.{}".format(match.group(2), match.group(3))
        result.update(json.loads(match.group(4)))

        return result

    except Exception as e:
        return psycopg2.InterfaceError("Bad vertex representation: {}".format(value))


def edge_parser(value, cur=None):

    if value is None:
        return None
    try:
        match = _e_matcher.match(value)
        if not match:
            return {}

        result = {}

        result["label"] = match.group(1)
        result["eid"] = "{}.{}".format(match.group(2), match.group(3))
        result["source_vid"] = "{}.{}".format(match.group(4), match.group(5))
        result["destination_vid"] = "{}.{}".format(match.group(6), match.group(7))
        result.update(json.loads(match.group(8)))

        return result
    except Exception as e:
        return psycopg2.InterfaceError("Bad edge representation: {}".format(value), e)


def path_parser(value, cur=None):

    def _tokenize(value_to_tokenize):
        i = 0
        s = 0
        depth = 0
        in_gid = False
        character_list = []
        clean_value = value_to_tokenize[1:-1]  # remove '[' and ']'
        for char in clean_value:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            elif depth == 0 and char == '[':  # for GID
                in_gid = True
            elif in_gid and char == ']':
                in_gid = False
            elif depth == 0 and not in_gid and  char == ',':
                character_list.append(clean_value[s:i])
                s = i + 1
            if depth < 0:
                raise ValueError
            i += 1
        character_list.append(clean_value[s:i])
        return character_list

    if value is None:
        return None

    try:
        objects_in_path = _tokenize(value)
        if not objects_in_path:
            return {}

        result = {}

        result["vertices"] = map(vertex_parser, objects_in_path[0::2])
        result["edges"] = map(edge_parser, objects_in_path[1::2])

        return result

    except Exception as e:
        return psycopg2.InterfaceError("Bad path representation: {}".format(value), e)


def edge_array_parser(value, cur):

    if value is None:
        return None

    try:
        edge_array_string = _e_array_matcher.findall(value[1:-1])
        edge_array = map(edge_parser, edge_array_string)

        return [a for a in edge_array]

    except Exception as e:
        return psycopg2.InterfaceError("Bad path representation: {}".format(value), e)


"""
To implement:
7001	_graphid
7002	graphid
7011	_vertex
7012	vertex --> single vertex
7021	_edge --> array of edges
7022	edge --> single edge
7031	_graphpath
7032	graphpath
7051	_edgeref
7052	edgeref
18764   ag_vertex
18777   ag_edge
"""


VERTEX = psycopg2.extensions.new_type((7012,), "VERTEX", vertex_parser)
psycopg2.extensions.register_type(VERTEX)

EDGE = psycopg2.extensions.new_type((7022,), "EDGE", edge_parser)
psycopg2.extensions.register_type(EDGE)

EDGE_ARRAY = psycopg2.extensions.new_type((7021,), "EDGE_ARRAY", edge_array_parser)
psycopg2.extensions.register_type(EDGE_ARRAY)

PATH = psycopg2.extensions.new_type((7032,), "PATH", path_parser)
psycopg2.extensions.register_type(PATH)

connect = psycopg2.connect
