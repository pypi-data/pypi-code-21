from django.core.exceptions import ValidationError
from jsonschema import validate, ValidationError as JSONSchemaValidationError


class JSONSchemaValidator(object):
    code = 'invalid'

    def __init__(self, schema):
        self.schema = schema

    def __call__(self, value):
        try:
            validate(value, self.schema)
        except JSONSchemaValidationError as e:
            raise ValidationError(
                '%s: %s' % ('.'.join(e.path), e.message), code=self.code,)
        else:
            return value

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and self.schema == other.schema
        )
