from django.contrib.postgres.fields import JSONField

from django_jsonschema.validators import JSONSchemaValidator


class JSONSchemaField(JSONField):
    def __init__(self, schema='', **kwargs):
        self.schema = schema
        super(JSONSchemaField, self).__init__(**kwargs)
        self.validators.append(JSONSchemaValidator(self.schema))

    def from_db_value(self, value, expression, connection, context):
        if value is not None:
            self.run_validators(value)
        return value

    def get_prep_value(self, value):
        if value is not None:
            self.run_validators(value)
        return super(JSONSchemaField, self).get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in {
            'iexact', 'contains', 'icontains',
            'startswith', 'istartswith', 'endswith', 'iendswith',
            'isnull', 'search', 'regex', 'iregex',
            'has_key', 'has_keys', 'has_any_keys'
        }:
            return value

        if isinstance(value, (dict, list)):
            return Json(value)

        if hasattr(value, '_prepare'):
            return value._prepare()

        get_prep_value = super(JSONSchemaField, self).get_prep_value
        if lookup_type in ('exact', 'gt', 'gte', 'lt', 'lte'):
            return get_prep_value(value)
        elif lookup_type in ('range', 'in'):
            return [get_prep_value(v) for v in value]
        return get_prep_value(value)
