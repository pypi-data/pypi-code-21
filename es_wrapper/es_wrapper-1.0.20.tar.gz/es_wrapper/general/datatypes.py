import inspect
import json
import re
import types
from itertools import chain

from jsonschema import validate, ValidationError

from six import string_types

def check_if_input_is_class(in_obj):
    """
    This method returns true if the input object is a class, else false
    :param Object in_obj: A object to check
    :return bool: is object a class
    """
    if not (isinstance(in_obj, types.ObjectType) or
            isinstance(in_obj, types.ClassType) or
            isinstance(in_obj, types.InstanceType)):
        return False
    return True


def class_name(class_to_check):
    """
    Returns the name of the input object only if its a class
    :param class_to_check: The type of variable we verify is a class
    :return str:
    """
    if check_if_input_is_class(class_to_check):
        try:
            return class_to_check.__class__.__name__
        except AttributeError:
            # An exception if raised if we are given the name of the class and not an instance.
            return class_to_check.__name__
    else:
        return "Bad Class Type"


def func_name():
    """
    This method returns the name of the current function we are using
    :return:
    """
    return inspect.stack()[1][3]


def compare_different_types(val_a, val_b):
    """
    Comparing two values of unknown type with type conversion
    :param val_a: Value of unknown type
    :param val_b: Value of unknown type
    :return bool: Comparison of the values
    """
    try:
        val_a = convert_data_types(val_a)
        val_b = convert_data_types(val_b)
        return val_a == val_b
    except TypeError:
        return False


def convert_data_types(data):
    """
    This method converts strings or unicode to their true type
    :param data: Data of unknown type
    :return: Data in the correct type
    """
    return format_data_recursively(data, convert_to_correct_type)


def convert_data_for_es(data):
    """
    Returns converted string as fitted for ES
    :param data: Data of unknown type
    :return: Data in the correct type for ES
    """
    return format_data_recursively(data, convert_to_correct_type, convert_strings_for_es)


def print_all_dict_keys(data):
    """
    Returns converted string as fitted for ES
    :param data: Data of unknown type
    :return: Data in the correct type for ES
    """
    return format_data_recursively(data, convert_to_correct_type, print_key)


def print_key(data):
    if type(data) == str or type(data) == unicode:
        print(data)


def format_data_recursively(data, *funcs):
    """
    This method formats all the values for a given dictionary, list of other type
    :param data:
    :param funcs: A list of functions to perform in the input data
    :return data:
    """
    try:
        # We call convert_data_for_es recursively to make sure all fields are set
        if type(data) == dict:
            data = dict((format_data_recursively(k, *funcs), format_data_recursively(data[k], *funcs)) for k in data)
        elif type(data) == list:
            data = [format_data_recursively(x, *funcs) for x in data]
        else:
            # Convert all data types as needed
            for func in funcs:
                data = func(data)

        return data

    except ValueError:
        return ""


def convert_to_correct_type(data):
    """
    Takes a string and returns in the correct type, int, float or string

    :param string data: input string to check
    :return string: the converted string

    :raise ValueError: We accept only non list or dict
    """
    if type(data) == list or type(data) == dict:
        raise ValueError("Incorrect type received %s" % type(data))
    # Make sure the received text string is valid
    if data:
        # no need to convert
        if type(data) == int or type(data) == float:
            return data
        # First try returning an integer
        try:
            return int(data)
        except ValueError:
            pass
        # On failure try returning a float
        try:
            return float(data)
        except ValueError:
            pass
    # We don't want to have None types going around so we return an empty string
    elif data is None:
        return ""
    return data


def es_aggregations_to_dict(es_dict, query_func):
    """
    Converts an ES aggregation to a serial: object dict
    :param dictionary es_dict:
    :param <function> query_func:
    :return:
    """
    output_dict = {}
    # Go over the list of outlier serial number, get objects from ES and create a dictionary
    for item_dict in es_dict:
        try:
            item_id = item_dict['key']
            item = query_func(item_id)
            output_dict[item_id] = item
        except KeyError:
            pass
    return output_dict


def convert_strings_for_es(data):
    """
    Used tp remove unnecessary ES chars which can't be visualized in Kibana
    :param data:
    :return : A string of the data itself
    """

    if type(data) == str or type(data) == unicode:
        chars_to_remove = [':', '-', '*']
        regex = '[' + re.escape(''.join(chars_to_remove)) + ']'
        return re.sub(regex, '_', data)
    else:
        return data


def extract_value(dictionary, *args):
    """
    This method extracts a value from a dictionary or a list with nested key values
    :param dict dictionary: A dictionary to extract value from
    :param args: list of keys
    """
    val = dictionary
    try:
        for arg in args:
            val = val[arg]
        return val
    except KeyError:
        return ""
    except IndexError:
        return ""


def build_nested_mapping_dictionary(index_dict, key_list):
    """
    key_list = [["key1", "nested_key1"], ["key2]]
    :param index_dict:
    :param key_list:
    :return:
    """
    for path in key_list:
        current_level = index_dict
        for part in path:
            if part not in current_level:
                current_level[part] = {"properties": {}}
            current_level = current_level[part]["properties"]

    return index_dict


def merge_dicts(d1, d2):
    """
    update first dict with second recursively
    :param dict d1: Dictionary to merge
    :param dict d2: Dictionary to merge
    """
    if type(d1) == dict:
        for k, v in d1.items():
            if k in d2:
                d2[k] = merge_dicts(v, d2[k])
        d1.update(d2)
    return d1


def merge_multiple_dictionaries(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.

    :param dict_args: unlimited number of input dictionaries
    :return dict result: A merge of all input dictionaries.
    """
    result = {}
    for d in dict_args:
        result = merge_dicts(result, d)
    return result


def extract_dictionary(input_dict, key_set):
    """
    The function will return a subset dictionary containing only the values for key_set

    :param dictionary input_dict: the dictionary to go over
    :param dictionary key_set: can be either a dictionary or a list of keys to strip from the input dictionary
    :return dictionary: A dictionary with the necessary values
    """
    # Make sure that the keys we'll search through the dictionary are a list
    if type(key_set) == dict:
        keys = key_set.keys()
    elif type(key_set) == list:
        keys = key_set
    else:
        raise ValueError("Wrong input key_set type %s" % type(key_set))

    return dict((k, input_dict[k]) for k in keys)


def multi_getattr(obj, attr, default=None):
    """
    Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.
    :param Object obj: The object to extract attributes from
    :param string attr:
    :param default:
    """
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default:
                return default
            else:
                raise
    return obj


class Serializable:
    """
    A serializable class giving object an ability to convert themselves to JSON
    """
    _message_mapper = {}
    _schema = {}

    def __init__(self):
        pass

    def is_valid(self, *args, **kwargs):
        """
        Returns a boolean if the object can be converted to a correct message by the JSON schema
        :param args: Optional values for schema validation
        :param kwargs: Optional values for schema validation
        :return bool: Schema Status
        """
        return self._validate_schema(*args, **kwargs)

    def _validate_schema(self, *args, **kwargs):
        """
        Returns a boolean if the object can be converted to a correct message by the JSON schema
        :param args: Optional values for schema validation
        :param kwargs: Optional values for schema validation
        :return bool: Schema Status
        """
        if not self._schema:
            raise ValueError("No JSON Scheme has been defined for %s" % class_name(self))
        try:
            validate(self.to_message(*args, **kwargs), self._schema)
            return True
        except ValidationError:
            return False

    def to_message(self, *args, **kwargs):
        # A message to be overridden - by default returning the members of the class
        return self.to_dict()

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def from_dict(self, values_dict):
        """
        Populate the object from a dictionary - On Key error just leave things as they are
        :param dictionary values_dict: A dictionary to load a neighbor
        :raises TypeError: When adding a non existing value
        """
        for name, value in values_dict.iteritems():
            # if name not in self.__dict__.keys():
            #     raise TypeError(("Trying to add a non existing key: %s " % name))
            # setattr(self, name, self._wrap(value))
            # Non recursive
            # Add only known members
            if name in self.__dict__.keys():
                setattr(self, name, value)

    def to_dict(self):
        """
        Returns a dictionary of all recursive members of the object
        If you wanted just the self dictionary, use return self.__dict__
        :return:
        """
        return json.loads(self.to_JSON())

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Serializable().from_dict(value) if isinstance(value, dict) else value

    def from_message(self, in_dict):
        """
        This method updated the object from a message coming from the client
        :param dict in_dict: Input dictionary to load neighborAP from
        :return:
        """
        if not self._message_mapper:
            raise ValueError("No Message mapper has been defined for %s" % class_name(self))

        # Update the neighbor object from a message dictionary
        for key, value in in_dict.items():
            try:
                attr_name = self._message_mapper[key]
                if hasattr(self, attr_name):
                    setattr(self, attr_name, value)
            except KeyError:
                pass


def percentage_checker(val_a, val_b, percentage=80, a_bigger_then_b=True):
    """
    This method checks if val_a is larger or smaller than a percentage of val_b
    :param int val_a:
    :param int val_b:
    :param int percentage: What should be the percentage of val_b in val_a
    :param bool a_bigger_then_b: Direction of the formula
    :return float:
    """
    try:
        val_b_percentage = float(val_b*percentage)/float(100)
        # return True if the percentage from A is bigger
        if a_bigger_then_b:
            return float(val_a) >= float(val_b_percentage)
        else:
            return float(val_a) <= float(val_b_percentage)

    except ValueError:
        return False


def str2bool(v):
    """
    Converts a string into a boolean
    :param v:
    :return bool:
    """
    if isinstance(v, string_types):
        return v.lower() in ("yes", "true", "t", "1")
    else:
        return v


def parse_range(rng):
    parts = rng.split('-')
    if 1 > len(parts) > 2:
        raise ValueError("Bad range: '%s'" % (rng,))
    parts = [int(i) for i in parts]
    start = parts[0]
    end = start if len(parts) == 1 else parts[1]
    if start > end:
        end, start = start, end
    return range(start, end + 1)


def parse_range_list(ranges):
    """
    Parse a string list as "0,1,2,3"
    :param str ranges:
    :return list:
    """
    return sorted(set(chain(*[parse_range(rng) for rng in ranges.split(',')])))


def sort_dict_by_key(dictionary):

    sorted_keys = dictionary.keys()
    sorted_keys.sort()

    return dict((key, dictionary[key]) for key in sorted_keys)

def unicode_conversion(data):

    if type(data) == str or type(data) == str :
        return data.encode("utf-8")

    return data


def convert_to_unicode(data):
    """
    This method converts strings or unicode to their true type
    :param data: Data of unknown type
    :return: Data in the correct type
    """
    return format_data_recursively(data, convert_to_correct_type, unicode_conversion)

def convert_keyword_data(data):
    """
    Returns converted string as fitted for ES
    :param data: Data of unknown type
    :return: Data in the correct type for ES
    """
    return format_data_recursively(data, convert_to_correct_type, remove_bad_chars)


def is_str(term):
    """
    This method checks if the input param is a string
    :param term:
    :return boolean:
    """
    if type(term) == str or type(term) == unicode:
        return True
    else:
        return False


BAD_CHARS = """,%"""


def remove_bad_chars(term):
    """
    The method formats a string and removes all bad query chars
    :param term:
    :return:
    """
    if not is_str(term):
        term = str(term)
    # Remove bad chars
    if type(term) == str:
        term = term.translate(None, BAD_CHARS)
    # For unicode
    else:
        term = term.translate(dict.fromkeys(map(ord, BAD_CHARS)))

    return term