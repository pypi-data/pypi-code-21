import json

from django.db import models

from .validators import JSONSchemaValidator


class JSONSchemaField(models.TextField):
    def __init__(self, schema='', **kwargs):
        self.schema = schema
        super(JSONSchemaField, self).__init__(**kwargs)
        self.validators.append(JSONSchemaValidator(self.schema))

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return
        value = json.loads(value)
        self.run_validators(value)
        return value

    def get_prep_value(self, value):
        if value is None:
            return
        self.run_validators(value)
        return json.dumps(value)
