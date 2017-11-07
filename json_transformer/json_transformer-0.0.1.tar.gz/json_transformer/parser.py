class JsonTransformer(object):

    _keep_undeclared_methods = False
    _new_json = dict()

    def __getattr__(self, attr, *args, **kwargs):
        if self._keep_undeclared_methods:
            return lambda x: (x, )
        else:
            return None

    def __init__(self, **fields):

        self._new_json = dict(
            tuple([field] + list(getattr(self, field)(value)))[-2:]
            for field, value in fields.items()
            if getattr(self, field)
        )


def print_object(json, space='    '):
    obj_str = 'class FieldMixin(object):\n\n'
    for method in json:
        obj_str += '{}@staticmethod\n'.format(space)
        obj_str += '{s}def {method}(value, dict_key=\'{method}\'):\n'.format(s=space, method=method)
        obj_str += '{s}{s}return dict_key, value\n\n'.format(s=space)

    print(obj_str)

