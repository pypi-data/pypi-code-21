from rest_framework import serializers
import json

class JSONField(serializers.Field):
    def to_representation(self, value):
        if value is None:
            response = None
        else:
            response = json.dumps(value)
        return response

    def to_internal_value(self, data):
        if data is None or isinstance(data, dict):
            response = data
        else:
            response = json.loads(data)
        return response
