from collections import defaultdict

from numpy import int8, int16, int32, uint8, uint16, uint32, uint64
from can_headers import drive_hardware_type, parameter_dictionary, trace_variables


def hex_string_to_bytes(input_string):
    """
    Take an input string of arbitrary length (assuming the first two characters
     are a full byte, i,e,, 22222 and 222202 produce the same result, to a
     reversed list of bytes, i.e., "221c0" -> [1, 28, 34]
    :param input_string:
    :return: list
    """
    out_bytes = []
    for i in range(0, len(input_string), 2):
        out_bytes.append(int(input_string[i:i+2], 16))
    return out_bytes


def bytes_to_string(input_bytes):
    if isinstance(input_bytes, int):
        raise ValueError("input_bytes not list or array: ", input_bytes)
    return "".join([chr(i) for i in input_bytes if i != 0])


def int_to_bit_list(input_int):
    if input_int is None:
        return [0 for i in range(16)]
    status_formatted = [int(i) for i in "{0:016b}".format(input_int)]
    status_formatted.reverse()
    return status_formatted


def int_to_hexes(input_int, width=None):
    if width == 4:
        input_int = uint32(input_int)
    _hex = hex(input_int)[2:].replace("L", "")
    out_hex = []
    for i in range(0, len(_hex), 2):
        out_hex.insert(0, int(_hex[i:i+2], 16))
    if width is not None:
        for i in range(len(out_hex), width, 1):
            out_hex.append(0)
    return out_hex


def test_int_to_hexes():
    data1 = int_to_hexes(30000, width=4)
    assert 0x75 == data1[1]
    assert 0x30 == data1[0]
    data2 = int_to_hexes(40863, width=4)
    assert 0x9F == data2[0]
    assert 0x9F == data2[1]


def int48(input_int):
    return input_int


def lookup_trace_variable_address(input_name):
    return int(trace_variables[input_name]["address"])


def lookup_trace_variable_units(input_name):
    try:
        return float(trace_variables[input_name]["units"].split(" ")[0])
    except Exception as e:
        return 1.0


def lookup_trace_variable_unit_name(input_name):
    try:
        return unit_getter(trace_variables[input_name]["units"].split(" "))
    except Exception as e:
        return "Unknown"


def unit_getter(parts):
    return parts[0] if len(parts) == 1 else " ".join(parts[1:])


def get_trace_variables():
    return trace_variables.keys()


def lookup_hardware_type(input_int):
    address = "%0.4X" % input_int
    return str(drive_hardware_type[address]["name"])


def read_in_data(_data):
    if not isinstance(_data, list):
        return _data
    _out_data = []
    for i in range(0, len(_data)-1, 4):
        _data_point = 0
        for byte_i in range(4):
            _data_point += _data[i+byte_i] << 8*byte_i
        _out_data.append(_data_point)
    return _out_data


def properties_from_cfg():
    maps = {"INT8": int8, "INT16": int16, "INT32": int32, "INT32*": int32,
            "String": bytes_to_string,
            "STRING": bytes_to_string, "U8": uint8, "U16": uint16,
            "U32": uint32, "U64": uint64, "HARDWARE_TYPE": lookup_hardware_type,
            "OCTET": read_in_data}

    width_dict = {"INT8": 1, "INT16": 2, "INT32": 4, "INT32*": 4, "String": 40,
                  "STRING": 40, "HARDWARE_TYPE": 4, "OCTET": 40,
                  "U8": 1, "U16": 2, "U32": 4, "U64": 8}

    out_dictionary = {}
    for section in parameter_dictionary.keys():
        _parameter_name = parameter_dictionary[section]["parametername"]
        _type = parameter_dictionary[section]["datatype"]
        out_dictionary[_parameter_name] = {}
        _add_bytes = hex_string_to_bytes(section)
        if len(_add_bytes) == 2:
            _add_bytes.append(0)

        out_dictionary[_parameter_name]["index"] = _add_bytes
        out_dictionary[_parameter_name]["width"] = width_dict[_type]
        out_dictionary[_parameter_name]["type"] = maps[_type]
        try:
            _units = parameter_dictionary[section]["units"].split(" ")
            out_dictionary[_parameter_name]["units"] = unit_getter(_units)
            try:
                out_dictionary[_parameter_name]["scale"] = float(_units[0])
            except:
                out_dictionary[_parameter_name]["scale"] = 1.0
        except:
            out_dictionary[_parameter_name]["units"] = "Unknown"
        try:
            _map_pdo = parameter_dictionary[section]["map_pdo"]
            out_dictionary[_parameter_name]["pdo"] = _map_pdo
        except:
            out_dictionary[_parameter_name]["pdo"] = True
        try:
            _plotable = parameter_dictionary[section]["plotable"]
            out_dictionary[_parameter_name]["plot"] = _plotable
        except:
            out_dictionary[_parameter_name]["plot"] = False
    return out_dictionary


PROPERTIES = properties_from_cfg()


def address_list_to_string(address_list):
    return "".join(['{:02d}'.format(address_list[i]) if i < len(address_list) - 1 
                    else '{:01d}'.format(address_list[i]) 
                    for i in range(len(address_list))])


def generate_index_map(properties):
    """
    Generate a dict mapping addresses to property names. This is used to map
     incoming data back to properties from SDO's.
    :param properties: dict of dicts
    :return: dict mapping addresses to property names
    """
    out_dict = {}
    for _property in properties.keys():
        address = properties[_property]['index']
        out_dict[address_list_to_string(address)] = _property
    return out_dict


def convert_numpy_points(data_points):
    out_dict = defaultdict(list)
    # removes numpy datatypes from data
    for i in range(len(data_points)):
        for key in data_points[i].keys():
            # purely for typing reduction
            dp = data_points[i][key]
            out_dict[key].append(dp if type(dp) == str or type(
                dp) == bool else float(dp))
    return out_dict

