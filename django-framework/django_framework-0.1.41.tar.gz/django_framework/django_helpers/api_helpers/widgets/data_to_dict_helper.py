import ast
from django.http import QueryDict
 
def querydict_to_dict(query_dict=None):
    if not isinstance(query_dict, QueryDict):
        raise TypeError("'query_dict' must be a django QueryDict to use this method")
 
    response = {}
    for k, v in dict(query_dict).iteritems():
        if isinstance(v, list):
            v = v[0]
        if "[" in v and "]" in v:
            v = ast.literal_eval(v)
 
        response[k] = v
    return response