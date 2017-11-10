from __future__ import absolute_import

import json

from schematics import Model


def get_schematics_model_fields(model, include=None, exclude=None):
    exclude = exclude or ()

    model_fields = model._fields
    if include is None:
        result = model_fields.copy()
        for field_name in exclude:
            result.pop(field_name, None)
    else:
        result = {field_name: model_fields[field_name] for field_name
                  in include if field_name not in exclude}

    return result


class CustomModel(Model):

    def __init__(self, *args, **kwargs):
        super(CustomModel, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.to_primitive())

    @classmethod
    def from_json(cls, source, **kwargs):
        return cls(json.loads(source), **kwargs)

    def to_json(self, **kwargs):
        return json.dumps(self.to_primitive(**kwargs), ensure_ascii=False)
