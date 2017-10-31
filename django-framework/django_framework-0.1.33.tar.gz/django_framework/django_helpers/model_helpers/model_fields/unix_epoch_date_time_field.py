import datetime
from django.db import models
import arrow

class UnixEpochDateTimeField(models.DateTimeField):

    def to_python(self, value):
        if value is None:
            value = value
        elif isinstance(value, datetime.datetime):
            value = value.replace(microsecond=0)
        else:
            if isinstance(value, basestring):
                value = int(value)
            value = arrow.get(value).replace(microsecond=0).datetime

        response = super(UnixEpochDateTimeField, self).to_python(value)
        return response

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            value = self.to_python(value)
            setattr(model_instance, self.attname, value)
        value = super(UnixEpochDateTimeField, self).pre_save(model_instance, add)
        if value:
            value = value.replace(microsecond=0)
            setattr(model_instance, self.attname, value)
        return value

    def get_prep_value(self, value):
        if value:
            value = self.to_python(value)
        response = super(UnixEpochDateTimeField, self).get_prep_value(value)
        return response

    def get_prep_lookup(self, lookup_type, value):
        if isinstance(value, list):
            response = [self.get_prep_value(v) for v in value]
        else:
            response = self.get_prep_value(value)

        response = super(UnixEpochDateTimeField, self).get_prep_lookup(lookup_type, value)
        return response

    @classmethod
    def value_to_string(cls, obj):
        if obj is None:
            obj = obj
        elif isinstance(obj, datetime.datetime):
            obj = obj
        else:
            if isinstance(obj, basestring):
                obj = int(obj)
            obj = arrow.get(obj).datetime
        response = str(obj)
        return response
