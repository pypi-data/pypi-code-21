import json

from django import forms
from jsonschema import ValidationError

from .validators import JSONSchemaValidator


class JSONSchemaField(forms.CharField):
    def __init__(self, schema, **kwargs):
        self.schema = schema
        super(JSONSchemaField, self).__init__(**kwargs)
        self.validators.append(JSONSchemaValidator(self.schema))

    def to_python(self, value):
        try:
            value = json.loads(value)
        except ValueError as error:
            raise ValidationError(str(error))
        return value
