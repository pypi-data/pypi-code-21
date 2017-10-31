
TRUE_BOOLEAN_QUERY_VALUES = [1, "1", "True", "true", True, "t", "T"]
FALSE_BOOLEAN_QUERY_VALUES = [0, "0", "", "False", "false", False, "f", "F"]

CACHE_KEY_ESCAPE_CHARACTERS = [
    "?", "*", "[", "]", "{", "}", "&", "%", "&", "$", "@", "!", "(", ")"
    
    ]


import ast



from querystring_parser import parser as query_parser

def query_params_to_dict(query_string =None):
    if query_string == None:
        return None
    
    if type(query_string) == dict:
        return query_string
    
    params = query_string_to_dict(query_string = query_string)
    params = format_django_lookups(params)
    
    return params

def query_string_to_dict(query_string=None):
    if not isinstance(query_string, basestring):
        raise TypeError("Requires a basestring to parse into dict")

    response = query_parser.parse(query_string)
    _recursively_convert_query(current_dict=response, level=0)
    return response


MAX_QUERY_RECURSION_DEPTH = 4  # shouldn't go deeper then that


def _recursively_convert_query(current_dict, level):
    for k, v in current_dict.iteritems():
        if isinstance(v, dict):
            if level == MAX_QUERY_RECURSION_DEPTH:
                raise ValueError("Your query parameters are nested too deeply.")
            else:
                _recursively_convert_query(v, level+1)
        elif isinstance(v, basestring) and all([bracket in v for bracket in ["[", "]"]]):
            current_dict[k] = ast.literal_eval(v)
            
            
            
def format_django_lookups(query_params):
    django_boolean_lookups = ["isnull"]
    if isinstance(query_params, dict):
        for k, v in query_params.iteritems():
            if isinstance(v, dict):
                for param in v.keys():
                    if any([lookup in param for lookup in django_boolean_lookups]):
                        if v[param] in TRUE_BOOLEAN_QUERY_VALUES:
                            v[param] = True
                        elif v[param] in FALSE_BOOLEAN_QUERY_VALUES:
                            v[param] = False
                        else:
                            raise ValueError("Incorrectly formatted boolean query")

    return query_params