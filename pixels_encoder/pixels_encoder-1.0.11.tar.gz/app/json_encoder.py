import json
import re


class Frozen(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class PrettyJSONEncoder(json.JSONEncoder):
    frozen_format = '_frozen: {}_'
    obj_value_pattern = re.compile(frozen_format.format(r'(.+)'))

    def default(self, obj):
        if not isinstance(obj, Frozen):
            return super(PrettyJSONEncoder, self).default(obj)
        return self.frozen_format.format(repr(obj))

    def iterencode(self, obj, **kwargs):
        for encoded in super(PrettyJSONEncoder, self).iterencode(obj, **kwargs):
            # check for list and tuple value that was wrapped into Froze instance
            match = self.obj_value_pattern.search(encoded)
            yield encoded if not match else match.group(1)
