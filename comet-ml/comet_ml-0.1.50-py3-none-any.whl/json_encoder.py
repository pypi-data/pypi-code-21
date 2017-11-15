import json



class NestedEncoder(json.JSONEncoder):
    '''
    A JSON Encoder that converts floats/decimals to strings and allows nested objects
    '''

    def default(self, obj):

        if isinstance(obj, float) or obj.__class__.__name__ == "float32":
            return self.floattostr(obj)
        elif obj.__class__.__name__ == "type":
            return str(obj)
        elif hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)

    def floattostr(self,o,_inf=float('Inf'), _neginf=-float('-Inf'),nan_str="None"):
        if o != o:
            text = nan_str
        elif o == _inf:
            text = 'Infinity'
        elif o == _neginf:
            text = '-Infinity'
        else:
            return o.__repr__()

        return text
