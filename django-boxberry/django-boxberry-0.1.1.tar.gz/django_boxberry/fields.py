import json

from django.contrib.postgres.fields import JSONField


class JSONFieldCustom(JSONField):

    def from_db_value(self, value, expression, connection, context):
        return json.loads(value)
